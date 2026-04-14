"""
RCA Pipeline: LSTM Anomaly Detection → Rule-Based Classification → LLM RCA.

Orchestrates the full pipeline from raw sensor data to root cause analysis.
"""

import os
import json
import pandas as pd
import numpy as np
import joblib

from tensorflow.keras.models import load_model

from rule_engine import (
    THRESHOLDS,
    TAG_MAP,
    PARAM_TO_TAG,
    UNITS,
    apply_rule_based,
    match_scenario,
    get_all_rules,
    get_non_normal_rules,
)


# ── LSTM Anomaly Detection ─────────────────────────────────────────

def load_lstm_artifacts(model_path: str, scaler_path: str):
    """Load trained LSTM model and scaler."""
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler


def load_data(csv_path: str, start: str = None, end: str = None,
              tz: str = "Asia/Makassar") -> pd.DataFrame:
    """Load and prepare historical data."""
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.set_index("datetime").sort_index()
    df = df[~df.index.isna()]
    df = df[~df.index.duplicated()]
    if df.index.tz is None:
        df.index = df.index.tz_localize(tz)
    if start and end:
        df = df.loc[start:end]
    return df


def make_sequences(X: np.ndarray, step: int) -> np.ndarray:
    """Convert 2D array into 3D sequences for LSTM input."""
    return np.array([X[i:i + step] for i in range(len(X) - step)])


def run_lstm_detection(
    df: pd.DataFrame,
    model,
    scaler,
    time_steps: int = 90,
    batch_size: int = 2048,
    th_phase1: float = 0.2,
    th_phase2: float = 4.0,
    phase2_start: str = "2025-08-15",
    smoothing_window: int = 12,
) -> pd.DataFrame:
    """
    Run LSTM autoencoder anomaly detection.

    Returns DataFrame indexed by timestamp with columns:
      - MAE, status, threshold_ratio, exceed_percent
      - All sensor values (inverse-scaled from last timestep)
      - Contribution and deviation per parameter
    """
    features = df.columns.tolist()
    X_scaled = scaler.transform(df)
    X_seq = make_sequences(X_scaled, time_steps)

    # Predict in batches
    preds = []
    for i in range(0, len(X_seq), batch_size):
        preds.append(model.predict(X_seq[i:i + batch_size], verbose=0))
    X_pred = np.concatenate(preds)

    # MAE per sample
    mae = np.mean(np.abs(X_pred - X_seq), axis=(1, 2))
    mae_smooth = pd.Series(mae).rolling(smoothing_window, min_periods=1).mean()

    dates = df.index[time_steps:]
    res = pd.DataFrame(index=dates)
    res["MAE"] = mae_smooth.values

    # Phase-based thresholding
    if df.index.tz is not None:
        phase2_ts = pd.Timestamp(phase2_start).tz_localize(df.index.tz)
    else:
        phase2_ts = pd.Timestamp(phase2_start)

    res["status"] = np.where(
        res.index < phase2_ts,
        np.where(res["MAE"] >= th_phase1, "ANOMALY", "NORMAL"),
        np.where(res["MAE"] >= th_phase2, "ANOMALY", "NORMAL"),
    )

    res["threshold_ratio"] = np.where(
        res.index < phase2_ts,
        (res["MAE"] / th_phase1) * 100,
        (res["MAE"] / th_phase2) * 100,
    )
    res["exceed_percent"] = res["threshold_ratio"] - 100

    # Inverse-scale real and predicted values (last timestep)
    real = scaler.inverse_transform(X_seq[:, -1, :])
    pred = scaler.inverse_transform(X_pred[:, -1, :])

    for i, col in enumerate(features):
        res[col] = real[:, i]
        res[f"dev_{col}"] = real[:, i] - pred[:, i]

    # Contribution
    abs_error = np.abs(real - pred)
    total_error = np.sum(abs_error, axis=1)
    for i, col in enumerate(features):
        res[f"contrib_{col}"] = (abs_error[:, i] / (total_error + 1e-9)) * 100

    # Production loss
    flow_col = "Flow_Rate"
    if flow_col in features:
        idx = features.index(flow_col)
        lpo = np.maximum(0, pred[:, idx] - real[:, idx])
        res["Production_Loss_MMSCFD"] = np.where(res["status"] == "ANOMALY", lpo, 0.0)
        res["Gas_Loss_MMSCF"] = res["Production_Loss_MMSCFD"] * (3 / 1440)
    else:
        res["Production_Loss_MMSCFD"] = 0.0
        res["Gas_Loss_MMSCF"] = 0.0

    return res


# ── Full Pipeline ──────────────────────────────────────────────────

def run_pipeline(
    csv_path: str,
    model_path: str,
    scaler_path: str,
    data_start: str = "2025-01-01",
    data_end: str = "2025-12-31",
    time_steps: int = 90,
    th_phase1: float = 0.2,
    th_phase2: float = 4.0,
    phase2_start: str = "2025-08-15",
) -> tuple:
    """
    Execute full pipeline:
      1. Load data
      2. Run LSTM anomaly detection
      3. Apply rule-based classification
      4. Filter anomalies and match scenarios

    Returns:
      - anomalies: DataFrame of anomaly rows with rule-based labels
      - all_results: Full DataFrame with all rows
      - features: List of feature column names
    """
    # Step 1 — Load
    print("[1/4] Loading data...")
    df = load_data(csv_path, start=data_start, end=data_end)
    features = df.columns.tolist()

    # Step 2 — LSTM
    print("[2/4] Running LSTM anomaly detection...")
    model, scaler = load_lstm_artifacts(model_path, scaler_path)
    results = run_lstm_detection(
        df, model, scaler,
        time_steps=time_steps,
        th_phase1=th_phase1,
        th_phase2=th_phase2,
        phase2_start=phase2_start,
    )

    # Step 3 — Rule-based
    print("[3/4] Applying rule-based classification...")
    results = apply_rule_based(results)

    # Step 4 — Filter anomalies + scenario matching
    print("[4/4] Filtering anomalies and matching scenarios...")
    anomalies = results[results["status"] == "ANOMALY"].copy()

    print(f"\nTotal rows: {len(results)}")
    print(f"Anomalies:  {len(anomalies)}")
    if len(anomalies) > 0:
        total_gas_loss = anomalies["Gas_Loss_MMSCF"].sum()
        print(f"Total Gas Loss: {total_gas_loss:.3f} MMSCF")

    return anomalies, results, features


# ── LLM Prompt Builder ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert industrial compressor diagnostician for a \
Booster Compressor system at an oil and gas facility. You specialize in Root \
Cause Analysis (RCA) based on real-time sensor data, anomaly detection outputs, \
and rule-based classifications.

Your task is to:
1. Analyze the sensor readings and their classifications
2. Identify the most likely root cause
3. Assess severity (LOW / MEDIUM / HIGH / CRITICAL)
4. Explain the failure mechanism
5. Recommend corrective actions
6. Estimate production impact

Respond in structured JSON format as specified in the user prompt."""


def build_rca_prompt(row: pd.Series) -> str:
    """Build a structured RCA prompt for LLM from a single anomaly row."""
    lines = [
        "## Anomaly Detected — Root Cause Analysis Request",
        "",
        f"**Timestamp**: {row.name}",
        f"**LSTM MAE Score**: {row.get('MAE', 'N/A')}",
        f"**Threshold Ratio**: {row.get('threshold_ratio', 'N/A'):.2f}%",
        f"**Exceed Percent**: {row.get('exceed_percent', 'N/A'):.2f}%",
        "",
        "### Sensor Readings & Rule-Based Classifications",
        "",
        "| Tag | Parameter | Value | Unit | Rule |",
        "|-----|-----------|-------|------|------|",
    ]

    for param, bounds in THRESHOLDS.items():
        tag = bounds["tag"]
        unit = bounds["unit"]
        value = row.get(param, "N/A")
        rule = row.get(f"{param}_rule", "UNKNOWN")
        if isinstance(value, (int, float)):
            lines.append(f"| {tag} | {param} | {value:.2f} | {unit} | **{rule}** |")
        else:
            lines.append(f"| {tag} | {param} | {value} | {unit} | **{rule}** |")

    # Deviation info
    lines += [
        "",
        "### Sensor Deviations (Actual - Predicted)",
        "",
    ]
    for param in THRESHOLDS:
        dev_col = f"dev_{param}"
        dev = row.get(dev_col, None)
        if dev is not None and isinstance(dev, (int, float)):
            lines.append(f"- **{param}**: {dev:+.4f}")

    # Contribution info
    lines += [
        "",
        "### Reconstruction Error Contribution (%)",
        "",
    ]
    for param in THRESHOLDS:
        contrib_col = f"contrib_{param}"
        contrib = row.get(contrib_col, None)
        if contrib is not None and isinstance(contrib, (int, float)):
            lines.append(f"- **{param}**: {contrib:.2f}%")

    # Scenario matches
    scenarios = match_scenario(row)
    if scenarios:
        lines += [
            "",
            "### Matched Known Scenarios",
            "",
        ]
        for s in scenarios:
            lines.append(f"- **Scenario {s['id']}**: {s['name']}")
            lines.append(f"  - Root Cause: {s['root_cause']}")
            lines.append(f"  - Severity: {s['severity']}")

    # Production loss
    lpo = row.get("Production_Loss_MMSCFD", 0)
    gas_loss = row.get("Gas_Loss_MMSCF", 0)
    lines += [
        "",
        "### Production Impact",
        "",
        f"- **Production Loss**: {lpo:.4f} MMSCFD",
        f"- **Gas Loss (3-min interval)**: {gas_loss:.6f} MMSCF",
        "",
        "### Task",
        "",
        "Based on all information above, provide your Root Cause Analysis.",
        "",
        "Respond **ONLY** in this JSON format:",
        "```json",
        "{",
        '  "root_cause": "<most likely root cause>",',
        '  "severity": "<LOW|MEDIUM|HIGH|CRITICAL>",',
        '  "confidence": <0.0-1.0>,',
        '  "failure_mechanism": "<explanation of physical process>",',
        '  "matched_scenario": <scenario_id or null>,',
        '  "corrective_actions": [',
        '    "<action 1>",',
        '    "<action 2>",',
        '    "<action 3>"',
        "  ],",
        '  "production_impact": {',
        '    "gas_loss_mmscf": <value>,',
        '    "operational_risk": "<description>"',
        "  }",
        "}",
        "```",
    ]

    return "\n".join(lines)


# ── LLM Caller ─────────────────────────────────────────────────────

def call_llm(prompt: str, api_key: str = None, model: str = None) -> str:
    """
    Call Groq API for RCA (free, OpenAI-compatible).

    Set environment variable or pass directly:
      - GROQ_API_KEY / api_key

    Free tier: 30 RPM, 14,400 RPD (Llama 3.3 70B)
    Get your key at: https://console.groq.com/keys
    """
    api_key = api_key or os.environ.get("GROQ_API_KEY")
    model = model or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        raise ValueError(
            "API key required. Set GROQ_API_KEY env var or pass api_key parameter.\n"
            "Get a free key at: https://console.groq.com/keys"
        )

    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content


def parse_rca_response(response_text: str) -> dict:
    """Parse LLM JSON response into a dict. Handles markdown code blocks."""
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_response": text, "parse_error": True}


# ── Batch RCA ──────────────────────────────────────────────────────

def run_rca_batch(anomalies: pd.DataFrame, api_key: str = None,
                  model: str = None, max_samples: int = None) -> pd.DataFrame:
    """
    Run LLM RCA on anomaly rows and append results.

    Parameters:
      - anomalies: DataFrame from run_pipeline()
      - max_samples: limit number of rows sent to LLM (None = all)

    Returns:
      - anomalies DataFrame with added RCA columns
    """
    if max_samples:
        sample = anomalies.head(max_samples)
    else:
        sample = anomalies

    rca_results = []
    for idx, row in sample.iterrows():
        prompt = build_rca_prompt(row)
        print(f"  RCA for {idx}...", end=" ")

        try:
            response = call_llm(prompt, api_key=api_key, model=model)
            parsed = parse_rca_response(response)
            rca_results.append(parsed)
            severity = parsed.get("severity", "UNKNOWN")
            root_cause = parsed.get("root_cause", "N/A")
            print(f"→ {severity}: {root_cause[:60]}...")
        except Exception as e:
            rca_results.append({"error": str(e)})
            print(f"→ ERROR: {e}")

    # Append RCA results as columns
    rca_df = pd.DataFrame(rca_results, index=sample.index)
    return anomalies.join(rca_df, how="left")


# ── Export ─────────────────────────────────────────────────────────

def export_rca_report(anomalies: pd.DataFrame, output_path: str = "RCA_Report.csv"):
    """Export anomaly data with RCA results to CSV."""
    anomalies.to_csv(output_path)
    print(f"RCA report saved to {output_path}")
