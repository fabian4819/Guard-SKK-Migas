"""
Test script for email notification configuration.

Usage:
    # Test with environment variables
    export $(cat .env | xargs)
    python test_email.py

    # Test with python-dotenv
    pip install python-dotenv
    python test_email.py
"""

import os
import sys

# Try to load .env file FIRST (before importing email_notifier)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    print("Note: python-dotenv not installed. Using environment variables.")
    print("      Run: pip install python-dotenv")

# Now import after .env is loaded
import pandas as pd
from datetime import datetime
from email_notifier import send_email_alert


def check_config():
    """Check if email configuration is set."""
    required_vars = {
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME"),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
        "ALERT_TO": os.getenv("ALERT_TO"),
    }

    print("\n" + "="*60)
    print("  Email Configuration Check")
    print("="*60)

    all_set = True
    for var, value in required_vars.items():
        if value and value.strip():
            # Mask password
            if "PASSWORD" in var:
                display = "*" * min(len(value), 16)
            else:
                display = value
            print(f"  ✓ {var}: {display}")
        else:
            print(f"  ✗ {var}: NOT SET")
            all_set = False

    optional_vars = {
        "SMTP_SERVER": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
        "ALERT_FROM": os.getenv("ALERT_FROM", required_vars["SMTP_USERNAME"]),
    }

    print("\n  Optional (using defaults):")
    for var, value in optional_vars.items():
        print(f"    {var}: {value}")

    print("="*60 + "\n")

    return all_set


def create_sample_anomaly():
    """Create a realistic sample anomaly for testing."""
    sample_data = {
        "MAE": 5.234,
        "status": "ANOMALY",
        "threshold_ratio": 130.5,
        "exceed_percent": 30.5,
        "asset_integrity_status": "WARNING",

        # Sensor values
        "Flow_Rate": 42.5,
        "Suction_Pressure": 31.2,
        "Discharge_Pressure": 65.8,
        "Suction_Temperature": 95.3,
        "Discharge_Temperature": 198.7,

        # Deviations
        "dev_Flow_Rate": -2.3,
        "dev_Suction_Pressure": -1.8,
        "dev_Discharge_Pressure": 2.5,
        "dev_Suction_Temperature": 3.1,
        "dev_Discharge_Temperature": 5.4,

        # Contributions
        "contrib_Flow_Rate": 40.9,
        "contrib_Suction_Pressure": 37.7,
        "contrib_Discharge_Pressure": 12.8,
        "contrib_Suction_Temperature": 5.6,
        "contrib_Discharge_Temperature": 3.0,
    }

    # Create series with timestamp index
    timestamp = datetime.now()
    row = pd.Series(sample_data, name=timestamp)

    return row


def main():
    print("\n" + "="*60)
    print("  i2AIMS Email Alert - Configuration Test")
    print("="*60 + "\n")

    # Check configuration
    if not check_config():
        print("\n❌ Configuration incomplete!")
        print("\nPlease set the following environment variables:")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in your SMTP credentials")
        print("  3. Run: export $(cat .env | xargs)")
        print("\nOr see EMAIL_SETUP.md for detailed instructions.")
        sys.exit(1)

    print("✓ Configuration looks good!\n")

    # Create sample anomaly
    print("Creating sample anomaly data...")
    sample_row = create_sample_anomaly()

    print(f"\nSample Anomaly Details:")
    print(f"  Timestamp: {sample_row.name}")
    print(f"  MAE: {sample_row['MAE']:.4f}")
    print(f"  Threshold Ratio: {sample_row['threshold_ratio']:.1f}%")
    print(f"  Top Contributor: Flow_Rate ({sample_row['contrib_Flow_Rate']:.1f}%)")

    # Confirm before sending
    print("\n" + "-"*60)
    confirm = input("Send test email? [y/N]: ")

    if confirm.lower() != 'y':
        print("Test cancelled.")
        sys.exit(0)

    # Send test email
    print("\n" + "="*60)
    print("  Sending Test Email")
    print("="*60 + "\n")

    recipients = os.getenv("ALERT_TO", "").split(",")
    recipients = [r.strip() for r in recipients if r.strip()]

    print(f"Recipients: {', '.join(recipients)}")
    print(f"From: {os.getenv('ALERT_FROM', os.getenv('SMTP_USERNAME'))}")
    print(f"Server: {os.getenv('SMTP_SERVER', 'smtp.gmail.com')}:{os.getenv('SMTP_PORT', '587')}")
    print("\nSending...")

    try:
        success = send_email_alert(sample_row)

        print("\n" + "="*60)
        if success:
            print("  ✓ TEST SUCCESSFUL!")
            print("="*60)
            print("\nEmail sent successfully!")
            print(f"\nCheck your inbox at: {', '.join(recipients)}")
            print("\nNext steps:")
            print("  1. Verify email arrived (check spam folder)")
            print("  2. Check email formatting")
            print("  3. Run main pipeline: python main.py --send-email")
        else:
            print("  ✗ TEST FAILED")
            print("="*60)
            print("\nEmail failed to send. Common issues:")
            print("  • Gmail: Use App Password, not regular password")
            print("  • 2FA: Must use App Password if 2FA enabled")
            print("  • Firewall: Check if SMTP port is blocked")
            print("  • Server: Verify SMTP server and port settings")
            print("\nSee EMAIL_SETUP.md for troubleshooting guide.")

    except Exception as e:
        print("\n" + "="*60)
        print("  ✗ ERROR")
        print("="*60)
        print(f"\nException: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check EMAIL_SETUP.md for your email provider")
        print("  2. Verify SMTP credentials are correct")
        print("  3. Check firewall/network settings")
        print("  4. Try a different SMTP port (465 for SSL)")

        sys.exit(1)


if __name__ == "__main__":
    main()
