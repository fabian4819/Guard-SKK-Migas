#!/usr/bin/env python3
"""
Test GUARD email system with PDF attachment
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import email module
from email_notifier import send_email_alert, SYSTEM_NAME

print("=" * 60)
print("  GUARD Email System Test")
print("  Generative Understanding for Anomaly Response & Detection")
print("=" * 60)
print()

# Load test data
print("Loading test data...")
DATA_DIR = Path(__file__).parent / "KODE_FIX" / "KODE FIX"
df = pd.read_csv(DATA_DIR / "AnomalyDetected_Test.csv", parse_dates=['datetime'])
df = df.set_index('datetime')

# Find first anomaly
anomalies = df[df['status'] == 'ANOMALY']

if len(anomalies) == 0:
    print("No anomalies found in test data")
    exit(1)

print(f"Found {len(anomalies)} anomalies in dataset")
print()

# Get first anomaly
test_row = anomalies.iloc[0]
print(f"Test anomaly timestamp: {test_row.name}")
print(f"MAE: {test_row['MAE']:.4f}")

threshold_ratio = test_row.get('threshold_ratio', '0')
if isinstance(threshold_ratio, str):
    threshold_ratio = threshold_ratio.replace('%', '')
print(f"Threshold ratio: {threshold_ratio}%")
print()

# Send test email
print("Sending test email with PDF attachment...")
print()

success = send_email_alert(test_row)

if success:
    print()
    print("=" * 60)
    print("  ✅ TEST SUCCESSFUL")
    print("=" * 60)
    print()
    print("Check your email for:")
    print("  1. Updated subject line (no 'i2AIMS')")
    print("  2. GUARD branding in header")
    print("  3. Updated email text")
    print("  4. PDF attachment (RCA Report)")
    print()
else:
    print()
    print("=" * 60)
    print("  ❌ TEST FAILED")
    print("=" * 60)
    print()
