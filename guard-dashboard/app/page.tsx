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
  const [anomalies, setAnomalies] = useState<SensorData[]>([]);
  const [speed] = useState(1.0); // Fixed to real-time 1x
  const [enableEmail] = useState(true); // Always enabled
  const [alertEmail, setAlertEmail] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [stats, setStats] = useState<DashboardStats>({
    currentTime: 'Not Started',
    pointsProcessed: 0,
    anomaliesDetected: 0,
    emailsSent: 0,
  });
  const [dateRange, setDateRange] = useState({
    startDate: '2026-04-14',
    endDate: '2026-04-14',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const emailBatchRef = useRef<SensorData[]>([]);
  const emailTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Load data on mount and when date range changes
  useEffect(() => {
    loadData();
  }, [dateRange]);

  // Simulation loop - Infinite looping like dashboard_modern.py
  useEffect(() => {
    if (isRunning && fullData.length > 0) {
      intervalRef.current = setTimeout(() => {
        processNextDataPoint();
      }, speed * 1000);
    }

    return () => {
      if (intervalRef.current) clearTimeout(intervalRef.current);
    };
  }, [isRunning, currentIndex, speed, fullData]);

  // Email batching timer - sends batch every 30 seconds
  useEffect(() => {
    if (isRunning && enableEmail) {
      // Set up 30-second timer
      emailTimerRef.current = setInterval(() => {
        if (emailBatchRef.current.length > 0) {
          sendBatchEmailAlert(emailBatchRef.current);
          emailBatchRef.current = []; // Clear batch after sending
        }
      }, 30000); // 30 seconds

      return () => {
        if (emailTimerRef.current) {
          clearInterval(emailTimerRef.current);
        }
      };
    } else {
      // Clear timer if stopped or email disabled
      if (emailTimerRef.current) {
        clearInterval(emailTimerRef.current);
        emailTimerRef.current = null;
      }
    }
  }, [isRunning, enableEmail]);

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
    // Loop back to start if reached end
    if (currentIndex >= fullData.length) {
      setCurrentIndex(0);
      return;
    }

    const currentData = fullData[currentIndex];
    if (!currentData) return;

    // Add to buffer (keep last 500 points)
    const newBuffer = [...dataBuffer, currentData];
    if (newBuffer.length > 500) {
      newBuffer.shift(); // Remove oldest
    }
    setDataBuffer(newBuffer);

    // Check for anomaly - store full sensor data
    if (currentData.status === 'ANOMALY') {
      setAnomalies((prev) => {
        const updated = [...prev, currentData];
        // Keep last 100 anomalies
        if (updated.length > 100) {
          return updated.slice(-100);
        }
        return updated;
      });

      // Add to email batch if enabled (will be sent every 30 seconds)
      if (enableEmail) {
        emailBatchRef.current.push(currentData);
      }
    }

    // Update stats
    setStats({
      currentTime: new Date(currentData.datetime).toLocaleString(),
      pointsProcessed: currentIndex + 1,
      anomaliesDetected: anomalies.length + (currentData.status === 'ANOMALY' ? 1 : 0),
      emailsSent: 0, // Will be updated by email handler
    });

    setCurrentIndex((prev) => prev + 1);
  };

  const handleStart = () => {
    if (fullData.length === 0) {
      alert('No data loaded. Please check the date range.');
      return;
    }

    // Validate email (required)
    if (!alertEmail || !alertEmail.includes('@')) {
      alert('Please enter a valid email address.');
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
    emailBatchRef.current = []; // Clear email batch
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

  const sendBatchEmailAlert = async (anomalies: SensorData[]) => {
    if (anomalies.length === 0) return;

    // Validate email address
    if (!alertEmail || !alertEmail.includes('@')) {
      console.error('❌ Invalid email address');
      return;
    }

    try {
      console.log(`📧 Sending batch email with ${anomalies.length} anomal${anomalies.length > 1 ? 'ies' : 'y'}...`);

      const response = await fetch('/api/send-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ anomalies, alertEmail }),
      });

      const result = await response.json();

      if (response.ok) {
        setStats(prev => ({ ...prev, emailsSent: prev.emailsSent + 1 }));
        console.log(`✅ Batch email sent successfully with ${anomalies.length} PDF attachment${anomalies.length > 1 ? 's' : ''}`);
      } else {
        console.error('❌ Failed to send batch email:', result.error);
      }
    } catch (error) {
      console.error('❌ Error sending batch email:', error);
    }
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
          <div className="flex items-center justify-between mb-10 pt-12">
            <div className="flex flex-col">
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-600 mb-1">System Navigation</span>
              <h2 className="text-3xl font-black text-gray-900 tracking-tight">
                Control <span className="text-blue-600">Panel</span>
              </h2>
              <div className="h-1 w-12 bg-blue-600 mt-2 rounded-full"></div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors lg:hidden"
              aria-label="Close sidebar"
            >
              <X size={20} className="text-gray-500" />
            </button>
          </div>

          {/* Email Alert Configuration */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Email Alert</h3>
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-700">Alert Email Address *</label>
              <input
                type="email"
                value={alertEmail}
                onChange={(e) => setAlertEmail(e.target.value)}
                placeholder="user@example.com"
                className="w-full px-4 py-3 text-base border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-300 shadow-sm"
                disabled={isRunning}
                required
              />
              <p className="text-sm text-gray-500">
                Alerts sent every 30s if anomalies detected
              </p>
            </div>
          </div>

          <div className="border-t border-gray-100 my-8"></div>

          {/* Control Buttons */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <button
              onClick={handleStart}
              disabled={isRunning}
              className={`flex items-center justify-center gap-2 py-4 px-6 rounded-xl font-bold text-lg transition-all active:scale-95 ${
                isRunning
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed shadow-none'
                  : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-200'
              }`}
            >
              Start
            </button>
            <button
              onClick={handleStop}
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

          {/* Status */}
          <div className={`p-6 rounded-xl flex items-center justify-center gap-3 mb-8 border transition-all duration-500 ${
            isRunning 
              ? 'bg-green-50 border-green-100' 
              : 'bg-gray-50 border-gray-100'
          }`}>
            <div className={`w-3 h-3 rounded ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
            <span className="text-xl font-bold text-gray-900">
              {isRunning ? 'Running' : 'Stopped'}
            </span>
          </div>

          {/* Instructions */}
          <div className="pt-8 border-t border-gray-100">
            <p className="text-sm font-bold text-gray-900 mb-4 tracking-tight uppercase">How it works:</p>
            <ol className="space-y-3 text-sm text-gray-600 list-none pl-0">
              <li>1. Enter your email address</li>
              <li>2. Click Start</li>
              <li>3. Data loops continuously</li>
              <li>4. Charts update in real-time</li>
              <li>5. Anomalies &#8594; Email alerts</li>
            </ol>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className={`min-h-screen transition-all duration-300 ease-in-out ${
        sidebarOpen ? 'ml-80' : 'ml-0'
      }`}>
        {/* Header */}
        <div className={`px-4 md:px-6 pt-6 pb-4 transition-all duration-300 ${
          sidebarOpen ? 'lg:pl-6' : 'lg:pl-20'
        }`}>
          <div className="bg-gradient-to-r from-[#1e3c72] to-[#2a5298] p-4 md:p-6 rounded-xl shadow-md">
            <h1 className="text-white text-2xl md:text-4xl font-black tracking-[0.15em] uppercase"
                style={{ textShadow: '3px 3px 8px rgba(0,0,0,0.5)' }}>
              GUARD
            </h1>
            <p className="text-white text-sm md:text-base mt-2 opacity-95"
               style={{ textShadow: '2px 2px 4px rgba(0,0,0,0.4)' }}>
              Generative Understanding for Anomaly Response & Detection - Machine Learning Early Warning System
            </p>
          </div>
        </div>

        {/* Divider */}
        <div className={`px-4 md:px-6 transition-all duration-300 ${
          sidebarOpen ? 'lg:pl-6' : 'lg:pl-20'
        }`}>
          <div className="border-t border-gray-200 my-4"></div>
        </div>

        {/* Stats Grid */}
        <div className={`px-4 md:px-6 pb-6 transition-all duration-300 ${
          sidebarOpen ? 'lg:pl-6' : 'lg:pl-20'
        }`}>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6 mb-6">
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
                <div className="p-3 md:p-6">
                  {/* Stats Cards Row */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-6 mb-6">
                    <div className="bg-white p-3 md:p-5 rounded-lg border-l-4 border-orange-500 shadow-sm">
                      <p className="text-2xl md:text-4xl font-bold text-[#1e40af] mb-1 md:mb-2">
                        {currentIndex > 0 ? dataBuffer[dataBuffer.length - 1].threshold_ratio.toFixed(1) : '0.0'}%
                      </p>
                      <p className="text-xs text-gray-600 font-medium">Latest Ratio</p>
                    </div>
                    <div className="bg-white p-3 md:p-5 rounded-lg border-l-4 border-orange-500 shadow-sm">
                      <p className="text-2xl md:text-4xl font-bold text-[#dc2626] mb-1 md:mb-2">
                        {anomalies.length > 0 ? Math.max(...anomalies.map(a => a.threshold_ratio)).toFixed(1) : '0.0'}%
                      </p>
                      <p className="text-xs text-gray-600 font-medium">Highest Ratio</p>
                    </div>
                    <div className="bg-white p-3 md:p-5 rounded-lg border-l-4 border-orange-500 shadow-sm">
                      <p className="text-3xl md:text-5xl font-bold text-[#1e40af] mb-1 md:mb-2">{stats.anomaliesDetected}</p>
                      <p className="text-xs text-gray-600 font-medium">Anomaly Count</p>
                    </div>
                  </div>

                  {/* Chart */}
                  <div className="h-[250px] md:h-[400px]">
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

      </div>

      {/* Chatbot - Keep as is */}
      <Chatbot data={dataBuffer} />
    </div>
  );
}
