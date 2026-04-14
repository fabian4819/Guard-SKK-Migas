# Email Alert Setup Guide

This guide explains how to configure email notifications for the i2AIMS anomaly detection system.

## Overview

The email notification system sends HTML-formatted alerts when anomalies are detected, matching the format shown in the mobile app. Each alert includes:

- Timestamp of anomaly
- Threshold ratio and exceedance percentage
- Asset integrity status
- Top contributing variables with deviations
- Visual formatting for easy reading

## Quick Start

### 1. Copy Configuration Template

```bash
cp .env.example .env
```

### 2. Configure Email Settings

Edit `.env` and fill in your email credentials:

```bash
# For Gmail (most common)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_FROM=your-email@gmail.com
ALERT_TO=recipient1@company.com,recipient2@company.com
```

### 3. Load Environment Variables

```bash
# Load .env file
export $(cat .env | xargs)
```

Or use `python-dotenv`:

```bash
pip install python-dotenv
```

Then in Python:
```python
from dotenv import load_dotenv
load_dotenv()
```

### 4. Run with Email Alerts

```bash
# Send email alerts for detected anomalies
python main.py --send-email

# Limit number of alerts sent
python main.py --send-email --max-alerts 5

# Full pipeline with LLM RCA and email alerts
python main.py --send-email --max-samples 10
```

## Email Provider Setup

### Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Configure .env**
   ```bash
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop  # App password (remove spaces)
   ```

### Outlook/Office 365 Setup

```bash
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### Custom SMTP Server

```bash
SMTP_SERVER=mail.yourcompany.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

## Testing Email Configuration

Create a test script `test_email.py`:

```python
import os
import pandas as pd
from datetime import datetime
from email_notifier import send_email_alert
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a sample anomaly row
sample_data = {
    "MAE": 5.2,
    "status": "ANOMALY",
    "threshold_ratio": 130.5,
    "exceed_percent": 30.5,
    "asset_integrity_status": "WARNING",
    "Flow_Rate": 42.5,
    "Suction_Pressure": 31.2,
    "Discharge_Pressure": 65.8,
    "Suction_Temperature": 95.3,
    "Discharge_Temperature": 198.7,
    "dev_Flow_Rate": -2.3,
    "dev_Suction_Pressure": -1.8,
    "dev_Discharge_Pressure": 2.5,
    "dev_Suction_Temperature": 3.1,
    "dev_Discharge_Temperature": 5.4,
    "contrib_Flow_Rate": 35.2,
    "contrib_Suction_Pressure": 25.1,
    "contrib_Discharge_Pressure": 20.3,
    "contrib_Suction_Temperature": 12.4,
    "contrib_Discharge_Temperature": 7.0,
}

# Create series with timestamp index
row = pd.Series(sample_data, name=datetime.now())

# Send test email
print("Sending test email...")
success = send_email_alert(row)

if success:
    print("✓ Test email sent successfully!")
else:
    print("✗ Failed to send test email. Check your configuration.")
```

Run the test:

```bash
python test_email.py
```

## Customization

### Change Equipment Name

Edit `email_notifier.py`:

```python
EQUIPMENT_NAME = "Your Equipment Name"
FIELD_NAME = "Your Field Name"
```

### Modify Email Template

The HTML template is in the `build_email_html()` function in `email_notifier.py`. You can customize:

- Colors and styling
- Number of top contributors (default: 5)
- Additional information sections
- Footer text

### Add Multiple Recipients

In `.env`:

```bash
ALERT_TO=engineer1@company.com,engineer2@company.com,manager@company.com
```

Or programmatically:

```python
from email_notifier import send_email_alert

recipients = [
    "engineer1@company.com",
    "engineer2@company.com",
    "manager@company.com"
]

send_email_alert(anomaly_row, recipients=recipients)
```

## Troubleshooting

### "Failed to send email: Authentication failed"

- **Gmail**: Make sure you're using an App Password, not your regular password
- **2FA**: If 2FA is enabled, you must use an App Password
- **Less Secure Apps**: Gmail has disabled "less secure app access" - use App Passwords

### "Failed to send email: Connection refused"

- Check SMTP server and port settings
- Verify firewall isn't blocking outbound SMTP connections
- Try using port 465 (SSL) instead of 587 (TLS)

### "No email recipients configured"

- Make sure `ALERT_TO` is set in `.env`
- Verify environment variables are loaded (`echo $ALERT_TO`)
- Check for trailing commas or spaces in email addresses

### Emails Not Arriving

- Check spam/junk folder
- Verify recipient email addresses are correct
- Check sender reputation (some providers block automated emails)
- Test with a different recipient address

## Integration with Monitoring Systems

### Scheduled Monitoring

Use cron to run periodic checks:

```bash
# Run every hour and send alerts
0 * * * * cd /path/to/skkmigas && export $(cat .env | xargs) && python main.py --send-email --max-alerts 10 >> logs/alerts.log 2>&1
```

### Real-time Monitoring

Create a monitoring service that continuously watches for anomalies:

```python
from rca_pipeline import run_pipeline
from email_notifier import send_email_alert
import time

while True:
    # Run detection
    anomalies, _, _ = run_pipeline(...)

    # Send alerts for new anomalies
    for idx, row in anomalies.iterrows():
        send_email_alert(row)

    # Wait before next check
    time.sleep(300)  # Check every 5 minutes
```

## Security Best Practices

1. **Never commit .env file**: Add `.env` to `.gitignore`
2. **Use App Passwords**: Don't use your main email password
3. **Rotate credentials**: Change passwords periodically
4. **Limit recipients**: Only send to authorized personnel
5. **Monitor usage**: Check for unusual email activity
6. **Use TLS**: Always use port 587 (STARTTLS) or 465 (SSL/TLS)

## API Reference

### `send_email_alert(row, recipients=None, equipment_name=None, ...)`

Send single anomaly alert email.

**Parameters:**
- `row` (pd.Series): Anomaly data with timestamp index
- `recipients` (List[str]): Email addresses (uses `ALERT_TO` if None)
- `equipment_name` (str): Equipment name for subject
- `smtp_server`, `smtp_port`, `username`, `password`: SMTP config

**Returns:**
- `bool`: True if sent successfully

### `send_batch_alerts(anomalies, max_alerts=None, **email_config)`

Send alerts for multiple anomalies.

**Parameters:**
- `anomalies` (pd.DataFrame): DataFrame of anomaly rows
- `max_alerts` (int): Maximum number of alerts to send
- `**email_config`: Override email settings

**Returns:**
- `dict`: Counts of sent/failed/total alerts

## Example Email Output

The email alert will look like this:

```
Subject: [i2AIMS Matindok Field] Anomaly Alert - Booster Compressor MTD-340-C1001B

[Blue Header]
[i2AIMS Matindok Field] Anomaly on Booster Compressor MTD-340-C1001B

An anomaly has been detected on process parameters related to
Booster Compressor MTD-340-C1001B. Below are the details:

Anomaly Details

• Timestamp: 2026-01-19 19:33:00
• Threshold ratio: 110.5% (Reconstruction loss exceeds threshold by 10.5%)
• Asset integrity status: N/A

Below are the details on variables that contributed the most* to anomaly
and each deviation from normal condition:

┌───────────────────────────┬────────┬──────────┬───────────┬──────────────┐
│ Variable                  │ Value  │ Expected │ Deviation │ Contribution │
├───────────────────────────┼────────┼──────────┼───────────┼──────────────┤
│ Flow_Rate (FI1001B)       │  42.50 │   44.80  │ -2.30 (-5.1%) │   40.9%   │
│ Suction_Pressure (PI1001B)│  31.20 │   33.00  │ -1.80 (-5.5%) │   37.7%   │
│ ...                       │        │          │           │              │
└───────────────────────────┴────────┴──────────┴───────────┴──────────────┘

*Contribution represents the percentage of total reconstruction error
attributed to each variable.
```

## Support

For issues or questions:
1. Check this guide first
2. Review error messages in console output
3. Test email configuration with `test_email.py`
4. Verify environment variables are loaded correctly
