import { readFileSync } from 'fs';
import { join } from 'path';
import * as XLSX from 'xlsx';
import { SensorData } from '@/types';

/**
 * Calculate threshold ratio based on actual sensor deviations
 * Returns value between 60-150%
 * > 100% = ANOMALY, < 100% = NORMAL
 */
function generateMockThresholdRatio(sensorData: any): { threshold_ratio: number; status: 'NORMAL' | 'ANOMALY' } {
  const sensors = {
    Flow_Rate: { low: 45, high: 56, weight: 1.0 },
    Suction_Pressure: { low: 33, high: 34, weight: 1.2 },
    Discharge_Pressure: { low: 60, high: 63.3, weight: 1.2 },
    Suction_Temperature: { low: 90, high: 100, weight: 0.8 },
    Discharge_Temperature: { low: 189, high: 205, weight: 0.8 },
  };

  let totalDeviation = 0;
  let outOfRangeCount = 0;
  const debugInfo: any = {};

  Object.entries(sensors).forEach(([key, config]) => {
    const value = sensorData[key];
    const range = config.high - config.low;
    debugInfo[key] = { value, low: config.low, high: config.high };

    if (value < config.low) {
      // Calculate how far below (as multiple of range)
      const deviationMultiple = (config.low - value) / range;
      totalDeviation += deviationMultiple * 30 * config.weight; // 30 points per range deviation
      outOfRangeCount++;
    } else if (value > config.high) {
      // Calculate how far above (as multiple of range)
      const deviationMultiple = (value - config.high) / range;
      totalDeviation += deviationMultiple * 30 * config.weight; // 30 points per range deviation
      outOfRangeCount++;
    } else {
      // Within range - minimal contribution
      const mid = (config.low + config.high) / 2;
      const normalizedDist = Math.abs(value - mid) / (range / 2);
      totalDeviation += normalizedDist * 2 * config.weight; // Max 2 points when at edge
    }
  });

  // Calculate threshold ratio
  let threshold_ratio;
  if (outOfRangeCount > 0) {
    // Has anomalies - base at 100% + deviations
    threshold_ratio = 100 + totalDeviation;
  } else {
    // All normal - base lower
    threshold_ratio = 75 + totalDeviation;
  }

  // Clamp to 60-150% range
  threshold_ratio = Math.max(60, Math.min(150, threshold_ratio));

  // Determine status based on threshold
  const status: 'NORMAL' | 'ANOMALY' = threshold_ratio > 100 ? 'ANOMALY' : 'NORMAL';

  // Debug logging (first 3 data points only to avoid spam)
  if (Math.random() < 0.01) { // Log ~1% of calculations
    console.log('🔍 Threshold Debug:', {
      sensors: debugInfo,
      outOfRangeCount,
      totalDeviation: totalDeviation.toFixed(2),
      threshold_ratio: threshold_ratio.toFixed(2),
      status
    });
  }

  return { threshold_ratio, status };
}

export function loadCSVData(startDate?: string, endDate?: string): SensorData[] {
  try {
    // Path to Test.xlsx file - using absolute path or relative from project root
    const xlsxPath = process.env.XLSX_PATH || join(process.cwd(), '..', 'Test.xlsx');

    console.log('Loading Excel from:', xlsxPath);

    // Read file as buffer first (works better in Next.js API routes)
    const fileBuffer = readFileSync(xlsxPath);
    const workbook = XLSX.read(fileBuffer, { type: 'buffer' });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];

    // Convert to JSON
    const jsonData: any[] = XLSX.utils.sheet_to_json(worksheet);

    const data: SensorData[] = jsonData.map((row) => {
      // Parse datetime from Excel format (DD/M/YYYY H:mm:ss)
      let parsedDatetime: string;
      if (typeof row.Datetime === 'string') {
        // Parse DD/M/YYYY H:mm:ss format
        const parts = row.Datetime.split(' ');
        const dateParts = parts[0].split('/');
        const timeParts = parts[1]?.split(':') || ['0', '0', '0'];

        // Convert to YYYY-MM-DD HH:mm:ss format
        const day = dateParts[0].padStart(2, '0');
        const month = dateParts[1].padStart(2, '0');
        const year = dateParts[2];
        const hour = timeParts[0].padStart(2, '0');
        const minute = timeParts[1].padStart(2, '0');
        const second = timeParts[2].padStart(2, '0');

        parsedDatetime = `${year}-${month}-${day} ${hour}:${minute}:${second}`;
      } else {
        parsedDatetime = new Date().toISOString();
      }

      // Generate mock threshold ratio and status
      const { threshold_ratio, status } = generateMockThresholdRatio(row);

      // Calculate derived values
      const exceed_percent = threshold_ratio - 100;
      const is_anomaly = status === 'ANOMALY';

      // Mock MAE based on threshold ratio
      const MAE = threshold_ratio > 100 ? 0.15 + Math.random() * 0.15 : 0.05 + Math.random() * 0.05;

      // Calculate deviations for each sensor
      const sensors = {
        Flow_Rate: { low: 45, high: 56 },
        Suction_Pressure: { low: 33, high: 34 },
        Discharge_Pressure: { low: 60, high: 63.3 },
        Suction_Temperature: { low: 90, high: 100 },
        Discharge_Temperature: { low: 189, high: 205 },
      };

      const dev_Flow_Rate = row.Flow_Rate - ((sensors.Flow_Rate.low + sensors.Flow_Rate.high) / 2);
      const dev_Suction_Pressure = row.Suction_Pressure - ((sensors.Suction_Pressure.low + sensors.Suction_Pressure.high) / 2);
      const dev_Discharge_Pressure = row.Discharge_Pressure - ((sensors.Discharge_Pressure.low + sensors.Discharge_Pressure.high) / 2);
      const dev_Suction_Temperature = row.Suction_Temperature - ((sensors.Suction_Temperature.low + sensors.Suction_Temperature.high) / 2);
      const dev_Discharge_Temperature = row.Discharge_Temperature - ((sensors.Discharge_Temperature.low + sensors.Discharge_Temperature.high) / 2);

      // Calculate percentage deviations
      const pct_Flow_Rate = (dev_Flow_Rate / ((sensors.Flow_Rate.low + sensors.Flow_Rate.high) / 2)) * 100;
      const pct_Suction_Pressure = (dev_Suction_Pressure / ((sensors.Suction_Pressure.low + sensors.Suction_Pressure.high) / 2)) * 100;
      const pct_Discharge_Pressure = (dev_Discharge_Pressure / ((sensors.Discharge_Pressure.low + sensors.Discharge_Pressure.high) / 2)) * 100;
      const pct_Suction_Temperature = (dev_Suction_Temperature / ((sensors.Suction_Temperature.low + sensors.Suction_Temperature.high) / 2)) * 100;
      const pct_Discharge_Temperature = (dev_Discharge_Temperature / ((sensors.Discharge_Temperature.low + sensors.Discharge_Temperature.high) / 2)) * 100;

      // Calculate contributions
      const totalDeviation = Math.abs(pct_Flow_Rate) + Math.abs(pct_Suction_Pressure) +
                           Math.abs(pct_Discharge_Pressure) + Math.abs(pct_Suction_Temperature) +
                           Math.abs(pct_Discharge_Temperature);

      const contrib_Flow_Rate = totalDeviation > 0 ? (Math.abs(pct_Flow_Rate) / totalDeviation) * 100 : 0;
      const contrib_Suction_Pressure = totalDeviation > 0 ? (Math.abs(pct_Suction_Pressure) / totalDeviation) * 100 : 0;
      const contrib_Discharge_Pressure = totalDeviation > 0 ? (Math.abs(pct_Discharge_Pressure) / totalDeviation) * 100 : 0;
      const contrib_Suction_Temperature = totalDeviation > 0 ? (Math.abs(pct_Suction_Temperature) / totalDeviation) * 100 : 0;
      const contrib_Discharge_Temperature = totalDeviation > 0 ? (Math.abs(pct_Discharge_Temperature) / totalDeviation) * 100 : 0;

      // Mock gas loss for anomalies
      const Gas_Loss_MMSCF = is_anomaly ? Math.random() * 0.01 : 0;
      const Production_Loss_MMSCFD = is_anomaly ? Math.abs(dev_Flow_Rate) : 0;

      return {
        datetime: parsedDatetime,
        status,
        MAE,
        threshold_ratio,
        exceed_percent,
        is_anomaly,
        Flow_Rate: row.Flow_Rate,
        Suction_Pressure: row.Suction_Pressure,
        Discharge_Pressure: row.Discharge_Pressure,
        Suction_Temperature: row.Suction_Temperature,
        Discharge_Temperature: row.Discharge_Temperature,
        contrib_Flow_Rate,
        contrib_Suction_Pressure,
        contrib_Discharge_Pressure,
        contrib_Suction_Temperature,
        contrib_Discharge_Temperature,
        pct_Flow_Rate,
        pct_Suction_Pressure,
        pct_Discharge_Pressure,
        pct_Suction_Temperature,
        pct_Discharge_Temperature,
        dev_Flow_Rate,
        dev_Suction_Pressure,
        dev_Discharge_Pressure,
        dev_Suction_Temperature,
        dev_Discharge_Temperature,
        Production_Loss_MMSCFD,
        Gas_Loss_MMSCF,
      };
    });

    // Filter by date range if provided
    let filteredData = data;
    if (startDate || endDate) {
      filteredData = data.filter(row => {
        const rowDate = new Date(row.datetime);
        if (startDate) {
          const start = new Date(startDate);
          start.setHours(0, 0, 0, 0);
          if (rowDate < start) return false;
        }
        if (endDate) {
          const end = new Date(endDate);
          end.setHours(23, 59, 59, 999); // End of day
          if (rowDate > end) return false;
        }
        return true;
      });
    }

    console.log(`Loaded ${data.length} rows, filtered to ${filteredData.length} rows`);
    return filteredData;
  } catch (error) {
    console.error('Error loading Excel data:', error);
    return [];
  }
}

export function getDataStatistics(data: SensorData[]) {
  const total = data.length;
  const anomalies = data.filter(d => d.status === 'ANOMALY').length;
  const normal = data.filter(d => d.status === 'NORMAL').length;
  const totalGasLoss = data
    .filter(d => d.status === 'ANOMALY')
    .reduce((sum, d) => sum + d.Gas_Loss_MMSCF, 0);

  return {
    total,
    anomalies,
    normal,
    totalGasLoss,
    anomalyRate: (anomalies / total) * 100,
    dateRange: {
      start: data[0]?.datetime,
      end: data[data.length - 1]?.datetime,
    },
  };
}
