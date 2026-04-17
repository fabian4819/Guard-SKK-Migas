import { NextRequest, NextResponse } from 'next/server';
import Groq from 'groq-sdk';
import { SYSTEM_CONTEXT } from '@/lib/rcaContext';

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

export async function POST(request: NextRequest) {
  try {
    const { messages, sensorData } = await request.json();

    // Build enhanced context with current sensor data if available
    let contextualInfo = SYSTEM_CONTEXT;

    if (sensorData && sensorData.length > 0) {
      const latestData = sensorData[sensorData.length - 1];
      const anomalyCount = sensorData.filter((d: any) => d.status === 'ANOMALY').length;
      const totalGasLoss = sensorData
        .filter((d: any) => d.status === 'ANOMALY')
        .reduce((sum: number, d: any) => sum + (d.Gas_Loss_MMSCF || 0), 0);

      contextualInfo += `

# CURRENT SESSION DATA CONTEXT
- Total data points loaded: ${sensorData.length}
- Anomalies detected: ${anomalyCount} (${((anomalyCount / sensorData.length) * 100).toFixed(1)}%)
- Total gas loss: ${totalGasLoss.toFixed(3)} MMSCF
- Latest reading timestamp: ${latestData.datetime}
- Latest status: ${latestData.status}
- Latest MAE: ${latestData.MAE?.toFixed(4)}

# LATEST SENSOR READINGS
- Flow Rate (FI1001B): ${latestData.Flow_Rate?.toFixed(2)} MMSCFD ${getStatusIndicator(latestData.Flow_Rate, 45, 56)}
- Suction Pressure (PI1001B): ${latestData.Suction_Pressure?.toFixed(2)} barg ${getStatusIndicator(latestData.Suction_Pressure, 33, 34)}
- Discharge Pressure (PI1004B): ${latestData.Discharge_Pressure?.toFixed(2)} barg ${getStatusIndicator(latestData.Discharge_Pressure, 60, 63.3)}
- Suction Temperature (TI1003B): ${latestData.Suction_Temperature?.toFixed(2)} °C ${getStatusIndicator(latestData.Suction_Temperature, 90, 100)}
- Discharge Temperature (TI1004B): ${latestData.Discharge_Temperature?.toFixed(2)} °C ${getStatusIndicator(latestData.Discharge_Temperature, 189, 205)}

Use this data to provide accurate, contextual responses about the current system state.`;
    }

    // Prepare messages with system context
    const chatMessages = [
      {
        role: 'system' as const,
        content: contextualInfo,
      },
      ...messages.map((msg: any) => ({
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
      })),
    ];

    // Call Groq API
    const completion = await groq.chat.completions.create({
      messages: chatMessages,
      model: process.env.GROQ_MODEL || 'llama-3.3-70b-versatile',
      temperature: 0.7,
      max_tokens: 1024,
      top_p: 1,
      stream: false,
    });

    const responseMessage = completion.choices[0]?.message?.content || 'Sorry, I could not generate a response.';

    return NextResponse.json({
      success: true,
      message: responseMessage,
      usage: completion.usage,
    });
  } catch (error: any) {
    console.error('Chat API Error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'An error occurred while processing your request.',
      },
      { status: 500 }
    );
  }
}

function getStatusIndicator(value: number, min: number, max: number): string {
  if (value < min) return '⚠️ BELOW NORMAL';
  if (value > max) return '⚠️ ABOVE NORMAL';
  return '✅ NORMAL';
}
