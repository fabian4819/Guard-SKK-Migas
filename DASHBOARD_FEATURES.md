# i2AIMS Dashboard - Feature Overview

Complete visual guide to all dashboard components and capabilities.

## 🎯 Dashboard Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  SIDEBAR                │  MAIN CONTENT AREA                     │
├─────────────────────────┼────────────────────────────────────────┤
│                         │                                        │
│  [i2AIMS Logo]          │  🏭 i2AIMS - CPP Donggi               │
│                         │  BOOSTER COMPRESSOR B CPP DONGGI       │
│  ⚙️ Settings            │  Last Updated: 2026-04-12 10:30:00    │
│                         │                                        │
│  📅 Date Range          │  ┌──────────────────────────────────┐ │
│  ┌─────────────┐        │  │  OVERVIEW METRICS (4 cards)      │ │
│  │ Start Date  │        │  ├──────────┬──────────┬──────────┬─┤ │
│  │ 2026-03-13  │        │  │ Total    │ Gas Loss │ Current  │D│ │
│  └─────────────┘        │  │Anomalies │ (MMSCF)  │ Status   │P│ │
│  ┌─────────────┐        │  └──────────┴──────────┴──────────┴─┘ │
│  │ End Date    │        │                                        │
│  │ 2026-04-12  │        │  ════════════════════════════════════ │
│  └─────────────┘        │                                        │
│                         │  📊 REAL-TIME SENSOR READINGS          │
│  [🔄 Refresh Data]      │  ┌──────┬──────┬──────┬──────┬──────┐ │
│                         │  │Gauge │Gauge │Gauge │Gauge │Gauge │ │
│  ─────────────────      │  │ 1    │ 2    │ 3    │ 4    │ 5    │ │
│                         │  └──────┴──────┴──────┴──────┴──────┘ │
│  📧 Email Alerts        │                                        │
│  [Send Test Email]      │  ════════════════════════════════════ │
│                         │                                        │
│  ─────────────────      │  📑 TABS                               │
│                         │  ┌─────┬─────┬─────┬─────┐           │
│  About                  │  │Time │Sens │Anom │Anal │           │
│  Equipment: ...         │  │line │ors  │alies│ysis │           │
│  Field: CPP Donggi      │  └─────┴─────┴─────┴─────┘           │
│                         │                                        │
│                         │  [TAB CONTENT AREA - Dynamic]          │
│                         │                                        │
└─────────────────────────┴────────────────────────────────────────┘
```

---

## 📊 Component Details

### 1. Overview Metrics Panel

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Total Anomalies │ Gas Loss (MMSCF)│ Current Status  │ Data Points     │
│ ─────────────── │ ─────────────── │ ─────────────── │ ─────────────── │
│      245        │     12.456      │    NORMAL       │    15,000       │
│  ↓ 1.6% of total│  ⚠️ Critical     │    ✓ Clear      │ Range: 15K pts  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

**Features:**
- Live metrics with delta indicators
- Color-coded alerts (green/yellow/red)
- Percentage calculations
- Tooltips on hover

---

### 2. Real-Time Sensor Gauges

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Flow Rate  │ │  Suction    │ │ Discharge   │ │  Suction    │ │ Discharge   │
│             │ │  Pressure   │ │ Pressure    │ │ Temperature │ │ Temperature │
│      ●      │ │      ●      │ │      ●      │ │      ●      │ │      ●      │
│    / | \    │ │    / | \    │ │    / | \    │ │    / | \    │ │    / | \    │
│   /  |  \   │ │   /  |  \   │ │   /  |  \   │ │   /  |  \   │ │   /  |  \   │
│  50.2 MMSCFD│ │  33.5 barg  │ │  61.2 barg  │ │  95°C       │ │  192°C      │
│             │ │             │ │             │ │             │ │             │
│  [NORMAL]   │ │  [NORMAL]   │ │  [NORMAL]   │ │  [NORMAL]   │ │  [NORMAL]   │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

**Features:**
- Circular gauge visualization
- Green zone = normal range
- Red zones = out of threshold
- Real-time value display
- Status badge below each gauge
- Delta from target value

**Color Coding:**
- 🟢 Green needle = Within thresholds
- 🔴 Red needle = Outside thresholds
- ⚪ Gray background = Low risk zone
- 🟢 Green background = Normal zone
- 🔴 Red background = High risk zone

---

### 3. Timeline Tab

```
     MAE vs Time with Anomaly Detection
     ────────────────────────────────────────────────
 8   │                                    ╳
 7   │                          ╳              ╳
 6   │               ╳    ╳                         ╳
 5   │     ╳                           ╳
 4   │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  Threshold
 3   │        ___                ___
 2   │   ___/   \___        ___/   \___
 1   │___            \___/              \___
 0   └────────────────────────────────────────────
     Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep

     Legend:
     ──── MAE (Mean Absolute Error)
     ╳    Anomaly detected
     ─ ─  Threshold line
```

**Features:**
- Interactive line chart
- Hover for exact values
- Zoom and pan controls
- Anomaly markers (red X)
- Threshold visualization
- Time range selector
- Summary statistics below

**Statistics Cards:**
```
┌───────────────┬───────────────┬───────────────┐
│ Total Data    │ Anomalies     │ Average MAE   │
│ Points        │ Detected      │               │
│ 15,000        │ 245           │ 2.3456        │
└───────────────┴───────────────┴───────────────┘
```

---

### 4. Sensors Tab

```
     All Sensor Readings Over Time
     ────────────────────────────────────────────────
 100 │                                    ┌── Discharge Temp
 90  │                            ┌───────┘
 80  │              ┌─────────────┘
 70  │          ────┘                     ┌── Discharge Press
 60  │      ────────────────────────────┬─┘
 50  │  ────────────────────────────────┘    ┌── Flow Rate
 40  │  ┌──────────────────────────────────┬─┘
 30  │  └────────── Suction Pressure ──────┘
 20  │
 10  │
  0  └────────────────────────────────────────────
     Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep

     ── Flow Rate          ── Discharge Pressure
     ── Suction Pressure   ── Suction Temperature
     ── Discharge Temperature
```

**Features:**
- Multi-line chart
- Legend with color codes
- Toggle lines on/off
- Hover for all values
- Synchronized time axis

**Sensor Statistics Table:**
```
┌────────────────────┬──────┬──────┬──────┬──────┬─────┬──────┬──────────┬──────────┐
│ Parameter          │ Tag  │ Unit │ Mean │ Min  │ Max │StdDev│Low Thresh│High Thresh│
├────────────────────┼──────┼──────┼──────┼──────┼─────┼──────┼──────────┼──────────┤
│ Flow_Rate          │FI1001│MMSCFD│ 50.2 │ 42.1 │ 55.8│ 2.45 │   45     │    56    │
│ Suction_Pressure   │PI1001│ barg │ 33.4 │ 31.2 │ 34.0│ 0.56 │   33     │    34    │
│ Discharge_Pressure │PI1004│ barg │ 61.5 │ 59.8 │ 63.1│ 0.78 │   60     │   63.3   │
│ Suction_Temperature│TI1003│  °C  │ 95.2 │ 88.5 │ 99.8│ 2.34 │   90     │   100    │
│ Discharge_Temp     │TI1004│  °C  │ 195.3│ 185.2│ 203.5│3.56 │  189     │   205    │
└────────────────────┴──────┴──────┴──────┴──────┴─────┴──────┴──────────┴──────────┘
```

---

### 5. Anomalies Tab

**Main Table:**
```
┌──────────────────┬────────┬──────────┬──────────┬─────────┬──────┬──────┬──────┬──────┬──────┐
│ Timestamp        │  MAE   │Threshold │  Exceed  │Gas Loss │ Flow │Suct P│Disch │Suct T│Disch │
│                  │        │  Ratio   │ Percent  │ (MMSCF) │ Rate │      │Press │      │ Temp │
├──────────────────┼────────┼──────────┼──────────┼─────────┼──────┼──────┼──────┼──────┼──────┤
│2026-01-19 19:33:00│ 5.2341│ 130.5%   │  30.5%   │0.052341 │ 42.5 │ 31.2 │ 65.8 │ 95.3 │198.7 │
│2026-01-20 08:15:00│ 4.8923│ 122.3%   │  22.3%   │0.048923 │ 43.8 │ 32.1 │ 64.2 │ 93.8 │196.4 │
│2026-01-21 14:47:00│ 6.1234│ 153.1%   │  53.1%   │0.061234 │ 41.2 │ 30.5 │ 66.9 │ 97.2 │201.3 │
│      ...         │  ...   │   ...    │   ...    │   ...   │ ...  │ ...  │ ...  │ ...  │ ...  │
└──────────────────┴────────┴──────────┴──────────┴─────────┴──────┴──────┴──────┴──────┴──────┘

[📥 Download Anomaly Data (CSV)]
```

**Detailed View (when anomaly selected):**

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🔬 Anomaly Detail: 2026-01-19 19:33:00                              │
├──────────────────────────────┬──────────────────────────────────────┤
│ Basic Info                   │ Contribution Analysis                │
│                              │                                      │
│ MAE: 5.2341                  │        [PIE CHART]                   │
│ Threshold Ratio: 130.5%      │     ┌─────────────┐                 │
│ Exceed Percent: 30.5%        │   ┌─┤ Flow Rate   │ 40.9%           │
│ Gas Loss: 0.052341 MMSCF     │  ┌┼─┤ Suction P   │ 37.7%           │
│                              │ ┌┼┼─┤ Discharge P │ 12.8%           │
│ Matched Scenario             │ └┼┼─┤ Suction T   │  5.6%           │
│ ⚠️ Upstream Supply           │  └┼─┤ Discharge T │  3.0%           │
│    Restriction               │   └─┴─────────────┘                 │
│ Severity: HIGH               │                                      │
│                              │                                      │
│ Root Cause:                  │                                      │
│ Upstream supply restriction  │                                      │
│ or inlet valve issue         │                                      │
│                              │                                      │
│ Recommended Actions:         │                                      │
│ • Check upstream supply      │                                      │
│ • Inspect inlet valve        │                                      │
│ • Verify pipeline integrity  │                                      │
└──────────────────────────────┴──────────────────────────────────────┘

Sensor Deviations
┌───────────────────┬──────┬────────────┬────────────┬────────────┬──────────┬────────┐
│ Parameter         │ Tag  │ Actual     │ Expected   │ Deviation  │Contribut │ Status │
├───────────────────┼──────┼────────────┼────────────┼────────────┼──────────┼────────┤
│ Flow_Rate         │FI1001│ 42.50 MMSCFD│ 44.80 MMSCFD│-2.30 (-5.1%)│  40.9%  │  LOW   │
│ Suction_Pressure  │PI1001│ 31.20 barg │ 33.00 barg │-1.80 (-5.5%)│  37.7%  │  LOW   │
│ Discharge_Pressure│PI1004│ 65.80 barg │ 63.30 barg │+2.50 (+3.9%)│  12.8%  │  HIGH  │
│ Suction_Temp      │TI1003│ 95.30 °C   │ 92.20 °C   │+3.10 (+3.4%)│   5.6%  │ NORMAL │
│ Discharge_Temp    │TI1004│ 198.7 °C   │ 193.3 °C   │+5.40 (+2.8%)│   3.0%  │ NORMAL │
└───────────────────┴──────┴────────────┴────────────┴────────────┴──────────┴────────┘
```

---

### 6. Analysis Tab

**Scenario Analysis:**
```
     Most Common Failure Scenarios
     ────────────────────────────────────────────────
     Upstream Supply Restriction (HIGH)      ████████████████████ 45
     Discharge Blockage (CRITICAL)           ████████████ 28
     Cooler Failure (HIGH)                   ██████████ 23
     Inlet Filter Plugging (MEDIUM)          ████████ 18
     Compressor Fouling/Wear (HIGH)          ██████ 12
     Downstream Leak (CRITICAL)              ████ 8
     Suction Separator Issue (MEDIUM)        ██ 5
     ────────────────────────────────────────────────
                                              Count
```

**Hourly Distribution:**
```
     Anomalies by Hour of Day
     ────────────────────────────────────────────────
  25│              ▄
  20│         ▄    █    ▄
  15│    ▄    █    █    █         ▄
  10│    █    █    █    █    ▄    █
   5│    █    █    █    █    █    █    ▄
   0└────────────────────────────────────────────────
     00  02  04  06  08  10  12  14  16  18  20  22
                        Hour of Day
```

**Gas Loss Trend:**
```
     Cumulative Gas Loss Over Time
     ────────────────────────────────────────────────
12  │                                            ╱───
11  │                                      ╱────╱
10  │                                ╱────╱
 9  │                          ╱────╱
 8  │                    ╱────╱
 7  │              ╱────╱
 6  │        ╱────╱
 5  │  ╱────╱
 4  │─╱
    └────────────────────────────────────────────────
     Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep
               Time Period
```

---

## 🎨 Dashboard Features Summary

### Visualization Types

1. **Metric Cards** - KPI displays with deltas
2. **Gauge Charts** - Real-time sensor readings
3. **Line Charts** - Time series trends
4. **Bar Charts** - Categorical comparisons
5. **Pie Charts** - Contribution breakdown
6. **Data Tables** - Detailed tabular data
7. **Scatter Plots** - Anomaly markers
8. **Heatmaps** - Pattern analysis (future)

### Interactive Elements

- ✅ **Hover tooltips** - Detailed info on hover
- ✅ **Click selection** - Select anomalies for detail view
- ✅ **Zoom/Pan** - Interactive chart navigation
- ✅ **Date picker** - Custom date range selection
- ✅ **Dropdowns** - Filter and select options
- ✅ **Buttons** - Actions (refresh, download, email)
- ✅ **Tabs** - Multiple view organization
- ✅ **Collapsible sections** - Organized layout

### Data Operations

- 📊 **Real-time loading** - Auto-refresh capability
- 💾 **Export to CSV** - Download anomaly data
- 🔍 **Filtering** - Date range, status, severity
- 📈 **Aggregation** - Statistics and summaries
- 🔄 **Caching** - Performance optimization
- 📱 **Responsive** - Works on mobile devices

### Color Coding

- 🟢 **Green** - Normal, OK, Within limits
- 🟡 **Yellow** - Warning, Attention needed
- 🔴 **Red** - Critical, Out of limits, Anomaly
- 🔵 **Blue** - Info, Neutral, Header
- ⚫ **Gray** - Disabled, Inactive, Background

---

## 📱 Responsive Design

### Desktop (> 1024px)
- Full multi-column layout
- All charts visible simultaneously
- Sidebar expanded
- Large gauges

### Tablet (768px - 1024px)
- 2-column layout
- Stacked sections
- Collapsible sidebar
- Medium gauges

### Mobile (< 768px)
- Single column layout
- Simplified charts
- Hidden sidebar (toggle)
- Small gauges
- Touch-friendly controls

---

## 🚀 Performance Features

- **Lazy Loading** - Load data only when needed
- **Caching** - 5-minute cache for data queries
- **Pagination** - Handle large datasets
- **Debouncing** - Prevent excessive API calls
- **Compression** - Efficient data transfer
- **CDN** - Fast library loading

---

## 🔐 Security Features

- **No sensitive data exposure** - Credentials in .env
- **Read-only by default** - No data modification
- **Local deployment** - Runs on localhost
- **HTTPS ready** - TLS support via reverse proxy
- **Authentication** - Pluggable auth system
- **Audit logging** - Track user actions (future)

---

## 🎯 Use Cases

### 1. Operations Team
- Monitor real-time status
- Receive alerts immediately
- Track production impact
- Generate daily reports

### 2. Maintenance Team
- Identify failure patterns
- Plan preventive maintenance
- Analyze root causes
- Track equipment health

### 3. Management
- View KPIs at a glance
- Assess production losses
- Review trends and patterns
- Make data-driven decisions

### 4. Engineers
- Deep dive into anomalies
- Analyze sensor correlations
- Validate ML model performance
- Tune thresholds and rules

---

## 📊 Data Flow

```
User Opens Dashboard
         ↓
Date Range Selected
         ↓
Load Historical Data (CSV)
         ↓
Run LSTM Model
         ↓
Apply Rule Engine
         ↓
Match Scenarios
         ↓
Display Results
         ↓
User Interaction (Click/Filter/Zoom)
         ↓
Update Views
         ↓
Export/Email (Optional)
```

---

## 🎓 Learning Path

### Beginner (Day 1)
- [ ] Launch dashboard
- [ ] Navigate all tabs
- [ ] Read overview metrics
- [ ] Check sensor gauges
- [ ] View anomaly table

### Intermediate (Week 1)
- [ ] Change date ranges
- [ ] Analyze specific anomalies
- [ ] Understand scenarios
- [ ] Export data
- [ ] Compare time periods

### Advanced (Month 1)
- [ ] Identify patterns
- [ ] Correlate sensors
- [ ] Predict failures
- [ ] Optimize thresholds
- [ ] Customize dashboard

---

**For detailed documentation, see [DASHBOARD_README.md](DASHBOARD_README.md)**

**For quick start, see [DASHBOARD_QUICK_START.md](DASHBOARD_QUICK_START.md)**
