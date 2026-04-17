'use client';

import { X } from 'lucide-react';
import { SensorData } from '@/types';
import { format } from 'date-fns';
import { getApplicableRcaScenarios } from '@/lib/rcaKnowledgeBase';

interface AnomalyDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  anomalyData: SensorData | null;
}
export default function AnomalyDetailModal({ isOpen, onClose, anomalyData }: AnomalyDetailModalProps) {
  if (!isOpen || !anomalyData) return null;

  const sensors = {
    Flow_Rate: { tag: 'FI1001B', unit: 'MMSCFD', low: 45, high: 56 },
    Suction_Pressure: { tag: 'PI1001B', unit: 'barg', low: 33, high: 34 },
    Discharge_Pressure: { tag: 'PI1004B', unit: 'barg', low: 60, high: 63.3 },
    Suction_Temperature: { tag: 'TI1003B', unit: '°C', low: 90, high: 100 },
    Discharge_Temperature: { tag: 'TI1004B', unit: '°C', low: 189, high: 205 },
  };

  // Get RCA scenarios
  const rcaScenarios = getApplicableRcaScenarios(anomalyData, 5);

  // Build table data
  const tableData = Object.entries(sensors).map(([param, config]) => {
    const actual = anomalyData[param as keyof SensorData] as number;
    const expected = (config.low + config.high) / 2;
    const deviation = actual - expected;
    const deviationPct = (deviation / expected * 100);
    const contribution = Math.abs(deviationPct) * 20; // Simplified calculation

    const isOutsideRange = (actual < config.low) || (actual > config.high);
    const isSignificantDeviation = Math.abs(deviationPct) > 2.0;
    const hasHighContribution = contribution > 20.0;
    const abnormality = (isOutsideRange || isSignificantDeviation || hasHighContribution) ? "YES" : "NO";

    return {
      variable: param.replace(/_/g, ' '),
      tag: config.tag,
      actual: actual.toFixed(2),
      expected: expected.toFixed(2),
      deviation: deviation.toFixed(2),
      deviationPct: deviationPct.toFixed(1),
      contribution: contribution.toFixed(1),
      abnormality,
    };
  });

  const exceedPct = anomalyData.threshold_ratio - 100;
  let status = "CAUTION ⚠️";
  if (anomalyData.threshold_ratio > 150) status = "CRITICAL ⚠️";
  else if (anomalyData.threshold_ratio > 120) status = "WARNING ⚠️";

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#1e3c72] to-[#2a5298] p-6 rounded-t-xl sticky top-0 z-10">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h2 className="text-white text-2xl font-bold mb-2 text-center">
                ANOMALY DETECTION BOOSTER COMPRESSOR B CPP DONGGI
              </h2>
              <p className="text-white text-sm text-center opacity-90">
                {format(new Date(anomalyData.datetime), 'dd MMMM yyyy HH:mm:ss')} | CPP Donggi
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/10 p-2 rounded-lg transition-colors ml-4"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Metrics */}
          <div className="grid grid-cols-3 gap-6">
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Threshold Ratio</p>
              <p className="text-3xl font-bold text-blue-900">{anomalyData.threshold_ratio.toFixed(1)}%</p>
              <p className="text-xs text-red-600 mt-1">+{exceedPct.toFixed(1)}% above threshold</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Exceed Percentage</p>
              <p className="text-3xl font-bold text-orange-600">{exceedPct.toFixed(1)}%</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Asset Integrity Status</p>
              <p className="text-2xl font-bold text-red-600">{status}</p>
            </div>
          </div>

          <div className="border-t border-gray-200"></div>

          {/* Variable Analysis Table */}
          <div>
            <h3 className="text-lg font-bold text-gray-800 mb-4">VARIABLE ANALYSIS - TOP CONTRIBUTORS</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-gray-100 border-b-2 border-gray-300">
                    <th className="px-3 py-3 text-left font-bold text-gray-700 border border-gray-300">VARIABLE</th>
                    <th className="px-3 py-3 text-left font-bold text-gray-700 border border-gray-300">TAG</th>
                    <th className="px-3 py-3 text-center font-bold text-gray-700 border border-gray-300">ACTUAL VALUE</th>
                    <th className="px-3 py-3 text-center font-bold text-gray-700 border border-gray-300">EXPECTED VALUE</th>
                    <th className="px-3 py-3 text-center font-bold text-gray-700 border border-gray-300">DEVIATION</th>
                    <th className="px-3 py-3 text-center font-bold text-gray-700 border border-gray-300">DEVIATION %</th>
                    <th className="px-3 py-3 text-center font-bold text-gray-700 border border-gray-300">LOSS CONTRIBUTION</th>
                    <th className="px-3 py-3 text-center font-bold text-gray-700 border border-gray-300">ABNORMALITY</th>
                  </tr>
                </thead>
                <tbody>
                  {tableData.map((row, idx) => (
                    <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                      <td className="px-3 py-2 border border-gray-300">{row.variable}</td>
                      <td className="px-3 py-2 border border-gray-300 font-mono text-xs">{row.tag}</td>
                      <td className="px-3 py-2 text-center border border-gray-300">{row.actual}</td>
                      <td className="px-3 py-2 text-center border border-gray-300">{row.expected}</td>
                      <td className={`px-3 py-2 text-center border border-gray-300 ${parseFloat(row.deviation) !== 0 ? 'font-semibold' : ''}`}>
                        {row.deviation}
                      </td>
                      <td className={`px-3 py-2 text-center border border-gray-300 ${Math.abs(parseFloat(row.deviationPct)) > 5 ? 'text-red-600 font-bold' : ''}`}>
                        {row.deviationPct}%
                      </td>
                      <td className="px-3 py-2 text-center border border-gray-300">{row.contribution}%</td>
                      <td className={`px-3 py-2 text-center border border-gray-300 font-bold ${row.abnormality === 'YES' ? 'text-red-600' : 'text-green-600'}`}>
                        {row.abnormality}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="border-t border-gray-200"></div>

          {/* RCA Table - Matching dashboard_modern.py */}
          <div>
            <h3 className="text-lg font-bold text-gray-800 mb-4">ROOT CAUSE ANALYSIS - PROBABLE SCENARIOS</h3>
            {rcaScenarios.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="bg-gray-100 border-b-2 border-gray-300">
                      <th className="px-2 py-2 text-left font-bold text-gray-700 border border-gray-300 text-[10px]">DIVISION</th>
                      <th className="px-2 py-2 text-left font-bold text-gray-700 border border-gray-300 text-[10px]">PROB</th>
                      <th className="px-3 py-2 text-left font-bold text-gray-700 border border-gray-300 text-[10px]">RCA</th>
                      <th className="px-3 py-2 text-left font-bold text-gray-700 border border-gray-300 text-[10px]">ACTIONS</th>
                      <th className="px-2 py-2 text-center font-bold text-gray-700 border border-gray-300 text-[10px]">Flow<br/>Rate</th>
                      <th className="px-2 py-2 text-center font-bold text-gray-700 border border-gray-300 text-[10px]">Suction<br/>Press</th>
                      <th className="px-2 py-2 text-center font-bold text-gray-700 border border-gray-300 text-[10px]">Discharge<br/>Press</th>
                      <th className="px-2 py-2 text-center font-bold text-gray-700 border border-gray-300 text-[10px]">Suction<br/>Temp</th>
                      <th className="px-2 py-2 text-center font-bold text-gray-700 border border-gray-300 text-[10px]">Discharge<br/>Temp</th>
                      <th className="px-3 py-2 text-left font-bold text-gray-700 border border-gray-300 text-[10px]">SYMPTOM</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rcaScenarios.map((scenario, idx) => (
                      <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                        <td className="px-2 py-2 border border-gray-300 font-medium text-xs">{scenario.division}</td>
                        <td className="px-2 py-2 border border-gray-300 font-mono text-[10px]">{scenario.prob}</td>
                        <td className="px-3 py-2 border border-gray-300 text-xs">{scenario.rca}</td>
                        <td className="px-3 py-2 border border-gray-300 text-gray-700 text-xs">{scenario.actions}</td>
                        <td className={`px-2 py-2 text-center border border-gray-300 font-bold text-xs ${scenario.Flow_Rate ? 'text-red-600' : 'text-gray-400'}`}>
                          {scenario.Flow_Rate ? 'YES' : 'NO'}
                        </td>
                        <td className={`px-2 py-2 text-center border border-gray-300 font-bold text-xs ${scenario.Suction_Pressure ? 'text-red-600' : 'text-gray-400'}`}>
                          {scenario.Suction_Pressure ? 'YES' : 'NO'}
                        </td>
                        <td className={`px-2 py-2 text-center border border-gray-300 font-bold text-xs ${scenario.Discharge_Pressure ? 'text-red-600' : 'text-gray-400'}`}>
                          {scenario.Discharge_Pressure ? 'YES' : 'NO'}
                        </td>
                        <td className={`px-2 py-2 text-center border border-gray-300 font-bold text-xs ${scenario.Suction_Temperature ? 'text-red-600' : 'text-gray-400'}`}>
                          {scenario.Suction_Temperature ? 'YES' : 'NO'}
                        </td>
                        <td className={`px-2 py-2 text-center border border-gray-300 font-bold text-xs ${scenario.Discharge_Temperature ? 'text-red-600' : 'text-gray-400'}`}>
                          {scenario.Discharge_Temperature ? 'YES' : 'NO'}
                        </td>
                        <td className="px-3 py-2 border border-gray-300 text-gray-600 text-[11px]">{scenario.symptom}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  ℹ️ No specific RCA scenarios matched. General investigation recommended.
                </p>
              </div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
