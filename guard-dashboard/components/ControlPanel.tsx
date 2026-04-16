'use client';

import { useState } from 'react';
import { Play, Pause, RotateCcw } from 'lucide-react';

interface ControlPanelProps {
  onStart: () => void;
  onStop: () => void;
  onReset: () => void;
  isRunning: boolean;
  onSpeedChange: (speed: number) => void;
  onDateChange: (startDate: string, endDate: string) => void;
}

export default function ControlPanel({
  onStart,
  onStop,
  onReset,
  isRunning,
  onSpeedChange,
  onDateChange,
}: ControlPanelProps) {
  const [speed, setSpeed] = useState(0.01); // Maximum speed by default
  const [startDate, setStartDate] = useState('2025-08-07');
  const [endDate, setEndDate] = useState('2025-08-15');

  const speedOptions = [
    { label: 'Real-time', value: 1.0 },
    { label: '2x Speed', value: 0.5 },
    { label: '5x Speed', value: 0.2 },
    { label: '10x Speed', value: 0.1 },
    { label: 'Maximum', value: 0.01 },
  ];

  const handleSpeedChange = (value: number) => {
    setSpeed(value);
    onSpeedChange(value);
  };

  const handleDateSubmit = () => {
    onDateChange(startDate, endDate);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800">⚙️ Simulation Controls</h2>

      {/* Date Range */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">📅 Date Range</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs text-gray-600 mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isRunning}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isRunning}
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={handleDateSubmit}
              disabled={isRunning}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Apply
            </button>
          </div>
        </div>
      </div>

      {/* Speed Control */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">⚡ Playback Speed</h3>
        <select
          value={speed}
          onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {speedOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Control Buttons */}
      <div className="flex gap-3">
        {!isRunning ? (
          <button
            onClick={onStart}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold shadow-md hover:shadow-lg"
          >
            <Play size={20} />
            Start Simulation
          </button>
        ) : (
          <button
            onClick={onStop}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-semibold shadow-md hover:shadow-lg"
          >
            <Pause size={20} />
            Stop Simulation
          </button>
        )}
        <button
          onClick={onReset}
          className="flex items-center justify-center gap-2 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold shadow-md hover:shadow-lg"
        >
          <RotateCcw size={20} />
          Reset
        </button>
      </div>

      {/* Status Indicator */}
      <div className="mt-4">
        {isRunning ? (
          <div className="flex items-center gap-2 text-sm text-green-600 font-medium">
            <span className="inline-block w-3 h-3 bg-green-600 rounded-full animate-pulse"></span>
            Simulation Running
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-gray-600 font-medium">
            <span className="inline-block w-3 h-3 bg-gray-400 rounded-full"></span>
            Simulation Stopped
          </div>
        )}
      </div>
    </div>
  );
}
