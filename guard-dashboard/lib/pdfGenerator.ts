import type { TDocumentDefinitions } from 'pdfmake/interfaces';
import { getApplicableRcaScenarios, type RCAScenario } from './rcaKnowledgeBase';

interface SensorData {
  datetime: string;
  Flow_Rate: number;
  Suction_Pressure: number;
  Discharge_Pressure: number;
  Suction_Temperature: number;
  Discharge_Temperature: number;
  threshold_ratio: number;
  status: string;
  [key: string]: any;
}

const SENSOR_CONFIG = {
  Flow_Rate: { low: 45, high: 56, unit: 'MMSCFD', tag: 'FT-001' },
  Suction_Pressure: { low: 33, high: 34, unit: 'bar', tag: 'PT-001' },
  Discharge_Pressure: { low: 60, high: 63.3, unit: 'bar', tag: 'PT-002' },
  Suction_Temperature: { low: 90, high: 100, unit: '°C', tag: 'TT-001' },
  Discharge_Temperature: { low: 189, high: 205, unit: '°C', tag: 'TT-002' },
};

function getTopContributors(row: SensorData, topN: number = 5) {
  const contributors = [];

  for (const [key, config] of Object.entries(SENSOR_CONFIG)) {
    const value = row[key];
    if (value === undefined) continue;

    const range = config.high - config.low;
    const expected = (config.high + config.low) / 2;
    const deviation = value - expected;
    const deviationPct = (deviation / expected) * 100;

    // Contribution logic
    let contribution = 0;
    if (value < config.low || value > config.high) {
      const deviationMultiple = Math.abs(value < config.low ?
        (value - config.low) / range :
        (value - config.high) / range);
      contribution = deviationMultiple * 30;
    }

    contributors.push({
      variable: key,
      tag: config.tag,
      value,
      expected,
      deviation,
      deviation_pct: deviationPct,
      contribution,
      unit: config.unit,
    });
  }

  contributors.sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));
  return contributors.slice(0, topN);
}

export function generateRCAPDF(anomalyData: SensorData): TDocumentDefinitions {
  const timestamp = new Date(anomalyData.datetime);
  const timestampStr = timestamp.toLocaleDateString('en-US', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });

  // Get top contributors
  const contributors = getTopContributors(anomalyData, 5);

  // Get RCA scenarios
  const scenarios = getApplicableRcaScenarios(anomalyData, 8);

  // Build sensor table
  const sensorTableBody = [
    [
      { text: 'VARIABLE', style: 'tableHeader' },
      { text: 'TAG', style: 'tableHeader' },
      { text: 'ACTUAL\nVALUE', style: 'tableHeader' },
      { text: 'EXPECTED\nVALUE', style: 'tableHeader' },
      { text: 'DEVIATION', style: 'tableHeader' },
      { text: 'DEVIATION\n%', style: 'tableHeader' },
      { text: 'LOSS\nCONTRIBUTION', style: 'tableHeader' },
      { text: 'ABNORMALITY', style: 'tableHeader' },
    ],
  ];

  contributors.forEach((c) => {
    const config = SENSOR_CONFIG[c.variable as keyof typeof SENSOR_CONFIG];
    const isOutOfRange = c.value < config.low || c.value > config.high;
    const isSignificantDeviation = Math.abs(c.deviation_pct) > 2.0;
    const hasHighContribution = c.contribution > 20.0;
    const abnormality = (isOutOfRange || isSignificantDeviation || hasHighContribution) ? 'YES' : 'NO';

    sensorTableBody.push([
      { text: c.variable.replace(/_/g, ' '), style: 'tableCell' },
      { text: c.tag, style: 'tableCell' },
      { text: c.value.toFixed(2), style: 'tableCellRight' },
      { text: c.expected.toFixed(2), style: 'tableCellRight' },
      { text: c.deviation.toFixed(2), style: 'tableCellRight' },
      { text: `${c.deviation_pct >= 0 ? '+' : ''}${c.deviation_pct.toFixed(1)}%`, style: 'tableCellRight' },
      { text: `${c.contribution.toFixed(1)}%`, style: 'tableCellRight' },
      { text: abnormality, style: 'tableCellCenter' },
    ]);
  });

  // Build RCA table
  const rcaTableBody: any[] = [
    [
      { text: 'SYMPTOM', style: 'rcaHeader' },
      { text: 'SUB', style: 'rcaHeader' },
      { text: 'PROB', style: 'rcaHeader' },
      { text: 'RCA', style: 'rcaHeader' },
      { text: 'ACTIONS', style: 'rcaHeader' },
      { text: 'Flow\nRate', style: 'rcaHeader', fontSize: 7 },
      { text: 'Suction\nPress', style: 'rcaHeader', fontSize: 7 },
      { text: 'Discharge\nPress', style: 'rcaHeader', fontSize: 7 },
      { text: 'Suction\nTemp', style: 'rcaHeader', fontSize: 7 },
      { text: 'Discharge\nTemp', style: 'rcaHeader', fontSize: 7 },
      { text: 'SYMPTOM', style: 'rcaHeader' },
    ],
  ];

  // Group scenarios by division
  const divisionGroups: { [key: string]: RCAScenario[] } = {};
  scenarios.forEach(s => {
    if (!divisionGroups[s.division]) divisionGroups[s.division] = [];
    divisionGroups[s.division].push(s);
  });

  const divisionOrder = ['INSTRUMENT', 'PROCESS', 'MECHANICAL', 'ELECTRICAL'];

  divisionOrder.forEach(divName => {
    const divScenarios = divisionGroups[divName];
    if (!divScenarios || divScenarios.length === 0) return;

    divScenarios.forEach((scenario, idx) => {
      rcaTableBody.push([
        { text: idx === 0 ? divName : '', style: 'rcaCell', fillColor: scenario.color },
        { text: idx === 0 ? scenario.division_code : '', style: 'rcaCellCenter', fillColor: scenario.color },
        { text: scenario.prob, style: 'rcaCellCenter', fillColor: scenario.color },
        { text: scenario.rca, style: 'rcaCell', fontSize: 6, fillColor: scenario.color },
        { text: scenario.actions, style: 'rcaCell', fontSize: 6, fillColor: scenario.color },
        { text: scenario.Flow_Rate ? 'YES' : 'NO', style: 'rcaCellCenter', fillColor: scenario.color },
        { text: scenario.Suction_Pressure ? 'YES' : 'NO', style: 'rcaCellCenter', fillColor: scenario.color },
        { text: scenario.Discharge_Pressure ? 'YES' : 'NO', style: 'rcaCellCenter', fillColor: scenario.color },
        { text: scenario.Suction_Temperature ? 'YES' : 'NO', style: 'rcaCellCenter', fillColor: scenario.color },
        { text: scenario.Discharge_Temperature ? 'YES' : 'NO', style: 'rcaCellCenter', fillColor: scenario.color },
        { text: scenario.symptom, style: 'rcaCell', fontSize: 6, fillColor: scenario.color },
      ]);
    });
  });

  // Add summary row
  const thresholdRatio = anomalyData.threshold_ratio || 0;
  const exceedPercent = thresholdRatio - 100;

  rcaTableBody.push([
    { text: 'SUMMARY', style: 'summaryCell', colSpan: 3, bold: true },
    {},
    {},
    { text: `Threshold Ratio: ${thresholdRatio.toFixed(1)}% (Exceeds by ${exceedPercent.toFixed(1)}%)`, style: 'summaryCell', colSpan: 8 },
    {}, {}, {}, {}, {}, {}, {},
  ]);

  const docDefinition: TDocumentDefinitions = {
    pageSize: 'A4',
    pageOrientation: 'landscape',
    pageMargins: [20, 30, 20, 30],
    content: [
      {
        text: 'ANOMALY DETECTION BOOSTER COMPRESSOR B CPP DONGGI',
        style: 'title',
        alignment: 'center',
        margin: [0, 0, 0, 10],
      },
      {
        table: {
          widths: [70, 230, 70, 170],
          body: [
            [
              { text: 'Equipment:', bold: true },
              { text: 'BOOSTER COMPRESSOR B CPP DONGGI' },
              { text: 'Timestamp:', bold: true },
              { text: timestampStr },
            ],
            [
              { text: 'Location:', bold: true },
              { text: 'CPP Donggi' },
              { text: '', border: [false, false, false, false] },
              { text: '', border: [false, false, false, false] },
            ],
          ],
        },
        layout: 'noBorders',
        margin: [0, 0, 0, 15],
      },
      {
        table: {
          headerRows: 1,
          widths: [95, 65, 60, 60, 60, 60, 65, 70],
          body: sensorTableBody,
        },
        layout: {
          fillColor: (rowIndex) => (rowIndex === 0 ? '#4472C4' : rowIndex % 2 === 0 ? '#F2F2F2' : null),
        },
        margin: [0, 0, 0, 15],
      },
      {
        table: {
          headerRows: 1,
          widths: [60, 30, 30, 110, 110, 35, 35, 35, 35, 35, 80],
          body: rcaTableBody,
        },
        layout: 'lightHorizontalLines',
      },
    ],
    styles: {
      title: {
        fontSize: 12,
        bold: true,
        color: '#1976d2',
      },
      tableHeader: {
        fontSize: 8,
        bold: true,
        color: 'white',
        fillColor: '#4472C4',
        alignment: 'center',
      },
      tableCell: {
        fontSize: 8,
      },
      tableCellRight: {
        fontSize: 8,
        alignment: 'right',
      },
      tableCellCenter: {
        fontSize: 8,
        alignment: 'center',
      },
      rcaHeader: {
        fontSize: 8,
        bold: true,
        fillColor: '#4472C4',
        color: 'white',
        alignment: 'center',
      },
      rcaCell: {
        fontSize: 7,
      },
      rcaCellCenter: {
        fontSize: 7,
        alignment: 'center',
      },
      summaryCell: {
        fontSize: 8,
        fillColor: '#E7E6E6',
        bold: true,
      },
    },
  };

  return docDefinition;
}
