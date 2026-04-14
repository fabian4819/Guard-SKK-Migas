# Quick Start: Email Alerts

Get email notifications for anomalies in 5 minutes.

## Step 1: Configure Email (2 minutes)

```bash
# Copy template
cp .env.example .env

# Edit with your favorite editor
nano .env    # or vim, code, etc.
```

### For Gmail Users (most common):

```bash
# In .env file:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx    # Get from: myaccount.google.com/apppasswords
ALERT_FROM=your-email@gmail.com
ALERT_TO=recipient1@company.com,recipient2@company.com
```

**Important**: Gmail requires an App Password (not your regular password)
1. Enable 2FA: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Copy the 16-character password (remove spaces)

## Step 2: Load Configuration (30 seconds)

```bash
# Option A: Export variables
export $(cat .env | xargs)

# Option B: Install dotenv (recommended)
pip install python-dotenv
# (No export needed - automatically loads .env)
```

## Step 3: Test Email (1 minute)

```bash
python test_email.py
```

Expected output:
```
✓ Loaded .env file
✓ Configuration looks good!

Send test email? [y/N]: y

Sending...
✓ Alert email sent to: recipient@company.com
✓ TEST SUCCESSFUL!
```

**If it fails**: See troubleshooting section below

## Step 4: Run with Alerts (1 minute)

```bash
# Basic usage
python main.py --send-email

# With all features
python main.py --send-email --max-alerts 10

# Full pipeline with LLM RCA
export GROQ_API_KEY='your-groq-key'
python main.py --send-email
```

## That's It! 🎉

You'll now receive email alerts like this:

```
Subject: [i2AIMS Matindok Field] Anomaly Alert - Booster Compressor MTD-340-C1001B

[Blue Header Bar]
[i2AIMS Matindok Field] Anomaly on Booster Compressor MTD-340-C1001B

An anomaly has been detected...

Anomaly Details
• Timestamp: 2026-01-19 19:33:00
• Threshold ratio: 110.5% (Exceeds threshold by 10.5%)
• Asset integrity status: WARNING

Top Contributing Variables:
┌─────────────────────┬────────┬──────────┬───────────┬──────────────┐
│ Variable (Tag)      │ Value  │ Expected │ Deviation │ Contribution │
├─────────────────────┼────────┼──────────┼───────────┼──────────────┤
│ Flow_Rate (FI1001B) │  42.50 │   44.80  │ -2.30 (-5.1%) │   40.9%   │
└─────────────────────┴────────┴──────────┴───────────┴──────────────┘
```

---

## Troubleshooting (if test fails)

### ✗ "No email recipients configured"
```bash
# Check if ALERT_TO is set
echo $ALERT_TO

# If empty, reload .env
export $(cat .env | xargs)
```

### ✗ "Authentication failed"
**Gmail users**: Make sure you're using an App Password, NOT your regular password
- Go to: https://myaccount.google.com/apppasswords
- Generate new password
- Update SMTP_PASSWORD in .env

### ✗ "Connection refused"
**Firewall issue** - check if port 587 is blocked
```bash
# Test connection
telnet smtp.gmail.com 587
# Should connect (press Ctrl+] then quit)

# If fails, try port 465 (SSL)
# Update .env: SMTP_PORT=465
```

### ✗ Email sent but not received
1. Check spam/junk folder
2. Verify recipient email address in ALERT_TO
3. Check sender reputation (some providers block automated emails)

---

## Command Reference

```bash
# Test configuration
python test_email.py

# Run with email alerts (limit 10)
python main.py --send-email --max-alerts 10

# Run without LLM (faster)
python main.py --no-llm --send-email

# Custom date range
python main.py --send-email --start 2025-08-01 --end 2025-08-31

# Full pipeline
export GROQ_API_KEY='your-key'
python main.py --send-email --max-samples 20 --max-alerts 5
```

## Common Email Providers

### Gmail
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=app-password-16-chars
```

### Outlook/Office 365
```bash
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### Yahoo Mail
```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=app-password
```

### Custom SMTP
```bash
SMTP_SERVER=mail.yourcompany.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

---

## Need More Help?

- **Detailed setup**: See [EMAIL_SETUP.md](EMAIL_SETUP.md)
- **Full documentation**: See [README.md](README.md)
- **Gmail App Passwords**: https://myaccount.google.com/apppasswords
- **Test script**: `python test_email.py`

---

## Security Reminder

- ✓ Never commit `.env` file (already in .gitignore)
- ✓ Use App Passwords for Gmail (not regular password)
- ✓ Rotate credentials every 90 days
- ✓ Only send to authorized recipients
- ✓ Monitor for unusual email activity
