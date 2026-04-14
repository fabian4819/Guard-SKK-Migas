# PDF Structure - Two Tables

## ✅ Updated PDF Attachment Structure

The PDF now contains **TWO TABLES** as requested:

---

## 📊 TABLE 1: Sensor Values & Deviations

**Purpose:** Shows actual sensor readings, expected values, and deviations

**Columns:**
1. VARIABLE - Sensor parameter name
2. TAG - Sensor tag (FI1001B, PI1001B, etc.)
3. ACTUAL VALUE - Current reading
4. EXPECTED VALUE - Normal/predicted value
5. DEVIATION - Difference (actual - expected)
6. DEVIATION % - Percentage deviation
7. LOSS CONTRIBUTION - % contribution to total anomaly
8. ABNORMALITY - YES/NO if deviation > 10%

**Example:**
```
┌──────────────┬─────────┬────────┬──────────┬───────────┬─────────────┬──────────────┬──────────────┐
│ VARIABLE     │ TAG     │ ACTUAL │ EXPECTED │ DEVIATION │ DEVIATION % │ LOSS CONTRIB │ ABNORMALITY  │
├──────────────┼─────────┼────────┼──────────┼───────────┼─────────────┼──────────────┼──────────────┤
│ Flow Rate    │ FI1001B │  52.64 │    54.99 │     -2.35 │      -4.27% │        68.42%│ NO           │
│ Discharge    │ PI1004B │  63.41 │    63.56 │     -0.15 │      -0.23% │         4.29%│ NO           │
│ Temperature  │         │        │          │           │             │              │              │
│ ...          │ ...     │  ...   │    ...   │     ...   │       ...   │        ...   │ ...          │
└──────────────┴─────────┴────────┴──────────┴───────────┴─────────────┴──────────────┴──────────────┘
```

**Styling:**
- Blue header (#4472C4)
- Alternating white/gray rows
- 5 rows (top 5 contributing sensors)

---

## 🔧 TABLE 2: RCA Division Analysis

**Purpose:** Root cause analysis organized by equipment division with action recommendations

**Columns:** (CODE column removed as requested)
1. SYMPTOM - Division name (INSTRUMENT, PROCESS, MECHANICAL, ELECTRICAL, RELATIONAL)
2. SUB - Division code (305, 390, 440, 525, 225)
3. PROB - Scenario number within division
4. RCA - Detailed root cause description
5. ACTIONS - Recommended corrective actions
6. Flow Rate - YES/NO if affected
7. Suction Press - YES/NO if affected
8. Discharge Press - YES/NO if affected
9. Suction Temp - YES/NO if affected
10. Discharge Temp - YES/NO if affected
11. SYMPTOM - Detailed symptom description

**~~CODE~~** - ❌ Removed (was in far right column)

**Example:**
```
┌────────────┬─────┬──────┬───────────────────┬──────────────────┬─────┬──────┬─────────┬──────┬─────────┬─────────────────────┐
│ SYMPTOM    │ SUB │ PROB │ RCA               │ ACTIONS          │ FR  │ SP   │ DP      │ ST   │ DT      │ SYMPTOM             │
├────────────┼─────┼──────┼───────────────────┼──────────────────┼─────┼──────┼─────────┼──────┼─────────┼─────────────────────┤
│ INSTRUMENT │ 305 │  0   │ Faulty FT         │ Verify FT output │ YES │ NO   │ NO      │ NO   │ NO      │ Inaccurate flow...  │
│            │     │  1   │ PT failure        │ Compare PT       │ NO  │ YES  │ NO      │ NO   │ NO      │ Erratic pressure... │
├────────────┼─────┼──────┼───────────────────┼──────────────────┼─────┼──────┼─────────┼──────┼─────────┼─────────────────────┤
│ PROCESS    │ 390 │  0   │ Gas composition   │ Obtain gas       │ YES │ NO   │ YES     │ NO   │ YES     │ Unexpected perf...  │
│            │     │  1   │ Surge risk        │ Review map       │ YES │ YES  │ YES     │ NO   │ NO      │ Operating near...   │
├────────────┼─────┼──────┼───────────────────┼──────────────────┼─────┼──────┼─────────┼──────┼─────────┼─────────────────────┤
│ MECHANICAL │ 440 │  0   │ Piping stress     │ Inspect supports │ NO  │ YES  │ YES     │ NO   │ NO      │ Unusual vibrations..│
├────────────┼─────┼──────┼───────────────────┼──────────────────┼─────┼──────┼─────────┼──────┼─────────┼─────────────────────┤
│ SUMMARY    │     │      │                   │                  │     │      │         │      │         │ Loss 1.34%...       │
└────────────┴─────┴──────┴───────────────────┴──────────────────┴─────┴──────┴─────────┴──────┴─────────┴─────────────────────┘
```

**Styling:**
- Blue header (#4472C4)
- Color-coded rows by division:
  - INSTRUMENT: Yellow/Beige (#FFF2CC)
  - PROCESS: Yellow/Beige (#FFF2CC)
  - MECHANICAL: Light Blue (#DDEBF7)
  - ELECTRICAL: Light Blue (#DDEBF7)
  - RELATIONAL: Pink/Red (#F4CCCC)
- Gray summary row (#E7E6E6)
- 8-10 rows (most relevant scenarios)

---

## 📄 Complete PDF Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  115-KOST CASE ANOMALI BOOSTER COMPRESSOR B CPP DONGGI         │
│                                                                 │
│  Model/System: J.BEC-UAD        Timestamp: 22 March 2025       │
│  Equipment: BOOSTER COMPRESSOR B    Location: CPP Donggi       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TABLE 1: SENSOR VALUES & DEVIATIONS                           │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ VARIABLE │ TAG │ ACTUAL │ EXPECTED │ DEVIATION │ ... │    │
│  ├──────────┼─────┼────────┼──────────┼───────────┼─────┤    │
│  │ Flow Rate│ ... │  52.64 │    54.99 │     -2.35 │ ... │    │
│  │ Discharge│ ... │  63.41 │    63.56 │     -0.15 │ ... │    │
│  │ ...      │ ... │  ...   │    ...   │     ...   │ ... │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TABLE 2: RCA DIVISION ANALYSIS                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ SYMPTOM │SUB│PROB│ RCA │ ACTIONS │ FR │SP│DP│ST│DT│... │   │
│  ├─────────┼───┼────┼─────┼─────────┼────┼──┼──┼──┼──┼────┤   │
│  │ [YELLOW] INSTRUMENT (305)                              │   │
│  │         │305│ 0  │ ... │ ...     │YES │..│..│..│..│... │   │
│  │         │   │ 1  │ ... │ ...     │NO  │..│..│..│..│... │   │
│  ├─────────┼───┼────┼─────┼─────────┼────┼──┼──┼──┼──┼────┤   │
│  │ [YELLOW] PROCESS (390)                                 │   │
│  │         │390│ 0  │ ... │ ...     │YES │..│..│..│..│... │   │
│  ├─────────┼───┼────┼─────┼─────────┼────┼──┼──┼──┼──┼────┤   │
│  │ [BLUE] MECHANICAL (440)                                │   │
│  │         │440│ 0  │ ... │ ...     │NO  │..│..│..│..│... │   │
│  ├─────────┼───┼────┼─────┼─────────┼────┼──┼──┼──┼──┼────┤   │
│  │ [GRAY] SUMMARY                                         │   │
│  │ SUMMARY │   │    │     │         │    │  │  │  │  │... │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Generated by: GUARD | Date: 2025-XX-XX | Scenarios: 8        │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Changes Made

### **Kept:**
- ✅ TABLE 1: Original sensor values table
  - Shows actual vs expected values
  - Deviation calculations
  - Loss contribution percentages

### **Added:**
- ✅ TABLE 2: RCA division analysis
  - Division categorization
  - Root cause descriptions
  - Action recommendations
  - YES/NO variable matrix
  - Symptom descriptions

### **Removed from Table 2:**
- ❌ CODE column (far right) - Removed as requested
  - Was showing codes like "S.S.F.A", "D.S.P.A", etc.
  - Now only shows SYMPTOM description without code

---

## 🔍 What to Check in Email

### **Open PDF attachment and verify:**

1. **Page should have TWO tables**, not one
2. **TABLE 1** should show:
   - 8 columns (VARIABLE, TAG, ACTUAL VALUE, EXPECTED VALUE, DEVIATION, DEVIATION %, LOSS CONTRIBUTION, ABNORMALITY)
   - 5-6 rows (top contributing sensors)
   - Blue header

3. **TABLE 2** should show:
   - 11 columns (no CODE column at the end)
   - Multiple rows grouped by division
   - Color-coded by division (yellow, blue, pink)
   - Detailed RCA and ACTIONS columns
   - YES/NO columns for sensors
   - SYMPTOM description column (no code)

4. **Far right column** of Table 2 should be:
   - "SYMPTOM" (description text)
   - NOT "CODE" (no S.S.F.A codes)

---

## 📧 Test Email Sent

✅ **Email sent to:** bianfahlesi20@gmail.com
✅ **PDF attached:** RCA_Report_20250322_020600.pdf
✅ **Contains:** 2 tables (sensor values + RCA analysis)
✅ **Table 2 columns:** 11 (CODE column removed)

---

## 🎯 Quick Verification

**Open the PDF and count:**
1. How many tables? → Should be **2**
2. Table 1 columns? → Should be **8**
3. Table 2 columns? → Should be **11**
4. Far right column of Table 2? → Should say **"SYMPTOM"** (not "CODE")

**If all 4 checks pass → Perfect! ✅**

---

**Updated:** 2025-XX-XX
**Version:** GUARD v1.2 (Two-Table PDF)
