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
    <div className="min-h-screen bg-[#f0f2f5] font-sans">
      {/* Main Header - LEADS-Inspired */}
      <div className="mx-4 mt-4 mb-6">
        <div className="bg-[#1e3c72] p-8 rounded-xl shadow-lg relative overflow-hidden group transition-all duration-300">
          <div className="relative z-10">
            <h1 className="text-white text-5xl font-black tracking-widest uppercase drop-shadow-md">
              GUARD
            </h1>
            <p className="text-white text-md font-medium mt-4">
              Generative Understanding for Anomaly Response & Detection - Machine Learning Based Early Warning System
            </p>
          </div>
        </div>
      </div>

      <main className="px-6 pb-12">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
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

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-9 space-y-10">
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
              <div className="bg-orange-500 px-6 py-3 text-white font-black text-md uppercase tracking-wide">
                Threshold Ratio Analysis
              </div>
              <div className="p-8">
                <div className="grid grid-cols-3 gap-8 mb-10">
                  <div className="border-l-4 border-blue-600 pl-6">
                    <p className="text-4xl font-black text-blue-900 mb-2">
                       {currentIndex > 0 ? (dataBuffer[dataBuffer.length - 1].threshold_ratio * (dataBuffer[dataBuffer.length - 1].threshold_ratio < 2 ? 100 : 1)).toFixed(1) : '---'}%
                    </p>
                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Latest Ratio</p>
                  </div>
                  <div className="border-l-4 border-orange-500 pl-6">
                    <p className="text-4xl font-black text-red-600 mb-2">
                      {anomalies.length > 0 ? Math.max(...anomalies.map(a => a.threshold_ratio * (a.threshold_ratio < 2 ? 100 : 1))).toFixed(1) : '---'}%
                    </p>
                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Highest Ratio</p>
                  </div>
                  <div className="border-l-4 border-blue-900 pl-6">
                    <p className="text-4xl font-black text-blue-900 mb-2">{stats.anomaliesDetected}</p>
                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Anomaly Count</p>
                  </div>
                </div>
                
                <div className="h-[400px]">
                  <MAEChart data={dataBuffer} currentIndex={currentIndex - 1} />
                </div>
              </div>
            </div>

            <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-100">
               <SensorChart data={dataBuffer} />
            </div>
          </div>

          <div className="lg:col-span-3 space-y-8">
            <AlertsPanel alerts={anomalies} />
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
              <div className="flex items-center gap-2 mb-6 border-b border-gray-50 pb-4">
                <Activity size={18} className="text-blue-600" />
                <h3 className="font-black text-gray-800 uppercase text-xs tracking-widest">Control Panel</h3>
              </div>
              <ControlPanel
                onStart={handleStart}
                onStop={handleStop}
                onReset={handleReset}
                isRunning={isRunning}
                onSpeedChange={setSpeed}
                onDateChange={handleDateChange}
              />
            </div>
          </div>
        </div>
      </main>

      <Chatbot data={dataBuffer} />
    </div>
  );
}
