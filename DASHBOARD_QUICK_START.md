# Dashboard Quick Start Guide

Get your i2AIMS monitoring dashboard running in 3 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
pip install streamlit plotly
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

## Step 2: Launch Dashboard (30 seconds)

### Option A: Using the launcher script (Recommended)

```bash
./run_dashboard.sh
```

### Option B: Direct command

```bash
streamlit run dashboard.py
```

## Step 3: Access Dashboard (Immediately)

The dashboard will automatically open in your browser at:
```
http://localhost:8501
```

If it doesn't open automatically, copy the URL from the terminal.

## That's It! 🎉

You should now see:
- **Overview Panel** - Key metrics at the top
- **Real-Time Sensors** - Gauge charts showing current values
- **Timeline Tab** - Anomaly detection over time
- **Sensors Tab** - Trend charts for all sensors
- **Anomalies Tab** - Detailed table of all anomalies
- **Analysis Tab** - Scenario analysis and statistics

---

## What You'll See

### Overview Metrics (Top of Page)

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Total Anomalies │ Gas Loss (MMSCF)│ Current Status  │ Data Points     │
│      245        │     12.456      │    NORMAL       │    15,000       │
│  ↓ 1.6% of total│  ⚠️ Critical     │    ✓ Clear      │ Range: 15,000pts│
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### Real-Time Sensor Gauges

Five circular gauges showing:
- **Flow Rate** (MMSCFD)
- **Suction Pressure** (barg)
- **Discharge Pressure** (barg)
- **Suction Temperature** (°C)
- **Discharge Temperature** (°C)

Each with:
- ✅ Green zone = Normal
- 🔴 Red zone = Out of range
- Current value and trend

### Interactive Charts

**Timeline Tab:**
- Blue line = MAE values
- Red X markers = Anomalies
- Dashed line = Threshold
- Zoom, pan, hover for details

**Sensors Tab:**
- All 5 sensors on one chart
- Different colors for each
- Statistics table below

**Anomalies Tab:**
- Sortable table of all anomalies
- Click any row for detailed analysis
- Download CSV button

**Analysis Tab:**
- Bar chart of common scenarios
- Hourly distribution
- Gas loss trends

---

## Using the Dashboard

### Change Date Range

1. Look at **left sidebar**
2. Select **Start Date** and **End Date**
3. Click **🔄 Refresh Data**

### Analyze Specific Anomaly

1. Go to **Anomalies** tab
2. Scroll to **"Select anomaly for detailed analysis"**
3. Choose from dropdown
4. See:
   - Contribution pie chart
   - Matched scenario
   - Root cause
   - Recommended actions
   - Deviation table

### Export Data

1. Go to **Anomalies** tab
2. Click **📥 Download Anomaly Data (CSV)**
3. File saves to your Downloads folder

### Refresh Data

Click **🔄 Refresh Data** in sidebar to:
- Clear cache
- Reload latest data
- Update all charts

---

## Common Tasks

### Monitor Real-Time Status

1. Keep dashboard open
2. Check **Current Status** metric
3. Watch **Real-Time Sensors** gauges
4. Click **🔄 Refresh Data** periodically

### Investigate Anomaly

1. Go to **Anomalies** tab
2. Find anomaly by timestamp
3. Select it from dropdown
4. Review:
   - What sensors contributed most?
   - What scenario matched?
   - What actions are recommended?

### Identify Patterns

1. Go to **Analysis** tab
2. Check **Scenario Analysis** bar chart
3. See which failures occur most
4. Look at **Hourly Distribution**
5. Plan preventive maintenance

### Generate Report

1. Set date range for reporting period
2. Click **🔄 Refresh Data**
3. Go to **Anomalies** tab
4. Click **📥 Download Anomaly Data**
5. Open CSV in Excel/Sheets
6. Create report or presentation

---

## Keyboard Shortcuts

- `R` - Rerun app
- `Ctrl+R` / `Cmd+R` - Refresh browser
- `?` - Show help

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"

```bash
pip install streamlit plotly pandas numpy
```

### Dashboard won't start

Check if port 8501 is already in use:

```bash
# macOS/Linux
lsof -ti:8501 | xargs kill -9

# Then restart
./run_dashboard.sh
```

### No data showing

1. Check that these files exist:
   - `KODE_FIX/KODE FIX/Historical_Data.csv`
   - `KODE_FIX/KODE FIX/lstm_compressor_17.keras`
   - `KODE_FIX/KODE FIX/scaler_17.pkl`

2. Verify date range includes data

3. Click **🔄 Refresh Data**

### Charts not loading

1. Check internet connection (for CDN resources)
2. Try different browser (Chrome/Firefox recommended)
3. Clear browser cache
4. Check terminal for error messages

### Slow performance

1. Reduce date range (try 7-30 days)
2. Click **🔄 Refresh Data** to clear cache
3. Close other browser tabs
4. Check system resources (RAM, CPU)

---

## Next Steps

After launching the dashboard:

1. ✅ **Explore the interface** - Click through all tabs
2. ✅ **Try different date ranges** - See how data changes
3. ✅ **Analyze an anomaly** - Pick one and dive deep
4. ✅ **Export data** - Download and review CSV
5. ✅ **Share** - Show your team!

For advanced features, see [DASHBOARD_README.md](DASHBOARD_README.md)

---

## Integration with Email Alerts

The dashboard complements the email alert system:

- **Email alerts** - Instant notifications when anomalies occur
- **Dashboard** - Investigate, analyze, and track trends

Run both together:

```bash
# Terminal 1: Dashboard
./run_dashboard.sh

# Terminal 2: Email alerts
python3 main.py --send-email --max-alerts 10
```

---

## Mobile Access

Dashboard works on mobile devices!

1. Get your computer's IP address:
   ```bash
   # macOS
   ipconfig getifaddr en0

   # Linux
   hostname -I
   ```

2. Edit `run_dashboard.sh`, change:
   ```bash
   --server.address=localhost
   ```
   to:
   ```bash
   --server.address=0.0.0.0
   ```

3. On mobile browser, go to:
   ```
   http://YOUR_IP:8501
   ```

---

## Demo Mode

Want to show the dashboard to others?

1. Use a good date range with several anomalies:
   ```
   Start: 2025-08-01
   End: 2025-08-31
   ```

2. Prepare talking points:
   - Show Overview metrics
   - Demonstrate Real-Time sensors
   - Navigate through tabs
   - Analyze specific anomaly
   - Show export feature

3. Practice navigation beforehand

---

## Questions?

- **Setup issues**: See [DASHBOARD_README.md](DASHBOARD_README.md)
- **Feature requests**: Document what you'd like to see
- **Bug reports**: Note error messages and steps to reproduce

**Enjoy monitoring! 🏭📊**
