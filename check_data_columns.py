#!/usr/bin/env python3
"""Check what columns are in the test data"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "KODE_FIX" / "KODE FIX"
df = pd.read_csv(DATA_DIR / "AnomalyDetected_Test.csv", parse_dates=['datetime'])

print("Columns in test data:")
print(df.columns.tolist())
print()

# Check first anomaly
anomalies = df[df['status'] == 'ANOMALY']
if len(anomalies) > 0:
    test_row = anomalies.iloc[0]
    print("Sample anomaly row:")
    print(test_row)
    print()

    # Check for _rule columns
    rule_cols = [col for col in df.columns if col.endswith('_rule')]
    print(f"Rule columns found: {rule_cols}")
