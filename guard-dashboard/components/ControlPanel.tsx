'use client';

import { useState } from 'react';

interface ControlPanelProps {
  onStart: () => void;
  onStop: () => void;
  onReset: () => void;
  isRunning: boolean;
  onSpeedChange: (speed: number) => void;
  onDateChange: (startDate: string, endDate: string) => void;
  enableEmail: boolean;
  onEnableEmailChange: (enabled: boolean) => void;
  alertEmail: string;
  onAlertEmailChange: (email: string) => void;
}

export default function ControlPanel({
  onStart,
  onStop,
  onReset,
  isRunning,
  onSpeedChange,
  onDateChange,
  enableEmail,
  onEnableEmailChange,
  alertEmail,
  onAlertEmailChange,
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
    <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-8 max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-8">Control Panel</h2>

      {/* Email Alert Section */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Email Alert</h3>
        <div className="space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            Alert Email Address *
          </label>
          <input
            type="email"
            value={alertEmail}
            onChange={(e) => onAlertEmailChange(e.target.value)}
            placeholder="user@example.com"
            title="Alert Email Address"
            className="w-full px-4 py-3 text-base border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-300"
            disabled={isRunning}
          />
          <p className="text-sm text-gray-500">
            Alerts sent every 30s if anomalies detected
          </p>
        </div>
      </div>

      <div className="pt-6 border-t border-gray-100 mb-8">
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={onStart}
            disabled={isRunning}
            className={`flex items-center justify-center gap-2 py-4 px-6 rounded-xl font-bold text-lg transition-all shadow-lg active:scale-95 ${
              isRunning 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed shadow-none' 
                : 'bg-blue-600 text-white hover:bg-blue-700 shadow-blue-200'
            }`}
          >
            Start
          </button>
          <button
            onClick={onStop}
            disabled={!isRunning}
            className={`flex items-center justify-center gap-2 py-4 px-6 rounded-xl font-bold text-lg transition-all active:scale-95 ${
              !isRunning 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
          >
            Stop
          </button>
        </div>
      </div>

      <div className="pt-6 border-t border-gray-100">
        <div className="bg-gray-50 border border-gray-100 rounded-xl p-6 flex items-center justify-center gap-3">
          <div className={`w-3 h-3 rounded ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
          <span className="text-xl font-bold text-gray-900">
            {isRunning ? 'Running' : 'Stopped'}
          </span>
        </div>
      </div>

      {/* How it works section */}
      <div className="mt-8 pt-8 border-t border-gray-100">
        <h4 className="text-sm font-bold text-gray-900 mb-4 tracking-tight uppercase">How it works:</h4>
        <ol className="space-y-3 text-sm text-gray-600 list-none pl-0">
          <li>1. Enter your email address</li>
          <li>2. Click Start</li>
          <li>3. Data loops continuously</li>
          <li>4. Charts update in real-time</li>
          <li>5. Anomalies &#8594; Email alerts</li>
        </ol>
      </div>
    </div>
  );
}
