# GUARD Quick Start Guide

## 🛡️ What is GUARD?

**GUARD** = Generative Understanding for Anomaly Response & Detection

A comprehensive anomaly detection system for booster compressor monitoring at CPP Donggi field.

---

## 🚀 Quick Start

### 1. Test Email System (with PDF)

```bash
python3 test_guard_email.py
```

**Expected output:**
```
============================================================
  GUARD Email System Test
  Generative Understanding for Anomaly Response & Detection
============================================================

✅ TEST SUCCESSFUL

Check your email for:
  1. Updated subject line (no 'i2AIMS')
  2. GUARD branding in header
  3. Updated email text
  4. PDF attachment (RCA Report)
```

**Email will contain:**
- Subject: `[CPP Donggi] ANOMALY DETECTION - BOOSTER COMPRESSOR B CPP DONGGI`
- Body: HTML-formatted with GUARD branding
- Attachment: `RCA_Report_YYYYMMDD_HHMMSS.pdf`

---

### 2. Launch Live Dashboard

```bash
streamlit run dashboard_live.py
```

**Features:**
- 🛡️ GUARD branding throughout
- 📊 Real-time data simulation
- 📈 Live updating charts
- 📧 Email alert status
- 💬 **NEW:** Chatbot for data search

**Using the Chatbot:**

Scroll to bottom of dashboard and click "🤖 Ask questions about your data"

**Try these queries:**
```
Show me all anomalies in August
What are the top 5 anomalies by MAE?
Show anomalies with gas loss > 0.5 MMSCF
Show me statistics
```

---

### 3. Run Full Demo

```bash
python3 run_demo.py
```

**Then visualize results:**
```bash
streamlit run dashboard_demo.py
```

---

## 📧 Email Example

**Subject:**
```
[CPP Donggi] ANOMALY DETECTION - BOOSTER COMPRESSOR B CPP DONGGI
```

**Header:**
```
[CPP Donggi] ANOMALY DETECTION - BOOSTER COMPRESSOR B CPP DONGGI
GUARD (Generative Understanding for Anomaly Response & Detection)
```

**Body:**
```
An abnormal condition has been detected in the process
parameters of the BOOSTER COMPRESSOR B CPP DONGGI.
The details are as follows:

Anomaly Details
• Timestamp: 2025-03-22 02:06:00
• Threshold ratio: 101.3%
• Asset integrity status: N/A

The main contributing variables and their deviations from
normal operating conditions are listed below:

[Table with top 5 contributing sensors]
```

**Attachment:**
- `RCA_Report_20250322_020600.pdf` (20-30 KB)

---

## 💬 Chatbot Examples

### Example 1: Date-based Search
**Query:** "Show me all anomalies in August"

**Result:** Filters data to August 2025, shows anomalies only

---

### Example 2: Sensor-specific Search
**Query:** "Show anomalies with high flow rate"

**Result:** Anomalies where Flow_Rate > median value

---

### Example 3: Gas Loss Search
**Query:** "Show anomalies with gas loss > 0.5"

**Result:** Anomalies where Gas_Loss_MMSCF > 0.5

---

### Example 4: Top Anomalies
**Query:** "What are the top 5 anomalies by MAE?"

**Result:** Top 5 anomalies sorted by highest MAE

---

### Example 5: Statistics
**Query:** "Show me statistics"

**Result:**
```
Data Summary:
- Total records: 175,110
- Anomalies: 13,448 (7.7%)
- Normal: 161,662 (92.3%)
- Total gas loss: 42.156 MMSCF
- Date range: 2025-01-01 to 2025-12-31
```

---

## 📊 Dashboard Features

### Live Dashboard (dashboard_live.py)

**Top Metrics:**
- Current Time
- Points Processed
- Anomalies Detected
- Emails Sent

**Charts:**
1. **Live Anomaly Detection**
   - MAE timeline
   - Anomaly markers (red X)
   - Current position marker (green triangle)

2. **Live Sensor Readings**
   - Flow Rate
   - Suction Pressure
   - Discharge Pressure
   - Suction Temperature
   - Discharge Temperature

**Alerts Section:**
- Recent anomalies (last 5)
- Email status per anomaly
- Timestamp, MAE, threshold ratio

**Chatbot Section:**
- Natural language search
- Instant results
- Example queries provided

---

## 🔧 Configuration

### Required Files

1. **`.env`** - Email credentials
```env
SMTP_USERNAME=bianfahlesi50@gmail.com
SMTP_PASSWORD=gcyc gdje gywo kxlf
ALERT_TO=bianfahlesi20@gmail.com
```

2. **Data files** (in KODE_FIX/KODE FIX/)
- `Historical_Data.csv`
- `AnomalyDetected_Test.csv`
- `lstm_compressor_17.keras`
- `scaler_17.pkl`

---

## 🎯 What's New in GUARD v1.0

### ✅ Removed
- ❌ "i2AIMS" branding from all emails and dashboards

### ✅ Added
1. **GUARD System Name**
   - Full name: Generative Understanding for Anomaly Response & Detection
   - Displayed in all emails, dashboards, and reports

2. **PDF Report Generation**
   - Professional RCA (Root Cause Analysis) format
   - Landscape A4 layout
   - Comprehensive sensor data table
   - Summary statistics
   - GUARD branding
   - Auto-attached to emails

3. **Dashboard Chatbot**
   - Natural language data search
   - Date-based queries
   - Sensor-specific filtering
   - Top N anomalies
   - Statistics summary
   - Time range filtering

4. **Updated Email Text**
   - More professional language
   - "Abnormal condition" terminology
   - Clearer descriptions
   - Better formatting

---

## 🏃 Typical Workflow

1. **Morning Check** - Run test email
   ```bash
   python3 test_guard_email.py
   ```

2. **Live Demo** - Show stakeholders
   ```bash
   streamlit run dashboard_live.py
   ```
   - Select date range (e.g., Aug 7-15, 2025)
   - Set speed to "Maximum Speed"
   - Enable email alerts
   - Click ▶️ Start

3. **Data Analysis** - Use chatbot
   - "Show me statistics"
   - "What are the top 10 anomalies by MAE?"
   - "Show anomalies in September"

4. **Generate Reports** - Run batch analysis
   ```bash
   python3 run_demo.py
   ```
   - Analyzes specified date range
   - Sends emails with PDF attachments
   - Saves results to CSV

---

## 📱 Mobile-Friendly

All email alerts are mobile-responsive and display correctly on:
- Gmail app (iOS/Android)
- Apple Mail
- Outlook mobile
- Web browsers

PDF attachments open in:
- Default PDF readers
- Mobile browsers
- Email app previews

---

## ⚠️ Troubleshooting

### Email Not Sending

**Check:**
1. `.env` file exists with correct credentials
2. SMTP settings correct (smtp.gmail.com:587)
3. App password generated (not regular password)
4. Internet connection active

**Test:**
```bash
python3 test_guard_email.py
```

### Chatbot Not Responding

**Check:**
1. Data loaded (run simulation first)
2. Query uses supported keywords
3. Try example queries
4. Check for typos

**Supported keywords:**
- Date: "august", "september", etc.
- Sensors: "flow", "pressure", "temperature"
- Actions: "show", "top", "statistics"

### PDF Not Generated

**Check:**
1. reportlab installed: `python3 -c "import reportlab"`
2. Data has required columns
3. Check email_notifier.py imports

**Install if needed:**
```bash
pip3 install --system reportlab
```

---

## 📞 Support Commands

```bash
# Check system
python3 -c "import reportlab; print('✓ reportlab installed')"
python3 -c "import streamlit; print('✓ streamlit installed')"

# Test components
python3 test_guard_email.py          # Test email + PDF
streamlit run dashboard_live.py       # Test dashboard + chatbot

# View logs
tail -f ~/.streamlit/logs/*.log       # Streamlit logs
```

---

## 🎉 Success Indicators

✅ Email subject: `[CPP Donggi]` (no "i2AIMS")
✅ Email header shows: "GUARD (Generative Understanding...)"
✅ PDF attached with RCA data
✅ Dashboard title: "🛡️ GUARD Live Simulation"
✅ Chatbot responds to queries
✅ All charts update in real-time

---

**System Version:** GUARD v1.0
**Last Updated:** January 2025
**Powered by:** Claude Sonnet 4.5
