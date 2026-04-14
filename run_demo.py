#!/usr/bin/env python3
"""
GUARD Demonstration Script
Generative Understanding for Anomaly Response & Detection

Runs anomaly detection + sends email alerts
Then you visualize results in dashboard
"""

import sys
from datetime import datetime
from pathlib import Path

print("="*60)
print("  GUARD Anomaly Detection Demonstration")
print("  Generative Understanding for Anomaly Response & Detection")
print("  BOOSTER COMPRESSOR B CPP DONGGI")
print("="*60)
print()

# Get date range from user
print("Select demonstration period (2025 data available):")
print()
start = input("Start date (YYYY-MM-DD) [default: 2025-08-01]: ").strip() or "2025-08-01"
end = input("End date (YYYY-MM-DD) [default: 2025-08-31]: ").strip() or "2025-08-31"
print()

# Email settings
send_email = input("Send email alerts? (y/n) [default: y]: ").strip().lower() or "y"
if send_email == 'y':
    max_alerts = input("Max email alerts to send (1-20) [default: 5]: ").strip() or "5"
    max_alerts = int(max_alerts)
else:
    max_alerts = 0

print()
print("="*60)
print(f"  Configuration")
print("="*60)
print(f"  Period: {start} to {end}")
print(f"  Email alerts: {'Enabled' if max_alerts > 0 else 'Disabled'}")
if max_alerts > 0:
    print(f"  Max alerts: {max_alerts}")
print("="*60)
print()

confirm = input("Start analysis? (y/n): ").strip().lower()
if confirm != 'y':
    print("Cancelled.")
    sys.exit(0)

print()
print("Starting analysis... This will take 30-60 seconds")
print()

# Import modules
print("[1/4] Loading modules...")
from rca_pipeline import run_pipeline
from email_notifier import send_email_alert

# Run pipeline
print("[2/4] Running LSTM anomaly detection...")
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "KODE_FIX" / "KODE FIX"

anomalies, all_results, features = run_pipeline(
    csv_path=str(DATA_DIR / "Historical_Data.csv"),
    model_path=str(DATA_DIR / "lstm_compressor_17.keras"),
    scaler_path=str(DATA_DIR / "scaler_17.pkl"),
    data_start=start,
    data_end=end,
)

print(f"✓ Analysis complete!")
print(f"  Total data points: {len(all_results):,}")
print(f"  Anomalies detected: {len(anomalies)}")
print()

# Send email alerts
if max_alerts > 0 and len(anomalies) > 0:
    print(f"[3/4] Sending email alerts (max {max_alerts})...")

    sent_count = 0
    failed_count = 0

    for idx, (timestamp, row) in enumerate(anomalies.head(max_alerts).iterrows()):
        try:
            success = send_email_alert(row)
            if success:
                sent_count += 1
                print(f"  ✓ Email sent for anomaly at {timestamp}")
            else:
                failed_count += 1
                print(f"  ✗ Failed to send email for {timestamp}")
        except Exception as e:
            failed_count += 1
            print(f"  ✗ Error sending email: {str(e)[:50]}")

    print()
    print(f"✓ Email alerts: {sent_count} sent, {failed_count} failed")
else:
    print("[3/4] Email alerts disabled")

print()

# Save results
print("[4/4] Saving results...")
output_file = "demo_results.csv"
anomalies.to_csv(output_file)

print(f"✓ Results saved to: {output_file}")
print()

# Summary
print("="*60)
print("  ANALYSIS COMPLETE")
print("="*60)
print(f"  Period: {start} to {end}")
print(f"  Anomalies: {len(anomalies)}")
if len(anomalies) > 0:
    total_gas_loss = anomalies['Gas_Loss_MMSCF'].sum()
    print(f"  Total gas loss: {total_gas_loss:.3f} MMSCF")
if max_alerts > 0:
    print(f"  Emails sent: {sent_count}")
print(f"  Results file: {output_file}")
print("="*60)
print()
print("Next step: Visualize results in dashboard")
print("Run: streamlit run dashboard_csv.py")
print()
