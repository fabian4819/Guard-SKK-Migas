// RCA Knowledge Base from "RCA FOR RULE BASED - Sheet1.pdf"
// 32 scenarios across 4 divisions: INSTRUMENT, PROCESS, MECHANICAL, ELECTRICAL

export interface RCAScenario {
  id: string;
  division: string;
  division_code: number;
  color: string;
  prob: string;
  variable: string;
  rca: string;
  actions: string;
  Flow_Rate: boolean;
  Suction_Pressure: boolean;
  Discharge_Pressure: boolean;
  Suction_Temperature: boolean;
  Discharge_Temperature: boolean;
  symptom: string;
  timeToSolve: string;
}

export const rcaKnowledgeBase: RCAScenario[] = [
  // INSTRUMENT Division
  {
    id: 'INS-01',
    division: 'INSTRUMENT',
    division_code: 305,
    color: '#DDEBF7',
    prob: '1',
    variable: 'Flow Transmitter (FT) Malfunction or Calibration',
    rca: 'Faulty or miscalibrated flow transmitter leading to inaccurate flow readings',
    actions: 'Inspect and recalibrate or replace flow transmitter; verify signal integrity',
    Flow_Rate: true,
    Suction_Pressure: false,
    Discharge_Pressure: false,
    Suction_Temperature: false,
    Discharge_Temperature: false,
    symptom: 'Abnormal flow readings; erratic or incorrect flow measurements',
    timeToSolve: '2 to 4 H'
  },
  {
    id: 'INS-02',
    division: 'INSTRUMENT',
    prob: '2',
    variable: 'Suction Pressure Transmitter (PT) Dysfunction',
    rca: 'PT failure causing inaccurate suction pressure data',
    actions: 'Test and recalibrate PT; replace if faulty',
    Flow_Rate: false,
    Suction_Pressure: true,
    Discharge_Pressure: false,
    Suction_Temperature: false,
    Discharge_Temperature: false,
    symptom: 'Incorrect suction pressure readings affecting compressor monitoring',
    timeToSolve: '1 to 3 H (DEG.1 to 4)'
  },
  {
    id: 'INS-03',
    division: 'INSTRUMENT',
    prob: '3',
    variable: 'Discharge Pressure Transmitter (PT) Malfunction',
    rca: 'Faulty discharge PT causing incorrect pressure readings',
    actions: 'Inspect, calibrate, or replace discharge PT',
    Flow_Rate: false,
    Suction_Pressure: false,
    Discharge_Pressure: true,
    Suction_Temperature: false,
    Discharge_Temperature: false,
    symptom: 'Abnormal discharge pressure values affecting system control',
    timeToSolve: '1 to 3 H (DEG.2, 3, 6 to 7)'
  },
  {
    id: 'INS-04',
    division: 'INSTRUMENT',
    prob: '4',
    variable: 'Suction Temperature Transmitter (TT) Malfunction',
    rca: 'TT failure or calibration issue affecting temperature readings',
    actions: 'Check TT sensor; recalibrate or replace if needed',
    Flow_Rate: false,
    Suction_Pressure: false,
    Discharge_Pressure: false,
    Suction_Temperature: true,
    Discharge_Temperature: false,
    symptom: 'Inaccurate suction temperature data affecting thermal monitoring',
    timeToSolve: '1 to 2 H (DEG.1 to 7, MAX.2-3)'
  },

  // PROCESS Division
  {
    id: 'PRO-01',
    division: 'PROCESS',
    prob: '1',
    variable: 'Compressor Valve (ACHP) Actuator',
    rca: 'Faulty actuator affecting valve operation and flow control',
    actions: 'Inspect and service actuator; verify valve movement',
    Flow_Rate: true,
    Suction_Pressure: true,
    Discharge_Pressure: false,
    Suction_Temperature: false,
    Discharge_Temperature: true,
    symptom: 'Erratic valve operation affecting system flow',
    timeToSolve: '1 to 4 H (DEG.1 to 7)'
  },
  {
    id: 'PRO-02',
    division: 'PROCESS',
    prob: '2',
    variable: 'Gas Cooler / Heat Exchanger Efficiency',
    rca: 'Fouling or reduced heat transfer in cooler/exchanger',
    actions: 'Clean heat exchanger; check cooling water flow',
    Flow_Rate: false,
    Suction_Pressure: false,
    Discharge_Pressure: false,
    Suction_Temperature: false,
    Discharge_Temperature: true,
    symptom: 'Elevated discharge temperature; reduced cooling efficiency',
    timeToSolve: '2 to 4 H (DEG.4, 5 to 6)'
  },
  {
    id: 'PRO-03',
    division: 'PROCESS',
    prob: '3',
    variable: 'Downstream Filter/Valve Malfunction',
    rca: 'Blocked or malfunctioning filter causing flow restriction',
    actions: 'Clean or replace filter; inspect downstream valves',
    Flow_Rate: true,
    Suction_Pressure: false,
    Discharge_Pressure: true,
    Suction_Temperature: false,
    Discharge_Temperature: false,
    symptom: 'Reduced flow; increased pressure drop',
    timeToSolve: '2 to 4 H (DEG.1 to 4, 6 to 7)'
  },
  {
    id: 'PRO-04',
    division: 'PROCESS',
    prob: '4',
    variable: 'Anti-Surge Control Valve Stuck',
    rca: 'ASV stuck affecting surge protection and flow',
    actions: 'Inspect ASV actuator and valve; verify control signal',
    Flow_Rate: true,
    Suction_Pressure: true,
    Discharge_Pressure: true,
    Suction_Temperature: false,
    Discharge_Temperature: false,
    symptom: 'Flow instability; surge risk',
    timeToSolve: '2 to 3 H (DEG.1 to 7)'
  },
  {
    id: 'PRO-05',
    division: 'PROCESS',
    prob: '5',
    variable: 'Gas Condensate & Impurity Density Builds',
    rca: 'Condensate accumulation affecting flow and efficiency',
    actions: 'Drain condensate; clean separator/scrubber',
    Flow_Rate: true,
    Suction_Pressure: true,
    Discharge_Pressure: false,
    Suction_Temperature: false,
    Discharge_Temperature: false,
    symptom: 'Reduced flow; liquid carryover',
    timeToSolve: '2 to 4 H (1,4, DEG.1,4, 6 to 7)'
  },
  {
    id: 'PRO-06',
    division: 'PROCESS',
    prob: '6',
    variable: 'Suction & Scrubber Leak Analysis',
    rca: 'Leak in suction system reducing pressure',
    actions: 'Locate and repair leak; pressure test system',
    Flow_Rate: true,
    Suction_Pressure: true,
    Discharge_Pressure: false,
    Suction_Temperature: false,
    Discharge_Temperature: false,
    symptom: 'Low suction pressure; reduced flow',
    timeToSolve: '3 to 5 H (DEG.1 to 7)'
  },
  {
    id: 'PRO-07',
    division: 'PROCESS',
    prob: '7',
    variable: 'Lube-Gas Temperature Check',
    rca: 'Abnormal lube gas temperature affecting lubrication',
    actions: 'Check lube oil cooler; verify temperature control',
    Flow_Rate: false,
    Suction_Pressure: false,
    Discharge_Pressure: false,
    Suction_Temperature: true,
    Discharge_Temperature: true,
    symptom: 'Temperature anomaly in lubrication system',
    timeToSolve: '2 to 6 H (DEG.1 to 7, MAX.1, 2,3,5,6,7)'
  },

  // MECHANICAL Division
  {
    id: 'MEC-01',
    division: 'MECHANICAL',
    prob: '1',
    variable: 'Compressor Internal (Impeller/Diffuser) Evaluation',
    rca: 'Impeller wear or damage reducing compression efficiency',
    actions: 'Inspect impeller and diffuser; replace if damaged',
    Flow_Rate: true,
    Suction_Pressure: false,
    Discharge_Pressure: true,
    Suction_Temperature: false,
    Discharge_Temperature: true,
    symptom: 'Reduced flow and pressure; increased temperature',
    timeToSolve: '3 to 5 H (DEG.1 to 4)'
  },
  {
    id: 'MEC-02',
    division: 'MECHANICAL',
    prob: '2',
    variable: 'Discharge Piston/Valve (APV) Inspection',
    rca: 'Faulty piston or valve affecting discharge performance',
    actions: 'Inspect and service piston/valve assembly',
    Flow_Rate: false,
    Suction_Pressure: false,
    Discharge_Pressure: true,
    Suction_Temperature: false,
    Discharge_Temperature: false,
    symptom: 'Discharge pressure issues',
    timeToSolve: '4 to 6 H (DEG.1,2,7)'
  },
  {
    id: 'MEC-03',
    division: 'MECHANICAL',
    prob: '3',
    variable: 'Gas Seals/Physical Inspection',
    rca: 'Seal leakage causing pressure loss',
    actions: 'Inspect seals; replace if worn or damaged',
    Flow_Rate: false,
    Suction_Pressure: true,
    Discharge_Pressure: false,
    Suction_Temperature: false,
    Discharge_Temperature: false,
    symptom: 'Pressure drop; gas leakage',
    timeToSolve: '4 to 5 H (DEG.1,2,7)'
  },
  {
    id: 'MEC-04',
    division: 'MECHANICAL',
    prob: '4',
    variable: 'Suction Strainer Check',
    rca: 'Clogged strainer restricting flow',
    actions: 'Clean or replace suction strainer',
    Flow_Rate: true,
    Suction_Pressure: true,
    Discharge_Pressure: false,
    Suction_Temperature: false,
    Discharge_Temperature: false,
    symptom: 'Reduced flow; low suction pressure',
    timeToSolve: '2 to 4 H (DEG.1,2,7)'
  },
  {
    id: 'MEC-05',
    division: 'MECHANICAL',
    prob: '5',
    variable: 'Compressor & Motor Bearings Temperature Check',
    rca: 'Bearing wear causing temperature rise',
    actions: 'Inspect bearings; check lubrication; replace if needed',
    Flow_Rate: false,
    Suction_Pressure: false,
    Discharge_Pressure: false,
    Suction_Temperature: true,
    Discharge_Temperature: true,
    symptom: 'High bearing temperature; vibration',
    timeToSolve: '5 to 7 H (DEG.1,2,3, 5 to 7, G.D.1)'
  },

  // ELECTRICAL Division
  {
    id: 'ELE-01',
    division: 'ELECTRICAL',
    prob: '1',
    variable: 'Coupling & Gearbox Inspection',
    rca: 'Coupling misalignment or gearbox issue',
    actions: 'Inspect coupling alignment and gearbox condition',
    Flow_Rate: false,
    Suction_Pressure: true,
    Discharge_Pressure: false,
    Suction_Temperature: true,
    Discharge_Temperature: false,
    symptom: 'Vibration; abnormal noise',
    timeToSolve: '2 to 4 H (DEG.1 to 6, MAX.2)'
  },
  {
    id: 'ELE-02',
    division: 'ELECTRICAL',
    prob: '2',
    variable: 'Main Drive Motor Current & Voltage Evaluation',
    rca: 'Abnormal motor current or voltage affecting performance',
    actions: 'Check motor electrical parameters; inspect connections',
    Flow_Rate: false,
    Suction_Pressure: true,
    Discharge_Pressure: false,
    Suction_Temperature: false,
    Discharge_Temperature: true,
    symptom: 'Motor current/voltage anomaly; performance issues',
    timeToSolve: '3 to 5 H (DEG.1 to 4, 6, MAX.2,3)'
  },
  {
    id: 'ELE-03',
    division: 'ELECTRICAL',
    prob: '3',
    variable: 'Variable Speed Drive (VSD) / Inverter Inspection',
    rca: 'VSD malfunction affecting speed control',
    actions: 'Inspect VSD; check control signals and settings',
    Flow_Rate: true,
    Suction_Pressure: true,
    Discharge_Pressure: true,
    Suction_Temperature: false,
    Discharge_Temperature: true,
    symptom: 'Speed control issues; erratic operation',
    timeToSolve: '2 to 4 H (1,2,3, DEG.1 to 7, MAX.1,2,3,5,7)'
  },
  {
    id: 'ELE-04',
    division: 'ELECTRICAL',
    prob: '4',
    variable: 'Motor Winding Temperature Check',
    rca: 'High motor winding temperature indicating overload or cooling issue',
    actions: 'Check motor load; inspect cooling system; verify insulation',
    Flow_Rate: false,
    Suction_Pressure: false,
    Discharge_Pressure: false,
    Suction_Temperature: true,
    Discharge_Temperature: true,
    symptom: 'Motor overheating; reduced efficiency',
    timeToSolve: '3 to 6 H (MAX.1,2,5,6)'
  }
];

/**
 * Get applicable RCA scenarios based on abnormal sensor variables
 */
export function getApplicableRcaScenarios(sensorData: any, topN: number = 5): RCAScenario[] {
  const sensors = {
    Flow_Rate: { low: 45, high: 56 },
    Suction_Pressure: { low: 33, high: 34 },
    Discharge_Pressure: { low: 60, high: 63.3 },
    Suction_Temperature: { low: 90, high: 100 },
    Discharge_Temperature: { low: 189, high: 205 },
  };

  // Determine which variables are abnormal
  const abnormalVars = {
    Flow_Rate: sensorData.Flow_Rate < sensors.Flow_Rate.low || sensorData.Flow_Rate > sensors.Flow_Rate.high,
    Suction_Pressure: sensorData.Suction_Pressure < sensors.Suction_Pressure.low || sensorData.Suction_Pressure > sensors.Suction_Pressure.high,
    Discharge_Pressure: sensorData.Discharge_Pressure < sensors.Discharge_Pressure.low || sensorData.Discharge_Pressure > sensors.Discharge_Pressure.high,
    Suction_Temperature: sensorData.Suction_Temperature < sensors.Suction_Temperature.low || sensorData.Suction_Temperature > sensors.Suction_Temperature.high,
    Discharge_Temperature: sensorData.Discharge_Temperature < sensors.Discharge_Temperature.low || sensorData.Discharge_Temperature > sensors.Discharge_Temperature.high,
  };

  // Score each RCA scenario based on matching variables
  const scoredScenarios = rcaKnowledgeBase.map(scenario => {
    let matchScore = 0;

    // High weight for matching abnormal variables
    if (scenario.Flow_Rate && abnormalVars.Flow_Rate) matchScore += 3;
    if (scenario.Suction_Pressure && abnormalVars.Suction_Pressure) matchScore += 3;
    if (scenario.Discharge_Pressure && abnormalVars.Discharge_Pressure) matchScore += 3;
    if (scenario.Suction_Temperature && abnormalVars.Suction_Temperature) matchScore += 3;
    if (scenario.Discharge_Temperature && abnormalVars.Discharge_Temperature) matchScore += 3;

    return { ...scenario, matchScore };
  });

  // Sort by match score (highest first) and return top N
  return scoredScenarios
    .filter(s => s.matchScore > 0) // Only return scenarios with at least one match
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, topN);
}
