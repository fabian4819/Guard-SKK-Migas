'use client';

import { useState } from 'react';
import { MessageCircle, X, Send, Trash2 } from 'lucide-react';
import { SensorData } from '@/types';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatbotProps {
  data?: SensorData[];
}

export default function Chatbot({ data }: ChatbotProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '👋 Hi! I\'m GUARD Assistant. Ask me anything about the system or your data!',
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages([...messages, userMessage]);
    setInput('');

    // Generate response
    setTimeout(() => {
      const response = generateResponse(input, data);
      const botMessage: Message = {
        role: 'assistant',
        content: response,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, botMessage]);
    }, 500);
  };

  const handleClear = () => {
    setMessages([
      {
        role: 'assistant',
        content: '👋 Chat cleared! How can I help you?',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-full shadow-2xl hover:scale-110 transition-transform z-50 flex items-center justify-center animate-pulse hover:animate-none"
          aria-label="Open chat"
        >
          <MessageCircle size={28} />
        </button>
      )}

      {/* Chat Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl h-[600px] flex flex-col overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-5 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">🛡️ GUARD Assistant</h3>
                <p className="text-sm opacity-90">Anomaly Detection Support</p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
                aria-label="Close chat"
              >
                <X size={24} />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-gray-50">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-md ${
                      message.role === 'user'
                        ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-br-sm'
                        : 'bg-white text-gray-800 border border-gray-200 rounded-bl-sm'
                    }`}
                  >
                    <p className="whitespace-pre-wrap text-sm">{message.content}</p>
                    <p
                      className={`text-xs mt-2 ${
                        message.role === 'user' ? 'text-white text-opacity-70' : 'text-gray-500'
                      }`}
                    >
                      {message.timestamp}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200 bg-white">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                <button
                  onClick={handleSend}
                  className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  aria-label="Send message"
                >
                  <Send size={20} />
                </button>
                <button
                  onClick={handleClear}
                  className="px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  aria-label="Clear chat"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// Simple response generator (can be enhanced with AI later)
function generateResponse(query: string, data?: SensorData[]): string {
  const q = query.toLowerCase();

  // About GUARD
  if (q.includes('what is guard') || q.includes('about guard')) {
    return '🛡️ **GUARD** = Generative Understanding for Anomaly Response & Detection\n\nAn advanced system for monitoring BOOSTER COMPRESSOR B at CPP Donggi using LSTM anomaly detection and comprehensive RCA.';
  }

  // How it works
  if (q.includes('how') && (q.includes('work') || q.includes('function'))) {
    return '⚙️ **How GUARD Works:**\n\n1. Monitors 5 sensors continuously\n2. LSTM compares actual vs predicted values\n3. Detects anomalies when MAE exceeds threshold\n4. Generates RCA report by division\n5. Sends email alerts with PDF';
  }

  // Statistics
  if (data && (q.includes('statistic') || q.includes('summary') || q.includes('overview'))) {
    const total = data.length;
    const anomalies = data.filter((d) => d.status === 'ANOMALY').length;
    const normal = total - anomalies;
    const totalGasLoss = data
      .filter((d) => d.status === 'ANOMALY')
      .reduce((sum, d) => sum + d.Gas_Loss_MMSCF, 0);

    return `📊 **Data Summary:**\n- Total records: ${total.toLocaleString()}\n- Anomalies: ${anomalies.toLocaleString()} (${(
      (anomalies / total) *
      100
    ).toFixed(1)}%)\n- Normal: ${normal.toLocaleString()} (${((normal / total) * 100).toFixed(
      1
    )}%)\n- Total gas loss: ${totalGasLoss.toFixed(3)} MMSCF`;
  }

  // Latest anomaly
  if (data && (q.includes('latest') || q.includes('recent') || q.includes('last'))) {
    const anomalies = data.filter((d) => d.status === 'ANOMALY');
    if (anomalies.length > 0) {
      const latest = anomalies[anomalies.length - 1];
      return `🕐 **Latest Anomaly:**\n- Timestamp: ${latest.datetime}\n- MAE: ${latest.MAE.toFixed(
        4
      )}\n- Gas Loss: ${latest.Gas_Loss_MMSCF.toFixed(4)} MMSCF`;
    }
    return 'No anomalies detected yet.';
  }

  // Sensors
  if (q.includes('sensor')) {
    return '📡 **Monitored Sensors:**\n\n1. FI1001B - Flow Rate (MMSCFD)\n2. PI1001B - Suction Pressure (barg)\n3. PI1004B - Discharge Pressure (barg)\n4. TI1003B - Suction Temperature (°C)\n5. TI1004B - Discharge Temperature (°C)';
  }

  // MAE explanation
  if (q.includes('mae') && (q.includes('what') || q.includes('explain'))) {
    return '📊 **MAE** = Mean Absolute Error\n\nMeasures how different actual sensor readings are from predicted "normal" values:\n- Low MAE → Normal operation\n- High MAE → Anomaly detected';
  }

  // Help
  if (q.includes('help') || q.includes('what can you')) {
    return '💬 **I can help you with:**\n\n**Data Queries:**\n- Show statistics\n- Latest anomaly\n- Current status\n\n**General Questions:**\n- What is GUARD?\n- How does it work?\n- Explain MAE\n- Tell me about sensors\n\nJust ask me anything! 😊';
  }

  // Default
  return '👋 I\'m GUARD Assistant! Ask me:\n\n**About GUARD:**\n- What is GUARD?\n- How does it work?\n- Tell me about sensors\n\n**About Data:**\n- Show statistics\n- Latest anomaly\n- Current status';
}
