# Rule-Based Anomaly Classification & LLM-Based RCA Pipeline

## Booster Compressor Monitoring System - SKK Migas

---

## 1. Tag-to-Parameter Mapping

| Tag ID   | Parameter Name           | Unit | Type                |
|----------|--------------------------|------|---------------------|
| FI1001B  | Flow_Rate                | MMSCFD | Flow Indicator     |
| PI1001B  | Suction_Pressure         | barg | Pressure Indicator  |
| PI1004B  | Discharge_Pressure       | barg | Pressure Indicator  |
| TI1003B  | Suction_Temperature      | C    | Temperature Indicator |
| TI1004B  | Discharge_Temperature    | C    | Temperature Indicator |

---

## 2. Rule-Based Threshold Definitions

### 2.1 Flow Rate (FI1001B / Flow_Rate)

| Condition           | Threshold Range    | Classification |
|----------------------|--------------------|----------------|
| Flow > 56 MMSCFD    | value > 56         | **HIGH**       |
| Flow < 45 MMSCFD    | value < 45         | **LOW**        |
| 45 <= Flow <= 56    | 45 <= value <= 56  | **MED/NORMAL** |

### 2.2 Discharge Temperature (TI1004B / Discharge_Temperature)

| Condition                | Threshold Range     | Classification |
|--------------------------|---------------------|----------------|
| Temp > 205 C            | value > 205         | **HIGH**       |
| Temp < 189 C            | value < 189         | **LOW**        |
| 189 <= Temp <= 205      | 189 <= value <= 205 | **MED/NORMAL** |

### 2.3 Suction Temperature (TI1003B / Suction_Temperature)

| Condition                | Threshold Range     | Classification |
|--------------------------|---------------------|----------------|
| Temp > 100 C            | value > 100         | **HIGH**       |
| Temp < 90 C             | value < 90          | **LOW**        |
| 90 <= Temp <= 100       | 90 <= value <= 100  | **MED/NORMAL** |

### 2.4 Suction Pressure (PI1001B / Suction_Pressure)

| Condition                | Threshold Range      | Classification |
|--------------------------|----------------------|----------------|
| Pressure < 33 barg      | value < 33           | **LOW**        |
| Pressure > 34 barg      | value > 34           | **HIGH**       |
| 33 <= Pressure <= 34    | 33 <= value <= 34    | **MED/NORMAL** |

### 2.5 Discharge Pressure (PI1004B / Discharge_Pressure)

| Condition                | Threshold Range         | Classification |
|--------------------------|-------------------------|----------------|
| Pressure < 60 barg      | value < 60              | **LOW**        |
| Pressure > 63.3 barg    | value > 63.3            | **HIGH**       |
| 60 <= Pressure <= 63.3  | 60 <= value <= 63.3     | **MED/NORMAL** |

---

## 3. Rule-Based Classification Engine

### 3.1 Classification Logic (Python)

```python
import pandas as pd
import numpy as np


# ── Threshold definitions ──────────────────────────────────────────

THRESHOLDS = {
    "Flow_Rate": {
        "tag": "FI1001B",
        "low":  45,
        "high": 56,
    },
    "Suction_Pressure": {
        "tag": "PI1001B",
        "low":  33,
        "high": 34,
    },
    "Discharge_Pressure": {
        "tag": "PI1004B",
        "low":  60,
        "high": 63.3,
    },
    "Suction_Temperature": {
        "tag": "TI1003B",
        "low":  90,
        "high": 100,
    },
    "Discharge_Temperature": {
        "tag": "TI1004B",
        "low":  189,
        "high": 205,
    },
}


def classify_parameter(value: float, low: float, high: float) -> str:
    """Classify a single sensor reading into HIGH / LOW / NORMAL."""
    if value > high:
        return "HIGH"
    elif value < low:
        return "LOW"
    else:
        return "NORMAL"


def classify_row(row: pd.Series) -> dict:
    """Classify all parameters for a single timestep."""
    result = {}
    for param, bounds in THRESHOLDS.items():
        val = row.get(param, np.nan)
        if pd.isna(val):
            result[param] = "UNKNOWN"
        else:
            result[param] = classify_parameter(val, bounds["low"], bounds["high"])
    return result


def apply_rule_based(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply rule-based classification to every row of a DataFrame.
    Adds a column '<param>_rule' for each parameter.
    """
    for param in THRESHOLDS:
        col = f"{param}_rule"
        df[col] = df[param].apply(
            lambda v: "UNKNOWN" if pd.isna(v)
            else classify_parameter(v, THRESHOLDS[param]["low"], THRESHOLDS[param]["high"])
        )
    return df
```

### 3.2 Combining LSTM Anomaly Detection with Rule-Based Classification

```python
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model


# ── Load LSTM artifacts ────────────────────────────────────────────

MODEL_PATH  = "lstm_compressor_17.keras"
SCALER_PATH = "scaler_17.pkl"
TIME_STEPS  = 90

model  = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)


def detect_anomalies_lstm(df: pd.DataFrame, phase2_start: str = "2025-08-15",
                          th_phase1: float = 0.2, th_phase2: float = 4.0):
    """
    Run LSTM autoencoder anomaly detection.
    Returns DataFrame with status, MAE, and threshold info.
    """
    X_scaled = scaler.transform(df)

    # Build sequences
    X_seq = np.array([X_scaled[i:i+TIME_STEPS] for i in range(len(X_scaled)-TIME_STEPS)])

    # Predict
    X_pred = model.predict(X_seq, verbose=0)

    # MAE per timestep
    mae = np.mean(np.abs(X_pred - X_seq), axis=(1, 2))
    mae_smooth = pd.Series(mae).rolling(12, min_periods=1).mean()

    dates = df.index[TIME_STEPS:]
    res = pd.DataFrame(index=dates)
    res["MAE"] = mae_smooth.values

    # Phase-based thresholding
    phase2_ts = pd.Timestamp(phase2_start, tz=df.index.tz)
    res["status"] = np.where(
        res.index < phase2_ts,
        np.where(res["MAE"] >= th_phase1, "ANOMALY", "NORMAL"),
        np.where(res["MAE"] >= th_phase2, "ANOMALY", "NORMAL"),
    )

    # Inverse-scale last timestep values
    real_vals = scaler.inverse_transform(X_seq[:, -1, :])
    pred_vals = scaler.inverse_transform(X_pred[:, -1, :])

    features = df.columns.tolist()
    for i, col in enumerate(features):
        res[col] = real_vals[:, i]

    return res, features


def run_full_pipeline(df: pd.DataFrame):
    """
    Full pipeline:
      1. LSTM anomaly detection
      2. Rule-based classification on real sensor values
      3. Combine results for LLM RCA prompt
    """
    # Step 1 — LSTM anomaly detection
    res, features = detect_anomalies_lstm(df)

    # Step 2 — Rule-based classification
    res = apply_rule_based(res)

    # Step 3 — Filter anomalies only for RCA
    anomalies = res[res["status"] == "ANOMALY"].copy()

    return anomalies, features
```

---

## 4. Anomaly-to-RCA Scenario Matrix

When LSTM detects an anomaly, the rule-based classifications are combined
to determine the likely root cause scenario.

| # | Scenario | Flow_Rate | Suction_Pressure | Discharge_Pressure | Suction_Temp | Discharge_Temp | Likely Root Cause |
|---|----------|-----------|------------------|--------------------|--------------|----------------|-------------------|
| 1 | Low Flow + Low Suction P | LOW | LOW | NORMAL | NORMAL | NORMAL | Upstream supply restriction / valve issue |
| 2 | High Discharge P + High Discharge T | LOW/NORMAL | NORMAL | HIGH | NORMAL | HIGH | Discharge blockage / valve partially closed |
| 3 | High Suction T + High Discharge T | NORMAL | NORMAL | NORMAL/HIGH | HIGH | HIGH | Cooler failure / insufficient cooling |
| 4 | Low Suction P + Low Flow | LOW | LOW | LOW | NORMAL | NORMAL | Inlet filter plugging / pipeline restriction |
| 5 | High Discharge P + Low Flow | LOW | NORMAL | HIGH | NORMAL | NORMAL/HIGH | Compressor fouling / internal wear |
| 6 | All Normal but LSTM flagged | NORMAL | NORMAL | NORMAL | NORMAL | NORMAL | Sub-threshold degradation / emerging fault |
| 7 | High Flow + Low Discharge P | HIGH | NORMAL | LOW | NORMAL | NORMAL | Downstream leak / relief valve open |
| 8 | Low Suction P + High Suction T | NORMAL | LOW | NORMAL | HIGH | NORMAL | Suction separator issue / liquid carryover |

---

## 5. LLM Prompt Template for Root Cause Analysis

### 5.1 System Prompt

```
You are an expert industrial compressor diagnostician for a Booster Compressor
system at an oil and gas facility. You specialize in Root Cause Analysis (RCA)
based on real-time sensor data, anomaly detection outputs, and rule-based
classifications.

Your task is to:
1. Analyze the sensor readings and their classifications
2. Identify the most likely root cause
3. Assess severity (LOW / MEDIUM / HIGH / CRITICAL)
4. Recommend corrective actions
5. Estimate production impact
```

### 5.2 User Prompt Template

```python
def build_rca_prompt(anomaly_row: pd.Series, features: list) -> str:
    """
    Build a structured prompt for LLM-based RCA from a single anomaly row.
    """
    tag_map = {
        "Flow_Rate":               ("FI1001B", "MMSCFD"),
        "Suction_Pressure":        ("PI1001B", "barg"),
        "Discharge_Pressure":      ("PI1004B", "barg"),
        "Suction_Temperature":     ("TI1003B", "C"),
        "Discharge_Temperature":   ("TI1004B", "C"),
    }

    lines = [
        "## Anomaly Detected — Root Cause Analysis Request",
        "",
        f"**Timestamp**: {anomaly_row.name}",
        f"**LSTM MAE Score**: {anomaly_row.get('MAE', 'N/A')}",
        "",
        "### Sensor Readings & Classifications",
        "",
        "| Tag | Parameter | Value | Unit | Classification |",
        "|-----|-----------|-------|------|----------------|",
    ]

    for param in features:
        tag, unit = tag_map.get(param, (param, ""))
        value = anomaly_row.get(param, "N/A")
        rule = anomaly_row.get(f"{param}_rule", "N/A")
        lines.append(f"| {tag} | {param} | {value:.2f} | {unit} | **{rule}** |")

    lines += [
        "",
        "### Task",
        "",
        "Based on the sensor readings and their rule-based classifications above:",
        "",
        "1. **Identify the most likely root cause** of this anomaly.",
        "2. **Severity assessment**: rate as LOW / MEDIUM / HIGH / CRITICAL.",
        "3. **Explain the failure mechanism**: what physical process is causing these readings?",
        "4. **Recommend corrective actions**: what should operators do immediately?",
        "5. **Production impact**: estimate any gas loss or operational risk.",
        "",
        "Reference the scenario matrix below for common patterns:",
        "",
        "| Scenario | Symptoms | Likely Root Cause |",
        "|----------|----------|-------------------|",
        "| 1 | Low Flow + Low Suction P | Upstream supply restriction / valve issue |",
        "| 2 | Low Flow + High Discharge P + High Discharge T | Discharge blockage |",
        "| 3 | High Suction T + High Discharge T | Cooler failure |",
        "| 4 | Low Suction P + Low Flow + Low Discharge P | Inlet filter plugging |",
        "| 5 | Low Flow + High Discharge P | Compressor fouling / internal wear |",
        "| 6 | All Normal but anomaly detected | Sub-threshold degradation |",
        "| 7 | High Flow + Low Discharge P | Downstream leak / relief valve |",
        "| 8 | Low Suction P + High Suction T | Suction separator issue |",
    ]

    return "\n".join(lines)
```

---

## 6. End-to-End Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Historical_Data.csv                   │
│  (Flow_Rate, Suction_Pressure, Discharge_Pressure,      │
│   Suction_Temperature, Discharge_Temperature)           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           LSTM Autoencoder (Anomaly Detection)          │
│  ─ Model: lstm_compressor_17.keras                      │
│  ─ Scaler: scaler_17.pkl                                │
│  ─ Window: 90 timesteps                                 │
│  ─ Output: MAE score per row + ANOMALY/NORMAL label     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           Rule-Based Classification Engine               │
│  ─ Classifies each sensor as HIGH / LOW / NORMAL        │
│  ─ Uses predefined operating thresholds                 │
│  ─ Adds <param>_rule column per parameter               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           Anomaly Filtering & Enrichment                 │
│  ─ Filter rows where LSTM status = ANOMALY              │
│  ─ Attach rule-based labels to each anomaly row         │
│  ─ Calculate production loss (MMSCFD) & gas loss        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           LLM-Based Root Cause Analysis                  │
│  ─ Receives: sensor values + rule labels + MAE score    │
│  ─ Cross-references scenario matrix                     │
│  ─ Outputs: root cause, severity, corrective actions    │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Threshold Quick Reference

| Tag     | Parameter              | LOW    | NORMAL Range    | HIGH   | Unit   |
|---------|------------------------|--------|-----------------|--------|--------|
| FI1001B | Flow_Rate              | < 45   | 45 – 56         | > 56   | MMSCFD |
| PI1001B | Suction_Pressure       | < 33   | 33 – 34         | > 34   | barg   |
| PI1004B | Discharge_Pressure     | < 60   | 60 – 63.3       | > 63.3 | barg   |
| TI1003B | Suction_Temperature    | < 90   | 90 – 100        | > 100  | C      |
| TI1004B | Discharge_Temperature  | < 189  | 189 – 205       | > 205  | C      |

---

## 8. File References

| File | Description |
|------|-------------|
| `KODE_FIX/KODE FIX/AnomalyDetection_BoosterCompressor_Hackathon.ipynb` | LSTM autoencoder training notebook |
| `KODE_FIX/KODE FIX/Testing_Anomaly_Hackathon.ipynb` | LSTM inference & anomaly detection on full dataset |
| `KODE_FIX/KODE FIX/lstm_compressor_17.keras` | Trained LSTM autoencoder model |
| `KODE_FIX/KODE FIX/scaler_17.pkl` | StandardScaler fitted on training data |
| `KODE_FIX/KODE FIX/Historical_Data.csv` | Raw sensor data (5 params, 3-min intervals) |
| `KODE_FIX/KODE FIX/AnomalyDetected_Test.csv` | Anomaly detection output with all metrics |
| `RCA FOR RULE BASED - Sheet1.pdf` | RCA reference document for rule-based system |
