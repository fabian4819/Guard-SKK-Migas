# GUARD System Update Summary

## Overview
Successfully updated the system from "i2AIMS" to **GUARD (Generative Understanding for Anomaly Response & Detection)** with enhanced features including PDF report generation and chatbot functionality.

---

## ✅ Completed Features

### 1. System Rebranding to GUARD

**Files Updated:**
- `email_notifier.py`
- `dashboard_live.py`
- `dashboard_demo.py`
- `run_demo.py`
- `requirements.txt`

**Changes:**
- ✓ Replaced "i2AIMS" with "GUARD (Generative Understanding for Anomaly Response & Detection)"
- ✓ Updated all page titles, headers, and captions
- ✓ Changed page icon from 🏭 to 🛡️
- ✓ Updated documentation strings

---

### 2. Email System Updates

**File:** `email_notifier.py`

**Subject Line:**
- ✗ Before: `[i2AIMS CPP Donggi] ANOMALY DETECTION BOOSTER COMPRESSOR B CPP DONGGI`
- ✓ After: `[CPP Donggi] ANOMALY DETECTION - BOOSTER COMPRESSOR B CPP DONGGI`

**Email Header:**
- ✓ Added GUARD system name subtitle
- ✓ Updated color scheme and branding

**Email Text Changes:**
1. **Main message:**
   - ✗ Before: "An anomaly has been detected on process parameters related to..."
   - ✓ After: "An abnormal condition has been detected in the process parameters of the BOOSTER COMPRESSOR B CPP DONGGI. The details are as follows:"

2. **Contributors section:**
   - ✗ Before: "Below are the details on variables that contributed the most* to anomaly and each deviation from normal condition:"
   - ✓ After: "The main contributing variables and their deviations from normal operating conditions are listed below:"

**Footer:**
- ✗ Before: "This is an automated alert from the i2AIMS (Industrial IoT Anomaly and Integrity Monitoring System)."
- ✓ After: "This is an automated alert from GUARD (Generative Understanding for Anomaly Response & Detection)."

---

### 3. PDF Report Generation

**File:** `email_notifier.py`

**New Function:** `generate_rca_pdf(row, equipment_name)`

**Features:**
- ✓ Generates PDF in landscape A4 format matching Excel RCA layout
- ✓ Includes comprehensive header information:
  - Model/System: J.BEC-UAD
  - Equipment name
  - Timestamp
  - Location (CPP Donggi)
- ✓ RCA table with columns:
  - Variable name
  - Sensor tag
  - Actual value
  - Expected value
  - Deviation
  - Deviation percentage
  - Loss contribution
  - Abnormality status (YES/NO)
  - Symptom/RCA description
- ✓ Summary row with:
  - Threshold ratio
  - Exceed percentage
  - Estimated gas loss (MMSCF)
- ✓ Professional styling with:
  - Blue header (matching company colors)
  - Alternating row backgrounds
  - Grid lines and borders
  - GUARD branding in footer

**Email Attachment:**
- ✓ PDF automatically attached to all anomaly alert emails
- ✓ Filename format: `RCA_Report_YYYYMMDD_HHMMSS.pdf`
- ✓ File size: ~20-30 KB per report

**Dependencies Added:**
- ✓ reportlab>=4.0.0 (already installed on system)

---

### 4. Dashboard Chatbot

**File:** `dashboard_live.py`

**New Feature:** Data Search Assistant

**Location:** Bottom of dashboard (above footer)

**Capabilities:**
1. **Date-based queries:**
   - "Show me all anomalies in August"
   - "What happened on August 10, 2025?"

2. **Sensor-specific queries:**
   - "Show anomalies with high flow rate"
   - "Show anomalies with high discharge pressure"
   - "Show anomalies with high temperature"

3. **Gas loss queries:**
   - "Show anomalies with gas loss > 0.5 MMSCF"

4. **Top N queries:**
   - "What are the top 5 anomalies by MAE?"
   - "Show top 10 anomalies"

5. **Time-based queries:**
   - "Show normal readings between 8 AM and 5 PM"
   - "Show anomalies between 9 AM and 6 PM"

6. **Statistics queries:**
   - "Show statistics"
   - "Give me a summary"
   - "Show overview"

7. **Status queries:**
   - "Show all anomalies"
   - "Show normal readings"

**Display:**
- ✓ Shows up to 50 matching results in table format
- ✓ Displays relevant columns: MAE, status, sensor values, gas loss
- ✓ Formatted timestamps for easy reading
- ✓ Success/warning/error messages for user feedback
- ✓ Example queries shown in expandable section

**User Experience:**
- ✓ Simple text input interface
- ✓ Natural language understanding (keyword-based)
- ✓ Helpful error messages if query not understood
- ✓ Expandable panel to save space

---

## 📧 Email Test Results

**Test performed:** ✅ Successful

**Test file:** `test_guard_email.py`

**Verified:**
- ✓ Email sent to: bianfahlesi20@gmail.com
- ✓ Subject line updated (no "i2AIMS")
- ✓ GUARD branding in header
- ✓ Updated email text
- ✓ PDF attachment generated and included
- ✓ All data formatting correct

**Sample Test Anomaly:**
- Timestamp: 2025-03-22 02:06:00
- MAE: 0.2027
- Threshold ratio: 101.34%

---

## 🔧 Technical Improvements

### Data Type Handling
**Problem:** CSV data contains string values for numeric fields (with % signs)

**Solution:** Added robust string-to-float conversion in:
- `get_top_contributors()` function
- `generate_rca_pdf()` function
- `build_email_html()` function

**Benefits:**
- ✓ Handles mixed data types gracefully
- ✓ Strips % signs and commas automatically
- ✓ Prevents ValueError exceptions
- ✓ Works with both string and numeric inputs

---

## 📁 Updated Files Summary

1. **email_notifier.py** (major update)
   - System rebranding
   - Email text updates
   - PDF generation function
   - String handling improvements

2. **dashboard_live.py** (major update)
   - GUARD branding
   - Chatbot component added
   - Updated title and footer

3. **dashboard_demo.py** (minor update)
   - GUARD branding
   - Updated title and footer

4. **run_demo.py** (minor update)
   - GUARD branding
   - Updated print messages

5. **requirements.txt** (minor update)
   - Added reportlab dependency
   - Updated header comment

6. **test_guard_email.py** (new file)
   - Email testing script
   - PDF attachment verification

---

## 🚀 How to Use

### 1. Send Email with PDF Attachment

```bash
# Test email system
python3 test_guard_email.py

# Run full analysis with emails
python3 run_demo.py
```

### 2. Launch Live Dashboard with Chatbot

```bash
streamlit run dashboard_live.py
```

**Steps:**
1. Select date range in sidebar
2. Choose playback speed
3. Click ▶️ Start to begin simulation
4. Watch live charts update
5. Scroll down to use chatbot for data search

**Chatbot Examples:**
- Type: "Show me all anomalies in August"
- Type: "What are the top 5 anomalies by MAE?"
- Type: "Show anomalies with gas loss > 0.5"

### 3. Run Demo Dashboard

```bash
streamlit run dashboard_demo.py
```

---

## 📊 System Architecture

```
GUARD System
├── Email Alerts
│   ├── HTML-formatted emails
│   ├── PDF attachments (RCA reports)
│   └── SMTP delivery
│
├── Live Dashboard
│   ├── Real-time simulation
│   ├── Live charts (MAE & sensors)
│   ├── Anomaly detection display
│   └── Chatbot (data search)
│
├── Demo Dashboard
│   ├── Date range selection
│   ├── On-demand analysis
│   ├── Email alert summary
│   └── Data visualization
│
└── Data Pipeline
    ├── LSTM anomaly detection
    ├── Rule-based classification
    └── Gas loss calculation
```

---

## 🎯 Requirements Completed

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Remove "i2AIMS" from Gmail subject | ✅ Done |
| 2 | Generate PDF attachment in email (RCA format) | ✅ Done |
| 3 | Add "GUARD" system name to Gmail & dashboard | ✅ Done |
| 4 | Add chatbot to dashboard for data search | ✅ Done |
| 5 | Update email text (abnormal condition) | ✅ Done |
| 6 | Update email text (contributing variables) | ✅ Done |

---

## 📝 Configuration

### Email Settings (.env)
```env
SMTP_USERNAME=bianfahlesi50@gmail.com
SMTP_PASSWORD=gcyc gdje gywo kxlf
ALERT_TO=bianfahlesi20@gmail.com
```

### System Constants (email_notifier.py)
```python
SYSTEM_NAME = "GUARD (Generative Understanding for Anomaly Response & Detection)"
EQUIPMENT_NAME = "BOOSTER COMPRESSOR B CPP DONGGI"
FIELD_NAME = "CPP Donggi"
MODEL_SYSTEM = "J.BEC-UAD"
```

---

## 🔍 Next Steps (Optional Enhancements)

1. **Chatbot AI Integration:**
   - Connect to LLM (GPT-4, Claude, or Groq) for natural language understanding
   - Enable complex queries and conversational interface

2. **PDF Customization:**
   - Add company logo
   - Include graphs/charts in PDF
   - Multi-page reports for batch anomalies

3. **Dashboard Enhancements:**
   - Real-time notifications
   - Export functionality
   - Custom date/time filters

4. **Email Templates:**
   - Multiple severity levels
   - Custom templates per equipment type
   - Recipient groups

---

## ✅ Testing Checklist

- [x] Email sends successfully
- [x] PDF attachment generated
- [x] Subject line updated (no "i2AIMS")
- [x] Email text updated
- [x] GUARD branding visible
- [x] Dashboard displays GUARD name
- [x] Chatbot responds to queries
- [x] Live simulation works
- [x] Demo dashboard works
- [x] String data types handled correctly

---

## 📞 Support

For issues or questions:
1. Check email configuration in `.env`
2. Verify reportlab is installed: `python3 -c "import reportlab"`
3. Test email system: `python3 test_guard_email.py`
4. Check dashboard: `streamlit run dashboard_live.py`

---

**Generated:** 2025-01-XX
**Version:** GUARD v1.0
**Author:** Claude Code (Sonnet 4.5)
