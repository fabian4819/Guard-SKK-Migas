'use client';

import { useState, useEffect, useRef } from 'react';
import { SensorData, AnomalyAlert, DashboardStats } from '@/types';
import StatsCard from '@/components/StatsCard';
import ControlPanel from '@/components/ControlPanel';
import MAEChart from '@/components/MAEChart';
import SensorChart from '@/components/SensorChart';
import AlertsPanel from '@/components/AlertsPanel';
import Chatbot from '@/components/Chatbot';
import { Clock, Activity, AlertTriangle, Mail } from 'lucide-react';

export default function Dashboard() {
  // State
  const [isRunning, setIsRunning] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [dataBuffer, setDataBuffer] = useState<SensorData[]>([]);
  const [fullData, setFullData] = useState<SensorData[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyAlert[]>([]);
  const [speed, setSpeed] = useState(0.01); // Maximum speed default
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
        <div className="container mx-auto px-6 py-8">
          <h1 className="text-4xl font-bold mb-2">🛡️ GUARD Live Dashboard</h1>
          <p className="text-lg opacity-90">
            Generative Understanding for Anomaly Response & Detection
          </p>
          <p className="text-sm opacity-75 mt-1">BOOSTER COMPRESSOR B - CPP DONGGI</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Control Panel */}
        <ControlPanel
          onStart={handleStart}
          onStop={handleStop}
          onReset={handleReset}
          isRunning={isRunning}
          onSpeedChange={setSpeed}
          onDateChange={handleDateChange}
        />

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Current Time"
            value={stats.currentTime}
            icon={<Clock />}
            color="primary"
          />
          <StatsCard
            title="Points Processed"
            value={stats.pointsProcessed.toLocaleString()}
            icon={<Activity />}
            color="success"
          />
          <StatsCard
            title="Anomalies Detected"
            value={stats.anomaliesDetected}
            icon={<AlertTriangle />}
            color="danger"
          />
          <StatsCard
            title="Emails Sent"
            value={stats.emailsSent}
            icon={<Mail />}
            color="warning"
          />
        </div>

        {/* Charts */}
        <div className="space-y-6 mb-8">
          <MAEChart data={dataBuffer} currentIndex={currentIndex - 1} />
          <SensorChart data={dataBuffer} />
        </div>

        {/* Alerts Panel */}
        <AlertsPanel alerts={anomalies} />

        {/* Info Box */}
        {!isRunning && dataBuffer.length === 0 && (
          <div className="mt-8 bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
            <h3 className="text-xl font-bold text-blue-900 mb-3">🎬 Live Demonstration Mode</h3>
            <div className="text-blue-800 space-y-2">
              <p className="font-semibold">How to use:</p>
              <ol className="list-decimal list-inside space-y-1 ml-4">
                <li>Select date range in control panel (default: Aug 7-15, 2025)</li>
                <li>Choose playback speed (Maximum Speed recommended for demo)</li>
                <li>Click "Start Simulation" to begin live playback</li>
              </ol>
              <p className="font-semibold mt-4">What happens:</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>Data plays forward in real-time</li>
                <li>Charts update live as time progresses</li>
                <li>Anomalies detected automatically</li>
                <li>See the entire period unfold before your eyes!</li>
              </ul>
              <p className="mt-4 text-sm">
                <strong>Loaded:</strong> {fullData.length.toLocaleString()} data points from{' '}
                {dateRange.startDate} to {dateRange.endDate}
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 mt-12">
        <div className="container mx-auto px-6 py-6 text-center">
          <p className="text-sm">
            GUARD (Generative Understanding for Anomaly Response & Detection) | Real historical
            data, simulated live playback
          </p>
          <p className="text-xs mt-2 opacity-75">
            Built with Next.js, React, and TailwindCSS
          </p>
        </div>
      </footer>

      {/* Chatbot */}
      <Chatbot data={dataBuffer} />
    </div>
  );
}
