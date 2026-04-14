"""
Rule-Based Classification Engine for Booster Compressor Monitoring.

Classifies sensor readings into HIGH / LOW / NORMAL based on
operating thresholds defined per parameter.
"""

import pandas as pd
import numpy as np


# ── Tag → Parameter mapping ────────────────────────────────────────

TAG_MAP = {
    "FI1001B": "Flow_Rate",
    "PI1001B": "Suction_Pressure",
    "PI1004B": "Discharge_Pressure",
    "TI1003B": "Suction_Temperature",
    "TI1004B": "Discharge_Temperature",
}

PARAM_TO_TAG = {v: k for k, v in TAG_MAP.items()}

UNITS = {
    "Flow_Rate": "MMSCFD",
    "Suction_Pressure": "barg",
    "Discharge_Pressure": "barg",
    "Suction_Temperature": "C",
    "Discharge_Temperature": "C",
}


# ── Threshold definitions ──────────────────────────────────────────

THRESHOLDS = {
    "Flow_Rate": {
        "tag": "FI1001B",
        "low": 45,
        "high": 56,
        "unit": "MMSCFD",
    },
    "Suction_Pressure": {
        "tag": "PI1001B",
        "low": 33,
        "high": 34,
        "unit": "barg",
    },
    "Discharge_Pressure": {
        "tag": "PI1004B",
        "low": 60,
        "high": 63.3,
        "unit": "barg",
    },
    "Suction_Temperature": {
        "tag": "TI1003B",
        "low": 90,
        "high": 100,
        "unit": "C",
    },
    "Discharge_Temperature": {
        "tag": "TI1004B",
        "low": 189,
        "high": 205,
        "unit": "C",
    },
}


# ── Classification functions ───────────────────────────────────────

def classify_parameter(value: float, low: float, high: float) -> str:
    """Classify a single sensor reading into HIGH / LOW / NORMAL."""
    if pd.isna(value):
        return "UNKNOWN"
    if value > high:
        return "HIGH"
    elif value < low:
        return "LOW"
    else:
        return "NORMAL"


def classify_row(row: pd.Series) -> dict:
    """Classify all parameters for a single timestep row."""
    result = {}
    for param, bounds in THRESHOLDS.items():
        val = row.get(param, np.nan)
        result[param] = classify_parameter(val, bounds["low"], bounds["high"])
    return result


def apply_rule_based(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply rule-based classification to every row of a DataFrame.
    Adds a column '<param>_rule' for each monitored parameter.
    """
    for param, bounds in THRESHOLDS.items():
        if param in df.columns:
            df[f"{param}_rule"] = df[param].apply(
                lambda v, lo=bounds["low"], hi=bounds["high"]: classify_parameter(v, lo, hi)
            )
    return df


# ── Scenario matching ──────────────────────────────────────────────

SCENARIOS = [
    {
        "id": 1,
        "name": "Upstream Supply Restriction",
        "conditions": {
            "Flow_Rate": "LOW",
            "Suction_Pressure": "LOW",
        },
        "root_cause": "Upstream supply restriction or inlet valve issue causing reduced flow and suction pressure",
        "severity": "HIGH",
        "actions": [
            "Check upstream supply pressure and flow conditions",
            "Inspect inlet valve position and operation",
            "Verify pipeline integrity upstream of compressor",
        ],
    },
    {
        "id": 2,
        "name": "Discharge Blockage",
        "conditions": {
            "Discharge_Pressure": "HIGH",
            "Discharge_Temperature": "HIGH",
        },
        "root_cause": "Discharge blockage or discharge valve partially closed, causing pressure buildup and temperature rise",
        "severity": "CRITICAL",
        "actions": [
            "Check discharge valve position immediately",
            "Inspect discharge piping for blockages",
            "Monitor compressor for potential trip conditions",
        ],
    },
    {
        "id": 3,
        "name": "Cooler Failure",
        "conditions": {
            "Suction_Temperature": "HIGH",
            "Discharge_Temperature": "HIGH",
        },
        "root_cause": "Aftercooler or intercooler failure leading to insufficient cooling across the compressor",
        "severity": "HIGH",
        "actions": [
            "Verify cooler water/gas flow rates",
            "Check cooler outlet temperatures",
            "Inspect cooler for fouling or tube damage",
        ],
    },
    {
        "id": 4,
        "name": "Inlet Filter Plugging",
        "conditions": {
            "Flow_Rate": "LOW",
            "Suction_Pressure": "LOW",
            "Discharge_Pressure": "LOW",
        },
        "root_cause": "Inlet filter plugging or pipeline restriction reducing gas supply to the compressor",
        "severity": "MEDIUM",
        "actions": [
            "Inspect and clean/replace inlet filter",
            "Check differential pressure across inlet filter",
            "Verify suction line for restrictions",
        ],
    },
    {
        "id": 5,
        "name": "Compressor Fouling / Internal Wear",
        "conditions": {
            "Flow_Rate": "LOW",
            "Discharge_Pressure": "HIGH",
        },
        "root_cause": "Compressor internal fouling or wear reducing efficiency, causing low flow and high discharge pressure",
        "severity": "HIGH",
        "actions": [
            "Schedule compressor inspection and overhaul",
            "Monitor vibration and bearing temperatures",
            "Review performance trend for degradation rate",
        ],
    },
    {
        "id": 6,
        "name": "Downstream Leak / Relief Valve",
        "conditions": {
            "Flow_Rate": "HIGH",
            "Discharge_Pressure": "LOW",
        },
        "root_cause": "Downstream leak or relief valve open, causing high flow with low discharge pressure",
        "severity": "CRITICAL",
        "actions": [
            "Check downstream piping for leaks immediately",
            "Verify relief valve status (open/closed)",
            "Isolate and depressurize affected section if needed",
        ],
    },
    {
        "id": 7,
        "name": "Suction Separator Issue",
        "conditions": {
            "Suction_Pressure": "LOW",
            "Suction_Temperature": "HIGH",
        },
        "root_cause": "Suction separator malfunction or liquid carryover causing low suction pressure with elevated temperature",
        "severity": "MEDIUM",
        "actions": [
            "Check suction separator liquid level",
            "Drain separator if liquid level is high",
            "Inspect separator internals for damage",
        ],
    },
]


def match_scenario(row: pd.Series) -> list:
    """
    Match anomaly row against known scenarios.
    Returns list of matching scenario dicts, sorted by number of matched conditions (best first).
    """
    matches = []
    for scenario in SCENARIOS:
        conditions = scenario["conditions"]
        matched = 0
        total = len(conditions)
        for param, expected_state in conditions.items():
            rule_col = f"{param}_rule"
            actual = row.get(rule_col, "UNKNOWN")
            if actual == expected_state:
                matched += 1
        if matched == total and total > 0:
            matches.append({**scenario, "matched_conditions": matched})
    matches.sort(key=lambda x: x["matched_conditions"], reverse=True)
    return matches


def get_all_rules(row: pd.Series) -> dict:
    """Return dict of parameter → rule classification for a row."""
    rules = {}
    for param in THRESHOLDS:
        rules[param] = row.get(f"{param}_rule", "UNKNOWN")
    return rules


def get_non_normal_rules(row: pd.Series) -> dict:
    """Return only parameters that are NOT NORMAL."""
    all_rules = get_all_rules(row)
    return {k: v for k, v in all_rules.items() if v != "NORMAL"}
