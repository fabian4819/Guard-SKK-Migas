"""
RCA Knowledge Base for Booster Compressor B CPP Donggi
Based on "RCA FOR RULE BASED - Sheet1.pdf"

Contains comprehensive Root Cause Analysis scenarios organized by division.
"""

import pandas as pd

# RCA Scenarios organized by division
RCA_DATABASE = {
    "INSTRUMENT": {
        "division_code": 305,
        "color": "#FFF2CC",  # Yellow/beige
        "scenarios": [
            {
                "id": "INST-0",
                "probable": "Flow Transmitter (FT) Malfunction & calibration",
                "rca": "Faulty FT producing incorrect flow readings due to drift in A readings through damaged sensor element. Electrical noise or damaged cable/wiring. Calibration errors due to improper setup/span adjustment.",
                "actions": "Verify FT output signal against actual flow using secondary measurement. Check wiring and signal integrity. Recalibrate or replace FT if necessary.",
                "variables": {"Flow_Rate": True},
                "symptom": "Inaccurate flow readings, reported flow rate significantly deviates from actual conditions causing incorrect MAE calculations.",
                "symptom_code": "S.S.F.A"
            },
            {
                "id": "INST-1",
                "probable": "Suction Pressure Transmitter (PT) Dysfunction",
                "rca": "PT failure causing erratic or constant readings not reflecting actual suction pressure. Sensor drift, membrane damage, or electrical connection issues. Impulse line blockage/leak affecting reading accuracy.",
                "actions": "Compare PT reading with independent pressure gauge. Inspect impulse lines for blockage/leaks. Check electrical connections. Calibrate or replace PT.",
                "variables": {"Suction_Pressure": True},
                "symptom": "Erratic or incorrect suction pressure readings leading to false anomaly detection or missed real issues.",
                "symptom_code": "S.S.F.A + D.S.P.A"
            },
            {
                "id": "INST-2",
                "probable": "Discharge Pressure Transmitter (PT) Malfunction",
                "rca": "Faulty discharge PT providing inaccurate pressure data. Sensor element degradation, impulse line issues. Environmental factors affecting sensor performance (vibration/temperature).",
                "actions": "Verify pressure reading with backup gauge. Check impulse line condition. Inspect sensor mounting and environmental conditions. Replace if drift confirmed.",
                "variables": {"Discharge_Pressure": True},
                "symptom": "Incorrect discharge pressure causing wrong MAE calculations and missed anomaly detection especially during discharge.",
                "symptom_code": "S.S.F.A + D.S.P.A"
            },
            {
                "id": "INST-3",
                "probable": "Suction Temperature Transmitter (TT) Malfunction",
                "rca": "TT sensor failure or calibration drift. Thermowell damage exposing sensor. Signal wiring issues. Environmental interference affecting readings.",
                "actions": "Validate temperature reading with portable thermometer. Check thermowell integrity and sensor installation. Verify wiring. Recalibrate or replace TT.",
                "variables": {"Suction_Temperature": True},
                "symptom": "Unreliable suction temperature data affecting thermal efficiency calculations and anomaly detection during suction phase.",
                "symptom_code": "S.S.T + D.S.T + MAE:↑"
            },
            {
                "id": "INST-4",
                "probable": "Discharge Temperature Transmitter (TT) Issue",
                "rca": "Discharge TT malfunction providing false temperature readings. Sensor degradation from high temperature exposure. Improper installation or thermowell issues.",
                "actions": "Cross-check with redundant temperature sensor. Inspect thermowell and sensor mounting. Test sensor output independently. Replace if faulty.",
                "variables": {"Discharge_Temperature": True},
                "symptom": "Inaccurate discharge temperature leading to incorrect assessment of compressor thermal performance and anomaly detection.",
                "symptom_code": "S.S.T + D.S.T"
            },
            {
                "id": "INST-5",
                "probable": "Transmitter Outputs and A-Module Inspection",
                "rca": "Analog output module (A-Module) malfunction causing signal distortion. Power supply issues to transmitters. Common mode interference affecting multiple sensors.",
                "actions": "Inspect A-Module functionality and connections. Check power supply stability. Test signal integrity for all transmitters. Replace faulty modules.",
                "variables": {"Flow_Rate": True, "Suction_Pressure": True, "Discharge_Pressure": True, "Suction_Temperature": True, "Discharge_Temperature": True},
                "symptom": "Multiple sensor readings showing simultaneous anomalies or drift indicating systematic instrumentation issue.",
                "symptom_code": "S.S.F.A + D.S.P.A + D.S.T"
            },
            {
                "id": "INST-6",
                "probable": "Signal A-Proven Tuned Wrongly Indication",
                "rca": "Control system signal processing incorrectly configured. PID tuning parameters causing oscillations or dampened response. Signal filtering inappropriate for process dynamics.",
                "actions": "Review control system configuration and tuning parameters. Verify signal processing algorithms. Re-tune PID controllers. Test control response.",
                "variables": {"Flow_Rate": True, "Discharge_Pressure": True},
                "symptom": "Control system showing oscillating or incorrect process variable values even when physical parameters are stable.",
                "symptom_code": "S.S.F.A + D.S.P.A + D"
            },
            {
                "id": "INST-7",
                "probable": "Process Control (LIC/SV/PCV) Dysfunction",
                "rca": "Level/flow/pressure control valve malfunction. Actuator failure or sticking. Control valve sizing issues. Positioner calibration drift.",
                "actions": "Inspect control valve operation and stroke testing. Check actuator air supply and functionality. Verify positioner calibration. Service or replace valve.",
                "variables": {"Flow_Rate": True, "Suction_Pressure": True, "Discharge_Pressure": True},
                "symptom": "Process control instability with flow and pressure variations not matching setpoints or expected performance.",
                "symptom_code": "S.S.F.A + D.S.P.A + MAE:↑"
            },
            {
                "id": "INST-8",
                "probable": "Control Valve Actuator & A-Pressure Check",
                "rca": "Pneumatic actuator air supply issues. Diaphragm or piston leakage. Air pressure regulator malfunction. Contaminated instrument air.",
                "actions": "Check instrument air pressure and quality. Inspect actuator for leaks. Test valve stroking speed and response. Clean or replace actuator components.",
                "variables": {"Flow_Rate": True, "Discharge_Pressure": True},
                "symptom": "Sluggish control valve response or inability to maintain position causing flow and pressure control issues.",
                "symptom_code": "S.S.F.A + D.S.P.A + D.S.T"
            },
        ]
    },

    "PROCESS": {
        "division_code": 390,
        "color": "#FFF2CC",  # Yellow/beige
        "scenarios": [
            {
                "id": "PROC-0",
                "probable": "Gas Composition & Specific Gravity Review",
                "rca": "Changes in gas composition affecting compressor performance. Specific gravity variation impacting pressure ratios and efficiency. Presence of condensables or contaminants.",
                "actions": "Obtain gas chromatography analysis. Review upstream process changes. Calculate impact on compressor performance. Adjust operating parameters if needed.",
                "variables": {"Flow_Rate": True, "Discharge_Pressure": True, "Discharge_Temperature": True},
                "symptom": "Unexpected performance degradation with unusual pressure/temperature profiles not explained by mechanical issues.",
                "symptom_code": "S.S.F.A + D.S.P.A + D.S.T + MAE:↑"
            },
            {
                "id": "PROC-1",
                "probable": "Surge & Overspeed Risk Analysis",
                "rca": "Operating near surge line due to reduced flow or excessive pressure ratio. Anti-surge valve malfunction. Discharge throttling causing flow restriction.",
                "actions": "Review compressor map and current operating point. Check anti-surge system functionality. Verify discharge conditions. Adjust flow/pressure to safe operating range.",
                "variables": {"Flow_Rate": True, "Discharge_Pressure": True, "Suction_Pressure": True},
                "symptom": "Compressor operating in unstable region with potential for surge, showing flow pulsations and pressure fluctuations.",
                "symptom_code": "S.S.F.A + D.S.P.A + MAE:↑"
            },
            {
                "id": "PROC-2",
                "probable": "Fouler Gas Preparation Check",
                "rca": "Inadequate gas preparation upstream causing contaminant entry. Separator malfunction allowing liquid carryover. Filter inefficiency.",
                "actions": "Inspect upstream separators and filters. Check separator liquid levels and dump valve operation. Verify filter differential pressure. Clean/replace as needed.",
                "variables": {"Flow_Rate": True, "Suction_Pressure": True, "Suction_Temperature": True},
                "symptom": "Gradual performance degradation with evidence of liquid or solid contaminants in gas stream.",
                "symptom_code": "S.S.F.A + D.S.P.A"
            },
            {
                "id": "PROC-3",
                "probable": "Filter Valve Leak/Alignment",
                "rca": "Inlet filter isolation valves leaking or misaligned. Filter element breakthrough. Bypass line not fully closed.",
                "actions": "Inspect filter housing and valves for leaks. Check valve position indication vs actual position. Test filter element integrity. Repair/replace leaking valves.",
                "variables": {"Flow_Rate": True, "Suction_Pressure": True},
                "symptom": "Unexpected flow variations or contamination downstream of filters indicating filter system bypass or failure.",
                "symptom_code": "S.S.F.A + D.S.P.A + MAE:↑"
            },
            {
                "id": "PROC-4",
                "probable": "Liquid Carry-Over Investigation",
                "rca": "Liquid slugs entering compressor from separator upset. High liquid level in suction separator. Separator internals damaged.",
                "actions": "Check separator operation and level control. Inspect separator internals for damage. Verify dump valve functionality. Review upstream conditions causing liquid formation.",
                "variables": {"Suction_Pressure": True, "Suction_Temperature": True, "Discharge_Temperature": True},
                "symptom": "Sudden pressure/temperature spikes or drops indicating liquid ingestion causing abnormal compression behavior.",
                "symptom_code": "S.S.P + PRE:S.A.A"
            },
            {
                "id": "PROC-5",
                "probable": "Cooler Oil System Inspection",
                "rca": "Aftercooler/intercooler fouling reducing heat transfer. Cooling water flow restriction. Tube leakage allowing water contamination.",
                "actions": "Inspect cooler for fouling on gas and water sides. Check cooling water flow and temperature. Test for tube leaks. Clean or repair cooler.",
                "variables": {"Discharge_Temperature": True, "Suction_Temperature": True},
                "symptom": "Elevated discharge temperature with reduced cooling efficiency indicating heat exchanger performance degradation.",
                "symptom_code": "D.S.T + PRE:S.A.S"
            },
        ]
    },

    "MECHANICAL": {
        "division_code": 440,
        "color": "#DDEBF7",  # Light blue
        "scenarios": [
            {
                "id": "MECH-0",
                "probable": "Piping Integrity & Support Inspection",
                "rca": "Piping stress or vibration causing mechanical integrity issues. Support failure leading to misalignment. Thermal expansion not properly accommodated.",
                "actions": "Inspect piping supports and hangers. Check for vibration and stress. Verify expansion joints. Perform stress analysis if needed. Repair/reinforce supports.",
                "variables": {"Suction_Pressure": True, "Discharge_Pressure": True},
                "symptom": "Unusual vibrations, pressure fluctuations, or mechanical noise indicating piping system issues affecting compressor.",
                "symptom_code": "S.S.F.A + PRE:S.A + MAE:↑"
            },
            {
                "id": "MECH-1",
                "probable": "Compressor Internal Seals/IMP Evaluation",
                "rca": "Internal seal wear causing gas recirculation between stages. Impeller damage or erosion. Clearance increase due to wear.",
                "actions": "Monitor efficiency trends. Check for unusual temperature patterns between stages. Schedule inspection during turnaround. Consider online cleaning if applicable.",
                "variables": {"Flow_Rate": True, "Discharge_Pressure": True, "Discharge_Temperature": True},
                "symptom": "Reduced efficiency, lower discharge pressure for given flow, elevated temperatures indicating internal gas recirculation.",
                "symptom_code": "S.S.F.A + PRE:S.A"
            },
            {
                "id": "MECH-2",
                "probable": "Discharge Intake and HRD Lubrication",
                "rca": "Lubrication system malfunction affecting bearings. Oil contamination or degradation. Inadequate oil flow or pressure.",
                "actions": "Check lube oil pressure, temperature, and flow. Analyze oil sample for contamination/degradation. Inspect lube oil filters. Service lubrication system.",
                "variables": {"Discharge_Temperature": True},
                "symptom": "Elevated bearing temperatures, unusual vibration patterns, or oil pressure/temperature anomalies.",
                "symptom_code": "D.S.T + PRE:S.A.S"
            },
            {
                "id": "MECH-3",
                "probable": "Gas Cooler Physical Inspection",
                "rca": "Cooler tube fouling or scaling. Fin damage reducing heat transfer. Tube leakage. Air flow blockage on air-cooled units.",
                "actions": "Perform visual inspection of cooler. Check heat transfer performance. Test for leaks. Clean cooler internals and externals. Repair damaged components.",
                "variables": {"Discharge_Temperature": True, "Suction_Temperature": True},
                "symptom": "Poor cooling performance with high outlet temperatures and low temperature drop across cooler.",
                "symptom_code": "D.S.T + PRE:S.A.P"
            },
            {
                "id": "MECH-4",
                "probable": "Suction Strainer Check",
                "rca": "Suction strainer plugging with debris. High differential pressure across strainer. Damaged strainer element allowing debris passage.",
                "actions": "Check differential pressure across strainer. Inspect and clean strainer element. Check for debris accumulation. Replace damaged elements.",
                "variables": {"Flow_Rate": True, "Suction_Pressure": True},
                "symptom": "Reduced flow with abnormally low suction pressure indicating flow restriction at compressor inlet.",
                "symptom_code": "S.S.F.A + D.S.P.A + PRE:S.A.P"
            },
            {
                "id": "MECH-5",
                "probable": "Compressor & Motor Bearing Temperature Check",
                "rca": "Bearing wear or damage. Inadequate lubrication. Misalignment between driver and compressor. Excessive vibration.",
                "actions": "Monitor bearing temperatures continuously. Check vibration levels. Verify alignment. Inspect lubrication system. Schedule bearing inspection/replacement.",
                "variables": {"Discharge_Temperature": True, "Suction_Temperature": True},
                "symptom": "Abnormal bearing temperatures indicating mechanical problems that could lead to catastrophic failure.",
                "symptom_code": "S.S.F.A + D.S.P.A + D.S.T + PRE:S.A + D.S.T"
            },
        ]
    },

    "ELECTRICAL": {
        "division_code": 525,
        "color": "#DDEBF7",  # Light blue
        "scenarios": [
            {
                "id": "ELEC-0",
                "probable": "Gearbox & Gearbox Inspection",
                "rca": "Gearbox wear or damage. Gear tooth damage. Bearing failure in gearbox. Lubrication issues specific to gearbox.",
                "actions": "Monitor gearbox vibration and temperature. Check lube oil condition. Perform vibration analysis. Inspect gearbox during maintenance window.",
                "variables": {"Discharge_Temperature": True},
                "symptom": "Unusual vibration patterns or temperature rises in gearbox area indicating mechanical degradation.",
                "symptom_code": "S.S.F.A + PRE:S.A.P + MAE:↑"
            },
            {
                "id": "ELEC-1",
                "probable": "Aux-in-Drive Silicone Cleaning & Voltage Isolation",
                "rca": "Auxiliary drive system contamination. Insulation degradation. Voltage irregularities affecting motor control.",
                "actions": "Clean silicone components in drive system. Check insulation resistance. Verify voltage levels and stability. Test isolation barriers.",
                "variables": {"Flow_Rate": True, "Discharge_Pressure": True},
                "symptom": "Erratic motor behavior or control issues potentially affecting compressor speed and performance.",
                "symptom_code": "S.S.F.A + D.S.P.A"
            },
            {
                "id": "ELEC-2",
                "probable": "Variable Speed Drive (VSD) / Inverter Inspection",
                "rca": "VSD malfunction causing speed control issues. Inverter component failure. Harmonic distortion. Cooling fan failure in VSD.",
                "actions": "Inspect VSD for error codes and alarms. Check cooling system. Verify output frequency and voltage. Test harmonic levels. Service or replace faulty components.",
                "variables": {"Flow_Rate": True, "Discharge_Pressure": True, "Discharge_Temperature": True},
                "symptom": "Speed variations, flow instability, or motor performance issues traced to variable speed drive problems.",
                "symptom_code": "S.S.F.A + D.S.P.A + D.S.T + MAE:↑ + MMSCFD: PRE:S.A.P+D.S.T"
            },
            {
                "id": "ELEC-3",
                "probable": "Motor Winding Temperature Check",
                "rca": "Motor winding overheating due to overload. Cooling system failure. Winding insulation degradation. Phase imbalance.",
                "actions": "Monitor motor winding temperatures via RTDs. Check motor load vs rated capacity. Verify cooling system operation. Test insulation resistance. Balance phases.",
                "variables": {"Discharge_Temperature": True},
                "symptom": "Elevated motor temperatures indicating electrical or cooling problems that could lead to motor failure.",
                "symptom_code": "S.S.F.A + PRE:S.A.P + MAE:↑"
            },
        ]
    },

    "RELATIONAL": {
        "division_code": 225,
        "color": "#F4CCCC",  # Pink/red
        "scenarios": [
            {
                "id": "REL-0",
                "probable": "Hydraulic Unit & Anti-ning Review",
                "rca": "Hydraulic control system malfunction. Anti-surge valve control issues. Hydraulic fluid contamination or low level.",
                "actions": "Check hydraulic fluid level and pressure. Inspect anti-surge valve operation. Test hydraulic pump performance. Service hydraulic system.",
                "variables": {"Flow_Rate": True, "Discharge_Pressure": True},
                "symptom": "Control system instability or anti-surge protection not functioning properly affecting safe operation.",
                "symptom_code": "S.S.F.A + PRE:S.A.P + MAE:↑"
            },
            {
                "id": "REL-1",
                "probable": "PSV Control Loop Tuning",
                "rca": "Pressure safety valve control loop poorly tuned. Relief valve chatter. Setpoint drift.",
                "actions": "Review PSV settings and operation. Re-tune control loop parameters. Test PSV operation. Verify setpoints match design requirements.",
                "variables": {"Discharge_Pressure": True},
                "symptom": "Pressure control instability or relief valve issues indicating need for control system optimization.",
                "symptom_code": "S.S.F.A + D.S.P.A"
            },
            {
                "id": "REL-2",
                "probable": "Turbo Lubericas & Anti-Syrg Installation",
                "rca": "Lube oil system malfunction affecting turbomachinery. Anti-surge system installation issues.",
                "actions": "Inspect lube oil system for proper operation. Verify anti-surge system installation and calibration. Test protective systems.",
                "variables": {"Flow_Rate": True, "Discharge_Pressure": True, "Discharge_Temperature": True},
                "symptom": "Protection system concerns or lubrication issues affecting safe and reliable compressor operation.",
                "symptom_code": "S.S.F.A + D.S.P.A + D.S.T"
            },
        ]
    },
}


def get_applicable_rca_scenarios(row, top_n=10):
    """
    Determine which RCA scenarios apply to an anomaly based on sensor deviations.

    Parameters:
        row: Anomaly data row with sensor values and rule classifications
        top_n: Maximum number of scenarios to return

    Returns:
        List of applicable RCA scenario dictionaries
    """
    from rule_engine import get_non_normal_rules, classify_row, THRESHOLDS

    # Check if row has rule classifications, if not compute them
    import pandas as pd
    has_rules = any(col.endswith('_rule') for col in row.index if isinstance(row.index, pd.Index))

    if not has_rules:
        # Compute rule classifications on the fly
        for param, bounds in THRESHOLDS.items():
            if param in row.index:
                val = row[param]
                if pd.notna(val):
                    if isinstance(val, str):
                        val = float(val.replace('%', '').replace(',', ''))
                    if val > bounds["high"]:
                        row = row.copy()
                        row[f"{param}_rule"] = "HIGH"
                    elif val < bounds["low"]:
                        row = row.copy()
                        row[f"{param}_rule"] = "LOW"
                    else:
                        row = row.copy()
                        row[f"{param}_rule"] = "NORMAL"

    # Get which sensors are abnormal
    abnormal_sensors = get_non_normal_rules(row)

    applicable_scenarios = []

    # Scan all divisions
    for division_name, division_data in RCA_DATABASE.items():
        for scenario in division_data["scenarios"]:
            # Check if scenario variables match abnormal sensors
            scenario_vars = scenario["variables"]

            # Count how many abnormal sensors this scenario addresses
            match_score = 0
            for sensor, is_relevant in scenario_vars.items():
                if is_relevant and sensor in abnormal_sensors:
                    match_score += 1

            # If scenario addresses at least one abnormal sensor, include it
            if match_score > 0:
                applicable_scenarios.append({
                    **scenario,
                    "division": division_name,
                    "division_code": division_data["division_code"],
                    "color": division_data["color"],
                    "match_score": match_score,
                    "abnormal_sensors": abnormal_sensors
                })

    # Sort by match score (scenarios addressing more abnormal sensors rank higher)
    applicable_scenarios.sort(key=lambda x: x["match_score"], reverse=True)

    return applicable_scenarios[:top_n]


def get_division_summary(applicable_scenarios):
    """
    Summarize which divisions are impacted.

    Returns:
        Dictionary of division_name -> count of applicable scenarios
    """
    division_counts = {}
    for scenario in applicable_scenarios:
        div = scenario["division"]
        division_counts[div] = division_counts.get(div, 0) + 1
    return division_counts
