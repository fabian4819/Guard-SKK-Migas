'use client';

import { useState } from 'react';
import { MessageCircle, X, Send, Trash2 } from 'lucide-react';
import { SensorData } from '@/types';

// Simple markdown renderer for chat messages
function renderMarkdown(text: string) {
  let html = text;

  // Bold text: **text** -> <strong>text</strong>
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Bullet points: - item -> • item
  html = html.replace(/^- (.*)/gm, '• $1');

  // Newlines
  html = html.replace(/\n/g, '<br/>');

  return html;
}

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
      content: '👋 Halo! Saya Asisten GUARD, didukung oleh AI. Saya memiliki pengetahuan mendalam tentang sistem GUARD, semua 32 skenario RCA, dan dapat membantu Anda menganalisis anomali. Tanyakan apa saja tentang sistem atau data Anda!',
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');

    // Add thinking indicator
    const thinkingMessage: Message = {
      role: 'assistant',
      content: '🤔 Sedang berpikir...',
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, thinkingMessage]);

    try {
      // Call AI API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: updatedMessages.map((m) => ({ role: m.role, content: m.content })),
          sensorData: data,
        }),
      });

      const result = await response.json();

      if (result.success) {
        const botMessage: Message = {
          role: 'assistant',
          content: result.message,
          timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        };
        // Replace thinking message with actual response
        setMessages((prev) => [...prev.slice(0, -1), botMessage]);
      } else {
        // Error handling - fallback to local response
        const fallbackResponse = generateResponse(input, data);
        const botMessage: Message = {
          role: 'assistant',
          content: fallbackResponse,
          timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev.slice(0, -1), botMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      // Fallback to local response on error
      const fallbackResponse = generateResponse(input, data);
      const botMessage: Message = {
        role: 'assistant',
        content: fallbackResponse,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev.slice(0, -1), botMessage]);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        role: 'assistant',
        content: '👋 Percakapan dibersihkan! Saya siap membantu Anda dengan analisis RCA, penjelasan anomali, kueri data sensor, atau pertanyaan tentang sistem GUARD.',
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
                <h3 className="text-xl font-bold">GUARD Assistant</h3>
                <p className="text-sm opacity-90">RCA Expert • Real-time Analysis</p>
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
                    <div
                      className="text-sm leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }}
                      style={{
                        wordWrap: 'break-word',
                        overflowWrap: 'break-word',
                      }}
                    />
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

// Fallback response generator (used when AI API is unavailable)
function generateResponse(query: string, data?: SensorData[]): string {
  const q = query.toLowerCase();

  // About GUARD
  if (q.includes('apa itu guard') || q.includes('tentang guard') || q.includes('what is guard')) {
    return '🛡️ **GUARD** = Generative Understanding for Anomaly Response & Detection\n\nSistem canggih untuk memantau KOMPRESOR PENAMBAH B di CPP Donggi menggunakan deteksi anomali LSTM dan RCA komprehensif.';
  }

  // How it works
  if ((q.includes('bagaimana') || q.includes('cara')) && (q.includes('kerja') || q.includes('work'))) {
    return '⚙️ **Cara Kerja GUARD:**\n\n1. Memantau 5 sensor secara terus-menerus\n2. LSTM membandingkan nilai aktual vs prediksi\n3. Mendeteksi anomali ketika MAE melebihi ambang batas\n4. Menghasilkan laporan RCA berdasarkan divisi\n5. Mengirim email peringatan dengan PDF';
  }

  // Statistics
  if (data && (q.includes('statistik') || q.includes('ringkasan') || q.includes('statistic') || q.includes('summary'))) {
    const total = data.length;
    const anomalies = data.filter((d) => d.status === 'ANOMALY').length;
    const normal = total - anomalies;
    const totalGasLoss = data
      .filter((d) => d.status === 'ANOMALY')
      .reduce((sum, d) => sum + d.Gas_Loss_MMSCF, 0);

    return `📊 **Ringkasan Data:**\n- Total rekaman: ${total.toLocaleString()}\n- Anomali: ${anomalies.toLocaleString()} (${(
      (anomalies / total) *
      100
    ).toFixed(1)}%)\n- Normal: ${normal.toLocaleString()} (${((normal / total) * 100).toFixed(
      1
    )}%)\n- Total kehilangan gas: ${totalGasLoss.toFixed(3)} MMSCF`;
  }

  // Latest anomaly
  if (data && (q.includes('terbaru') || q.includes('terakhir') || q.includes('latest') || q.includes('recent'))) {
    const anomalies = data.filter((d) => d.status === 'ANOMALY');
    if (anomalies.length > 0) {
      const latest = anomalies[anomalies.length - 1];
      return `🕐 **Anomali Terbaru:**\n- Waktu: ${latest.datetime}\n- MAE: ${latest.MAE.toFixed(
        4
      )}\n- Kehilangan Gas: ${latest.Gas_Loss_MMSCF.toFixed(4)} MMSCF`;
    }
    return 'Belum ada anomali yang terdeteksi.';
  }

  // Sensors
  if (q.includes('sensor')) {
    return '📡 **Sensor yang Dipantau:**\n\n1. FI1001B - Laju Alir (MMSCFD)\n2. PI1001B - Tekanan Hisap (barg)\n3. PI1004B - Tekanan Buang (barg)\n4. TI1003B - Suhu Hisap (°C)\n5. TI1004B - Suhu Buang (°C)';
  }

  // MAE explanation
  if (q.includes('mae') && (q.includes('apa') || q.includes('jelaskan') || q.includes('what') || q.includes('explain'))) {
    return '📊 **MAE** = Mean Absolute Error (Kesalahan Absolut Rata-rata)\n\nMengukur seberapa berbeda pembacaan sensor aktual dari nilai "normal" yang diprediksi:\n- MAE Rendah → Operasi normal\n- MAE Tinggi → Anomali terdeteksi';
  }

  // Help
  if (q.includes('bantuan') || q.includes('help') || q.includes('bisa')) {
    return '💬 **Saya dapat membantu Anda dengan:**\n\n**Kueri Data:**\n- Tampilkan statistik\n- Anomali terbaru\n- Status saat ini\n\n**Pertanyaan Umum:**\n- Apa itu GUARD?\n- Bagaimana cara kerjanya?\n- Jelaskan MAE\n- Tentang sensor\n\nTanyakan apa saja! 😊';
  }

  // Default
  return '👋 Saya Asisten GUARD! Tanyakan:\n\n**Tentang GUARD:**\n- Apa itu GUARD?\n- Bagaimana cara kerjanya?\n- Tentang sensor\n\n**Tentang Data:**\n- Tampilkan statistik\n- Anomali terbaru\n- Status saat ini';
}
