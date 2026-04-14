"""
Main entry point for Booster Compressor Anomaly Detection + Rule-Based + LLM RCA Pipeline.

Usage:
    # Run full pipeline with LLM RCA (requires OPENAI_API_KEY)
    python main.py

    # Run without LLM (rule-based + scenario matching only)
    python main.py --no-llm

    # Limit LLM calls to first N anomalies
    python main.py --max-samples 10

    # Custom data range
    python main.py --start 2025-07-01 --end 2025-09-30
"""

import argparse
import os
import sys

from rca_pipeline import (
    run_pipeline,
    build_rca_prompt,
    run_rca_batch,
    export_rca_report,
)
from rule_engine import match_scenario, get_non_normal_rules
from email_notifier import send_batch_alerts


# ── Paths (relative to KODE_FIX/KODE FIX) ──────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "KODE_FIX", "KODE FIX")

DEFAULT_CSV = os.path.join(DATA_DIR, "Historical_Data.csv")
DEFAULT_MODEL = os.path.join(DATA_DIR, "lstm_compressor_17.keras")
DEFAULT_SCALER = os.path.join(DATA_DIR, "scaler_17.pkl")


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_rule_summary(anomalies):
    """Print rule-based classification summary for anomalies."""
    print_separator("RULE-BASED CLASSIFICATION SUMMARY")

    from rule_engine import THRESHOLDS
    for param in THRESHOLDS:
        rule_col = f"{param}_rule"
        if rule_col in anomalies.columns:
            counts = anomalies[rule_col].value_counts()
            print(f"  {param}:")
            for state, count in counts.items():
                print(f"    {state}: {count}")
            print()


def print_scenario_summary(anomalies):
    """Print scenario matching summary."""
    print_separator("SCENARIO MATCHING SUMMARY")

    scenario_counts = {}
    for idx, row in anomalies.iterrows():
        matches = match_scenario(row)
        if matches:
            for m in matches:
                name = f"Scenario {m['id']}: {m['name']}"
                scenario_counts[name] = scenario_counts.get(name, 0) + 1

    if scenario_counts:
        for name, count in sorted(scenario_counts.items(), key=lambda x: -x[1]):
            print(f"  {name}: {count} occurrences")
    else:
        print("  No known scenarios matched.")
        print("  (Anomalies detected by LSTM but sensor values within rule thresholds)")
    print()


def print_sample_anomalies(anomalies, n=5):
    """Print sample anomaly details with rule-based info."""
    print_separator(f"SAMPLE ANOMALIES (showing {min(n, len(anomalies))})")

    from rule_engine import THRESHOLDS
    for idx, row in anomalies.head(n).iterrows():
        print(f"  Timestamp : {idx}")
        print(f"  MAE       : {row.get('MAE', 'N/A'):.4f}")
        print(f"  Status    : {row.get('status', 'N/A')}")

        non_normal = get_non_normal_rules(row)
        if non_normal:
            print(f"  Rules     : {non_normal}")
        else:
            print(f"  Rules     : All NORMAL")

        scenarios = match_scenario(row)
        if scenarios:
            print(f"  Scenario  : {scenarios[0]['name']} (Severity: {scenarios[0]['severity']})")
        else:
            print(f"  Scenario  : No match")

        lpo = row.get("Gas_Loss_MMSCF", 0)
        print(f"  Gas Loss  : {lpo:.6f} MMSCF")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Booster Compressor Anomaly Detection + RCA Pipeline"
    )
    parser.add_argument("--csv", default=DEFAULT_CSV, help="Path to Historical_Data.csv")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to LSTM model (.keras)")
    parser.add_argument("--scaler", default=DEFAULT_SCALER, help="Path to scaler (.pkl)")
    parser.add_argument("--start", default="2025-01-01", help="Data start date")
    parser.add_argument("--end", default="2025-12-31", help="Data end date")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM RCA, rule-based only")
    parser.add_argument("--max-samples", type=int, default=None, help="Max anomaly rows to send to LLM")
    parser.add_argument("--output", default="RCA_Report.csv", help="Output CSV path")
    parser.add_argument("--send-email", action="store_true", help="Send email alerts for anomalies")
    parser.add_argument("--max-alerts", type=int, default=10, help="Max number of email alerts to send")
    args = parser.parse_args()

    # ── Run pipeline ────────────────────────────────────────────
    print_separator("LSTM ANOMALY DETECTION + RULE-BASED PIPELINE")

    anomalies, all_results, features = run_pipeline(
        csv_path=args.csv,
        model_path=args.model,
        scaler_path=args.scaler,
        data_start=args.start,
        data_end=args.end,
    )

    if len(anomalies) == 0:
        print("\nNo anomalies detected. Exiting.")
        sys.exit(0)

    # ── Summaries ───────────────────────────────────────────────
    print_rule_summary(anomalies)
    print_scenario_summary(anomalies)
    print_sample_anomalies(anomalies, n=5)

    # ── LLM RCA (optional) ──────────────────────────────────────
    if not args.no_llm:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("=" * 60)
            print("  WARNING: GROQ_API_KEY not set.")
            print("  Get a free key at: https://console.groq.com/keys")
            print("  Then run:")
            print("    export GROQ_API_KEY='your-key-here'")
            print("  Or re-run with --no-llm for rule-based analysis only.")
            print("=" * 60)
        else:
            print_separator("LLM ROOT CAUSE ANALYSIS (Groq)")
            llm_model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
            print(f"  Model: {llm_model}")
            print(f"  Samples: {args.max_samples or 'all'}")

            anomalies = run_rca_batch(
                anomalies,
                api_key=api_key,
                model=llm_model,
                max_samples=args.max_samples,
            )

    # ── Email Alerts (optional) ─────────────────────────────────
    if args.send_email:
        print_separator("SENDING EMAIL ALERTS")
        send_batch_alerts(anomalies, max_alerts=args.max_alerts)

    # ── Export ──────────────────────────────────────────────────
    export_rca_report(anomalies, output_path=args.output)

    print_separator("PIPELINE COMPLETE")
    print(f"  Total data rows  : {len(all_results)}")
    print(f"  Anomalies found  : {len(anomalies)}")
    total_gas = anomalies["Gas_Loss_MMSCF"].sum()
    print(f"  Total Gas Loss   : {total_gas:.3f} MMSCF")
    print(f"  Report saved to  : {args.output}")


if __name__ == "__main__":
    main()
