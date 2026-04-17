'use client';

import { useState, useEffect, useRef } from 'react';
import { SensorData, AnomalyAlert, DashboardStats } from '@/types';
import StatsCard from '@/components/StatsCard';
import ControlPanel from '@/components/ControlPanel';
import MAEChart from '@/components/MAEChart';
import SensorChart from '@/components/SensorChart';
import AlertsPanel from '@/components/AlertsPanel';
import Chatbot from '@/components/Chatbot';
import { Clock, Activity, AlertTriangle, Mail, Play, Pause, Menu, X, ChevronLeft, ChevronRight } from 'lucide-react';

export default function Dashboard() {
  // State
  const [isRunning, setIsRunning] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [dataBuffer, setDataBuffer] = useState<SensorData[]>([]);
  const [fullData, setFullData] = useState<SensorData[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyAlert[]>([]);
  const [speed, setSpeed] = useState(0.01); // Maximum speed default
  const [enableEmail, setEnableEmail] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [stats, setStats] = useState<DashboardStats>({
    currentTime: 'Not Started',
    pointsProcessed: 0,
    anomaliesDetected: 0,
    emailsSent: 0,
  });
  const [dateRange, setDateRange] = useState({
    startDate: '2025-08-07',
    endDate: '2025-08-15',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Load data on mount and when date range changes
  useEffect(() => {
    loadData();
  }, [dateRange]);

  // Simulation loop
  useEffect(() => {
    if (isRunning && currentIndex < fullData.length) {
      intervalRef.current = setTimeout(() => {
        processNextDataPoint();
      }, speed * 1000);
    } else if (currentIndex >= fullData.length && isRunning) {
      setIsRunning(false);
      alert('✅ Simulation Complete!');
    }

    return () => {
      if (intervalRef.current) clearTimeout(intervalRef.current);
    };
  }, [isRunning, currentIndex, speed, fullData]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/data?startDate=${dateRange.startDate}&endDate=${dateRange.endDate}`
      );

      if (!response.ok) {
        throw new Error('Failed to load data');
      }

      const result = await response.json();
      setFullData(result.data);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      setLoading(false);
    }
  };

  const processNextDataPoint = () => {
    const currentData = fullData[currentIndex];
    if (!currentData) return;

    // Add to buffer
    const newBuffer = [...dataBuffer, currentData];
    setDataBuffer(newBuffer);

    // Check for anomaly
    if (currentData.status === 'ANOMALY') {
      const newAnomaly: AnomalyAlert = {
        timestamp: currentData.datetime,
        MAE: currentData.MAE,
        threshold_ratio: currentData.threshold_ratio,
        gas_loss: currentData.Gas_Loss_MMSCF,
        emailStatus: 'Not Sent', // Simplified for now
      };
      setAnomalies((prev) => [...prev, newAnomaly]);
    }

    // Update stats
    setStats({
      currentTime: new Date(currentData.datetime).toLocaleString(),
      pointsProcessed: currentIndex + 1,
      anomaliesDetected: anomalies.length + (currentData.status === 'ANOMALY' ? 1 : 0),
      emailsSent: 0, // Simplified for now
    });

    setCurrentIndex((prev) => prev + 1);
  };

  const handleStart = () => {
    if (fullData.length === 0) {
      alert('No data loaded. Please check the date range.');
      return;
    }
    setIsRunning(true);
  };

  const handleStop = () => {
    setIsRunning(false);
  };

  const handleReset = () => {
    setIsRunning(false);
    setCurrentIndex(0);
    setDataBuffer([]);
    setAnomalies([]);
    setStats({
      currentTime: 'Not Started',
      pointsProcessed: 0,
      anomaliesDetected: 0,
      emailsSent: 0,
    });
  };

  const handleDateChange = (startDate: string, endDate: string) => {
    if (isRunning) {
      alert('Stop the simulation before changing dates.');
      return;
    }
    setDateRange({ startDate, endDate });
    handleReset();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center bg-red-50 border border-red-200 rounded-lg p-8 max-w-md">
          <AlertTriangle className="text-red-600 mx-auto mb-4" size={48} />
          <h2 className="text-2xl font-bold text-red-800 mb-2">Error Loading Data</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={loadData}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Sidebar Toggle Button - Fixed on top left */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className={`fixed top-4 z-50 p-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 ${
          sidebarOpen ? 'left-[304px]' : 'left-4'
        }`}
        aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
        title={sidebarOpen ? "Hide Control Panel" : "Show Control Panel"}
      >
        {sidebarOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
        {/* Status indicator when sidebar is closed */}
        {!sidebarOpen && isRunning && (
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse border-2 border-white"></span>
        )}
      </button>

      {/* Sidebar Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-full w-80 bg-white border-r border-gray-200 overflow-y-auto z-40 shadow-lg transition-transform duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="p-6 pt-4">
          {/* Sidebar Header with Close Button */}
          <div className="flex items-center justify-between mb-6 pt-12">
            <h3 className="text-sm font-bold text-gray-700">⚙️ Control Panel</h3>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-1 hover:bg-gray-100 rounded transition-colors lg:hidden"
              aria-label="Close sidebar"
            >
              <X size={18} className="text-gray-500" />
            </button>
          </div>

          {/* Data Source Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-xs font-semibold text-blue-900 mb-1">📊 Data Source</p>
            <p className="text-xs text-blue-700">Test.xlsx</p>
            <p className="text-xs text-blue-600">14/4/2026 00:00-00:53</p>
            <p className="text-xs text-blue-500">(Infinite loop)</p>
          </div>

          {/* Playback Speed */}
          <div className="mb-6">
            <label className="block text-sm font-bold text-gray-700 mb-3">⚡ Playback Speed</label>
            <select
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={1.0}>Real-time (1x)</option>
              <option value={0.5}>2x Speed</option>
              <option value={0.2}>5x Speed</option>
              <option value={0.1}>10x Speed</option>
              <option value={0.01}>Maximum Speed</option>
            </select>
          </div>

          <div className="border-t border-gray-200 my-6"></div>

          {/* Email Alerts */}
          <div className="mb-6">
            <label className="block text-sm font-bold text-gray-700 mb-3">📧 Email Alerts</label>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={enableEmail}
                onChange={(e) => setEnableEmail(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">Send Email Alerts</span>
            </div>
            {!enableEmail && (
              <p className="text-xs text-orange-600 mt-2">⚠️ Email alerts disabled</p>
            )}
          </div>

          <div className="border-t border-gray-200 my-6"></div>

          {/* Control Buttons */}
          <div className="grid grid-cols-2 gap-3 mb-6">
            <button
              onClick={handleStart}
              disabled={isRunning}
              className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold text-sm transition-all ${
                isRunning
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md'
              }`}
            >
              <Play size={16} />
              Start
            </button>
            <button
              onClick={handleStop}
              disabled={!isRunning}
              className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold text-sm transition-all ${
                !isRunning
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-orange-500 text-white hover:bg-orange-600 shadow-md'
              }`}
            >
              <Pause size={16} />
              Stop
            </button>
          </div>

          <div className="border-t border-gray-200 my-6"></div>

          {/* Status */}
          <div className={`p-4 rounded-lg ${isRunning ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'}`}>
            <p className="text-sm font-bold">
              {isRunning ? '🔴 LIVE - Running' : '⏹️ Stopped'}
            </p>
          </div>

          {/* Instructions */}
          <div className="mt-6 text-xs text-gray-600 space-y-2">
            <p className="font-bold text-gray-700">How it works:</p>
            <ol className="list-decimal list-inside space-y-1 text-gray-600">
              <li>Click ▶️ Start</li>
              <li>Data loops continuously</li>
              <li>Charts update live</li>
              <li>Anomalies → Email alerts</li>
            </ol>
            <p className="mt-3 text-gray-500">
              <span className="font-semibold">Speed:</span> {
                speed === 1.0 ? 'Real-time (1x)' :
                speed === 0.5 ? '2x Speed' :
                speed === 0.2 ? '5x Speed' :
                speed === 0.1 ? '10x Speed' :
                'Maximum Speed'
              }
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className={`min-h-screen transition-all duration-300 ease-in-out ${
        sidebarOpen ? 'ml-80' : 'ml-0'
      }`}>
        {/* Header */}
        <div className={`px-6 pt-6 pb-4 transition-all duration-300 ${
          sidebarOpen ? 'pl-6' : 'pl-20'
        }`}>
          <div className="bg-gradient-to-r from-[#1e3c72] to-[#2a5298] p-6 rounded-xl shadow-md">
            <h1 className="text-white text-4xl font-black tracking-[0.15em] uppercase"
                style={{ textShadow: '3px 3px 8px rgba(0,0,0,0.5)' }}>
              GUARD
            </h1>
            <p className="text-white text-base mt-2 opacity-95"
               style={{ textShadow: '2px 2px 4px rgba(0,0,0,0.4)' }}>
              Generative Understanding for Anomaly Response & Detection - Machine Learning Based Early Warning System
            </p>
          </div>
        </div>

        {/* Divider */}
        <div className={`px-6 transition-all duration-300 ${
          sidebarOpen ? 'pl-6' : 'pl-20'
        }`}>
          <div className="border-t border-gray-200 my-4"></div>
        </div>

        {/* Stats Grid */}
        <div className={`px-6 pb-6 transition-all duration-300 ${
          sidebarOpen ? 'pl-6' : 'pl-20'
        }`}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <StatsCard
              title="Current Time"
              value={stats.currentTime === 'Not Started' ? '2026-04-14\n00:00:21' : stats.currentTime.replace(', ', '\n')}
              color="primary"
            />
            <StatsCard
              title="Points Processed"
              value={stats.pointsProcessed}
              color="success"
            />
            <StatsCard
              title="Anomalies"
              value={stats.anomaliesDetected}
              color="danger"
            />
            <StatsCard
              title="Emails Sent"
              value={stats.emailsSent}
              color="success"
            />
          </div>

          {/* Divider */}
          <div className="border-t border-gray-200 my-6"></div>

          {/* Main Dashboard Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Main Charts - 8 columns */}
            <div className="lg:col-span-8 space-y-6">
              {/* Threshold Ratio Analysis */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-orange-500 to-orange-600 px-5 py-3">
                  <h2 className="text-white font-semibold text-base">Threshold Ratio Analysis</h2>
                </div>
                <div className="p-6">
                  {/* Stats Cards Row */}
                  <div className="grid grid-cols-3 gap-6 mb-6">
                    <div className="bg-white p-4 rounded-lg border-l-4 border-orange-500 shadow-sm">
                      <p className="text-3xl font-bold text-blue-900 mb-1">
                        {currentIndex > 0 ? (dataBuffer[dataBuffer.length - 1].threshold_ratio * (dataBuffer[dataBuffer.length - 1].threshold_ratio < 2 ? 100 : 1)).toFixed(1) : '---'}%
                      </p>
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Latest Ratio</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg border-l-4 border-orange-500 shadow-sm">
                      <p className="text-3xl font-bold text-red-600 mb-1">
                        {anomalies.length > 0 ? Math.max(...anomalies.map(a => a.threshold_ratio * (a.threshold_ratio < 2 ? 100 : 1))).toFixed(1) : '---'}%
                      </p>
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Highest Ratio</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg border-l-4 border-orange-500 shadow-sm">
                      <p className="text-3xl font-bold text-blue-900 mb-1">{stats.anomaliesDetected}</p>
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Anomaly Count</p>
                    </div>
                  </div>

                  {/* Chart */}
                  <div className="h-[400px]">
                    <MAEChart data={dataBuffer} currentIndex={currentIndex - 1} />
                  </div>
                </div>
              </div>

              {/* Sensor Monitoring */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-orange-500 to-orange-600 px-5 py-3">
                  <h2 className="text-white font-semibold text-base">Equipment Sensor Monitoring</h2>
                </div>
                <div className="p-6">
                  <SensorChart data={dataBuffer} />
                </div>
              </div>
            </div>

            {/* Alerts Panel - 4 columns */}
            <div className="lg:col-span-4">
              <AlertsPanel alerts={anomalies} />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className={`px-6 pb-6 transition-all duration-300 ${
          sidebarOpen ? 'pl-6' : 'pl-20'
        }`}>
          <div className="border-t border-gray-200 pt-4">
            <p className="text-sm text-gray-500 text-center">🛡️ GUARD | SKK Migas</p>
          </div>
        </div>
      </div>

      {/* Chatbot - Keep as is */}
      <Chatbot data={dataBuffer} />
    </div>
  );
}
