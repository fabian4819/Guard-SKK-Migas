# i2AIMS - Industrial IoT Anomaly and Integrity Monitoring System

AI-powered anomaly detection and root cause analysis system for booster compressor monitoring at the Matindok Field.

## Features

- **LSTM Autoencoder Anomaly Detection**: Deep learning model trained on historical sensor data
- **Rule-Based Classification**: Real-time sensor threshold monitoring (HIGH/LOW/NORMAL)
- **Scenario Matching**: Pattern recognition for common failure modes
- **LLM Root Cause Analysis**: AI-powered RCA using Groq (free tier available)
- **Email Alerts**: Automated HTML-formatted email notifications with detailed anomaly information
- **Production Impact Estimation**: Gas loss calculation and operational risk assessment
- **Interactive Dashboard**: Real-time monitoring and visualization with Streamlit

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install tensorflow pandas numpy scikit-learn openai python-dotenv streamlit plotly
```

Or use requirements file:

```bash
pip install -r requirements.txt
```

### 2. Launch Interactive Dashboard

```bash
# Quick launch
./run_dashboard.sh

# Or manually
streamlit run dashboard.py
```

Dashboard opens at `http://localhost:8501`

See [DASHBOARD_QUICK_START.md](DASHBOARD_QUICK_START.md) for dashboard guide.

### 3. Run Command-Line Pipeline

```bash
# Run full pipeline (without email alerts)
python3 main.py

# Run with LLM RCA (requires GROQ_API_KEY)
export GROQ_API_KEY='your-groq-api-key'
python3 main.py

# Run without LLM (rule-based only)
python3 main.py --no-llm
```

### 4. Enable Email Alerts

```bash
# Configure email settings
cp .env.example .env
# Edit .env with your SMTP credentials

# Load environment variables
export $(cat .env | xargs)

# Run with email alerts
python3 main.py --send-email

# Limit alerts sent
python3 main.py --send-email --max-alerts 5
```

See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed email configuration instructions.

## System Architecture

```
                Historical Data (CSV)
                        ↓
            [LSTM Anomaly Detection]
                        ↓
    [Rule-Based Classification] → [Scenario Matching]
                        ↓
        [LLM Root Cause Analysis] (optional)
                        ↓
            ┌───────────┴───────────┐
            ↓                       ↓
    [Email Alerts]          [Interactive Dashboard]
            ↓                       ↓
    (Email Recipients)      (Web Browser: localhost:8501)
            ↓
    [RCA Report (CSV)]
```

## Monitored Parameters

| Tag     | Parameter              | Unit    | Normal Range    |
|---------|------------------------|---------|-----------------|
| FI1001B | Flow Rate              | MMSCFD  | 45 - 56         |
| PI1001B | Suction Pressure       | barg    | 33 - 34         |
| PI1004B | Discharge Pressure     | barg    | 60 - 63.3       |
| TI1003B | Suction Temperature    | °C      | 90 - 100        |
| TI1004B | Discharge Temperature  | °C      | 189 - 205       |

## Known Failure Scenarios

The system can automatically detect and classify these common failure modes:

1. **Upstream Supply Restriction** (HIGH severity)
   - Low flow rate + Low suction pressure
   - Indicates inlet valve issue or supply restriction

2. **Discharge Blockage** (CRITICAL severity)
   - High discharge pressure + High discharge temperature
   - Requires immediate action to prevent trip

3. **Cooler Failure** (HIGH severity)
   - High suction temperature + High discharge temperature
   - Aftercooler or intercooler malfunction

4. **Inlet Filter Plugging** (MEDIUM severity)
   - Low flow + Low suction pressure + Low discharge pressure
   - Filter needs cleaning/replacement

5. **Compressor Fouling/Wear** (HIGH severity)
   - Low flow rate + High discharge pressure
   - Internal degradation requiring inspection

6. **Downstream Leak** (CRITICAL severity)
   - High flow rate + Low discharge pressure
   - Safety hazard requiring immediate isolation

7. **Suction Separator Issue** (MEDIUM severity)
   - Low suction pressure + High suction temperature
   - Liquid carryover or separator malfunction

## Command Line Options

```bash
python main.py [OPTIONS]

Required files (default paths):
  --csv      Path to Historical_Data.csv
  --model    Path to LSTM model (.keras)
  --scaler   Path to scaler (.pkl)

Data filtering:
  --start    Start date (default: 2025-01-01)
  --end      End date (default: 2025-12-31)

LLM RCA:
  --no-llm        Skip LLM analysis (rule-based only)
  --max-samples   Limit LLM calls to first N anomalies

Email alerts:
  --send-email    Enable email notifications
  --max-alerts    Maximum number of alerts to send (default: 10)

Output:
  --output        Output CSV path (default: RCA_Report.csv)
```

## Example Usage

### Run Full Pipeline

```bash
# Complete analysis with LLM RCA and email alerts
export GROQ_API_KEY='your-key'
export $(cat .env | xargs)

python main.py \
  --start 2025-07-01 \
  --end 2025-09-30 \
  --send-email \
  --max-alerts 10 \
  --output reports/July-Sept_RCA.csv
```

### Rule-Based Only (No LLM)

```bash
# Fast analysis using only rule-based classification
python main.py --no-llm --start 2025-08-01 --end 2025-08-31
```

### Email Alerts Only

```bash
# Detect anomalies and send email alerts (no LLM RCA)
python main.py --no-llm --send-email --max-alerts 5
```

## Email Alert Format

Email alerts include:

- **Header**: Equipment name and field identifier
- **Anomaly Details**:
  - Timestamp of detection
  - Threshold exceedance ratio and percentage
  - Asset integrity status
- **Variable Analysis**:
  - Top 5 contributing variables
  - Actual vs. expected values
  - Deviations with percentage change
  - Reconstruction error contribution

Example email:

```
Subject: [i2AIMS Matindok Field] Anomaly Alert - Booster Compressor MTD-340-C1001B

Anomaly Details
• Timestamp: 2026-01-19 19:33:00
• Threshold ratio: 110.5% (Exceeds threshold by 10.5%)
• Asset integrity status: WARNING

Top Contributing Variables:
┌─────────────────────┬────────┬──────────┬───────────┬──────────────┐
│ Variable (Tag)      │ Value  │ Expected │ Deviation │ Contribution │
├─────────────────────┼────────┼──────────┼───────────┼──────────────┤
│ Flow_Rate (FI1001B) │  42.50 │   44.80  │ -2.30 (-5.1%) │   40.9%   │
│ ...                 │        │          │           │              │
└─────────────────────┴────────┴──────────┴───────────┴──────────────┘
```

## Testing Email Configuration

```bash
# Test email configuration
python test_email.py
```

This will:
1. Check if email settings are configured
2. Create a sample anomaly
3. Send a test email to your configured recipients

## Configuration Files

- **`.env`**: Email and API credentials (never commit!)
- **`.env.example`**: Template for configuration
- **`KODE_FIX/KODE FIX/`**: Model artifacts and historical data
  - `Historical_Data.csv`: Sensor readings
  - `lstm_compressor_17.keras`: Trained LSTM model
  - `scaler_17.pkl`: Feature scaler

## Output

### Console Output

```
==============================================================
  LSTM ANOMALY DETECTION + RULE-BASED PIPELINE
==============================================================

[1/4] Loading data...
[2/4] Running LSTM anomaly detection...
[3/4] Applying rule-based classification...
[4/4] Filtering anomalies and matching scenarios...

Total rows: 15000
Anomalies:  245
Total Gas Loss: 12.456 MMSCF

==============================================================
  RULE-BASED CLASSIFICATION SUMMARY
==============================================================
  Flow_Rate:
    NORMAL: 180
    LOW: 65
  ...

==============================================================
  SAMPLE ANOMALIES (showing 5)
==============================================================
  Timestamp : 2025-08-15 14:23:00
  MAE       : 5.2341
  Status    : ANOMALY
  Rules     : {'Flow_Rate': 'LOW', 'Suction_Pressure': 'LOW'}
  Scenario  : Upstream Supply Restriction (Severity: HIGH)
  Gas Loss  : 0.052341 MMSCF
  ...
```

### CSV Report

File: `RCA_Report.csv`

Columns:
- Timestamp, MAE, status, threshold_ratio
- Sensor values: Flow_Rate, Suction_Pressure, etc.
- Rule classifications: Flow_Rate_rule, etc.
- Deviations: dev_Flow_Rate, etc.
- Contributions: contrib_Flow_Rate, etc.
- LLM RCA (if enabled): root_cause, severity, confidence, failure_mechanism, corrective_actions
- Production impact: Production_Loss_MMSCFD, Gas_Loss_MMSCF

## API Keys

### Groq API (for LLM RCA)

Get a free API key at: https://console.groq.com/keys

Free tier includes:
- 30 requests per minute
- 14,400 requests per day
- Access to Llama 3.3 70B model

```bash
export GROQ_API_KEY='your-key-here'
```

## File Structure

```
skkmigas/
├── main.py                      # Main pipeline entry point
├── rca_pipeline.py              # LSTM detection + LLM RCA
├── rule_engine.py               # Rule-based classification
├── email_notifier.py            # Email alert system
├── test_email.py                # Email configuration tester
├── dashboard.py                 # Interactive web dashboard
├── run_dashboard.sh             # Dashboard launcher script
├── .env.example                 # Configuration template
├── .env                         # Your credentials (git-ignored)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── EMAIL_SETUP.md               # Email setup guide
├── QUICK_START_EMAIL.md         # Email quick start
├── DASHBOARD_README.md          # Dashboard documentation
├── DASHBOARD_QUICK_START.md     # Dashboard quick start
├── RULE_BASED_RCA.md            # Rule engine documentation
└── KODE_FIX/KODE FIX/           # Data and models
    ├── Historical_Data.csv
    ├── lstm_compressor_17.keras
    └── scaler_17.pkl
```

## Integration Examples

### Scheduled Monitoring (Cron)

```bash
# Add to crontab (run every hour)
0 * * * * cd /path/to/skkmigas && export $(cat .env | xargs) && python main.py --send-email --max-alerts 10 >> logs/monitor.log 2>&1
```

### Real-Time Monitoring Service

```python
from rca_pipeline import run_pipeline
from email_notifier import send_email_alert
import time

while True:
    anomalies, _, _ = run_pipeline(
        csv_path="Historical_Data.csv",
        model_path="lstm_compressor_17.keras",
        scaler_path="scaler_17.pkl",
    )

    for idx, row in anomalies.iterrows():
        send_email_alert(row)

    time.sleep(300)  # Check every 5 minutes
```

### Custom Email Recipients Per Severity

```python
from email_notifier import send_email_alert
from rule_engine import match_scenario

for idx, row in anomalies.iterrows():
    scenarios = match_scenario(row)

    if scenarios and scenarios[0]['severity'] == 'CRITICAL':
        # Send to management for critical issues
        recipients = ['manager@company.com', 'engineer@company.com']
    else:
        # Regular alerts to operations team
        recipients = ['operator@company.com']

    send_email_alert(row, recipients=recipients)
```

## Security Best Practices

1. **Never commit `.env`**: Add to `.gitignore`
2. **Use App Passwords**: For Gmail, use App Password instead of regular password
3. **Rotate credentials**: Change API keys and passwords regularly
4. **Limit recipients**: Only send alerts to authorized personnel
5. **Monitor usage**: Track API and email usage for anomalies
6. **Use TLS**: Always use secure SMTP connections (port 587/465)

## Troubleshooting

### Common Issues

**No anomalies detected**
- Check date range (--start, --end)
- Verify model and scaler paths
- Review threshold settings in rca_pipeline.py

**LLM RCA fails**
- Verify GROQ_API_KEY is set
- Check API rate limits (30 RPM free tier)
- Use --max-samples to limit calls

**Email not sending**
- Run `python test_email.py` to diagnose
- Check SMTP credentials in `.env`
- See [EMAIL_SETUP.md](EMAIL_SETUP.md) for provider-specific setup
- Verify firewall isn't blocking SMTP ports

**"Module not found" errors**
- Install all dependencies: `pip install tensorflow pandas numpy scikit-learn openai python-dotenv`

## Performance

- **Data loading**: ~2-5 seconds for 15,000 rows
- **LSTM inference**: ~10-20 seconds (batch size 2048)
- **Rule classification**: <1 second
- **LLM RCA**: ~2-3 seconds per anomaly (network dependent)
- **Email sending**: ~1-2 seconds per email

For large datasets:
- Use --max-samples to limit LLM calls
- Use --max-alerts to limit email notifications
- Consider parallel processing for batch RCA

## Contributing

For issues, improvements, or questions about the system:

1. Document the issue or enhancement
2. Include example data if relevant
3. Specify environment (Python version, OS, etc.)

## License

Copyright © 2026 SKK Migas - Matindok Field Operations

---

**Need Help?**
- Email setup: See [EMAIL_SETUP.md](EMAIL_SETUP.md)
- Rule engine: See [RULE_BASED_RCA.md](RULE_BASED_RCA.md)
- Test email: Run `python test_email.py`
