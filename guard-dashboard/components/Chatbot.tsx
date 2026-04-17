'use client';

import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Trash2, Bot, User, Sparkles, ChevronDown, Maximize2, Minimize2 } from 'lucide-react';
import { SensorData } from '@/types';

// Simple markdown renderer for chat messages
function renderMarkdown(text: string) {
  let html = text;

  // Code blocks: ```code``` -> <pre>code</pre>
  html = html.replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 p-2 rounded my-2 font-mono text-xs overflow-x-auto">$1</pre>');

  // Bold text: **text** -> <strong>text</strong>
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-blue-700">$1</strong>');

  // Bullet points: - item -> • item
  html = html.replace(/^- (.*)/gm, '<li class="ml-4 list-disc">$1</li>');
  if (html.includes('<li')) {
    // Wrap groups of li in ul if needed, but this is simple
  }

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
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '👋 **Halo! Saya Asisten GUARD.**\n\nSaya didukung oleh AI untuk membantu Anda memantau sistem. Saya memiliki pengetahuan mendalam tentang:\n- Semua 32 skenario RCA\n- Analisis anomali LSTM\n- Data sensor real-time\n\nApa yang bisa saya bantu hari ini?',
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    // Add thinking indicator
    const thinkingMessage: Message = {
      role: 'assistant',
      content: '✨ Sedang menganalisis...',
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
        setMessages((prev) => [...prev.slice(0, -1), botMessage]);
      } else {
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
      const fallbackResponse = generateResponse(input, data);
      const botMessage: Message = {
        role: 'assistant',
        content: fallbackResponse,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev.slice(0, -1), botMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        role: 'assistant',
        content: '🧹 **Percakapan dibersihkan!**\n\nSaya siap membantu Anda kembali dengan analisis RCA atau kueri data sensor GUARD.',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  const suggestions = [
    "Tampilkan statistik",
    "Anomali terbaru",
    "Jelaskan MAE",
    "Sensor yang dipantau"
  ];

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-tr from-blue-700 via-blue-600 to-indigo-600 text-white rounded-full shadow-[0_8px_30px_rgb(0,0,0,0.12)] border-2 border-white/20 hover:scale-105 active:scale-95 transition-all z-50 flex items-center justify-center group"
          aria-label="Open chat"
        >
          <div className="absolute inset-0 rounded-full bg-blue-400 blur-sm opacity-0 group-hover:opacity-40 transition-opacity animate-pulse"></div>
          <MessageCircle size={30} className="relative z-10" />
        </button>
      )}

      {/* Chat Modal */}
      {isOpen && (
        <div className={`fixed z-50 transition-all duration-300 ease-in-out flex flex-col shadow-2xl overflow-hidden
          ${isMinimized 
            ? 'bottom-6 right-6 w-72 h-14' 
            : 'bottom-6 right-6 w-[400px] h-[650px] max-h-[calc(100vh-40px)] rounded-2xl border border-gray-100'
          } bg-white`}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-700 to-indigo-700 text-white px-4 py-3 flex items-center justify-between shrink-0 cursor-pointer"
               onClick={() => isMinimized && setIsMinimized(false)}>
            <div className="flex items-center gap-3">
              <div>
                <h3 className="text-sm font-bold tracking-tight">GUARD AI Assistant</h3>
                {!isMinimized && (
                  <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                    <span className="text-[10px] uppercase tracking-wider font-semibold opacity-80">Online • RCA Specialist</span>
                  </div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={(e) => { e.stopPropagation(); setIsMinimized(!isMinimized); }}
                className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
                title={isMinimized ? "Expand" : "Minimize"}
              >
                {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}
                className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
                aria-label="Close chat"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages Container */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#f8fafc] scrollbar-thin scrollbar-thumb-gray-200">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex items-end gap-2 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                  >
                    {/* Avatar */}
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm
                      ${message.role === 'user' 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'bg-indigo-600 text-white'}`}
                    >
                      {message.role === 'user' ? <User size={14} /> : <Sparkles size={14} />}
                    </div>

                    <div
                      className={`max-w-[80%] px-4 py-3 rounded-2xl shadow-sm text-sm border
                        ${message.role === 'user'
                          ? 'bg-blue-600 text-white border-blue-500 rounded-br-none'
                          : 'bg-white text-gray-800 border-gray-100 rounded-bl-none'
                        }`}
                    >
                      <div
                        className="leading-relaxed"
                        dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }}
                      />
                      <p
                        className={`text-[10px] mt-2 font-medium ${
                          message.role === 'user' ? 'text-blue-10' : 'text-gray-400'
                        }`}
                      >
                        {message.timestamp}
                      </p>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Suggestions */}
              <div className="px-4 py-2 bg-[#f8fafc] border-t border-gray-100 overflow-x-auto whitespace-nowrap scrollbar-hide">
                <div className="flex gap-2">
                  {suggestions.map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => { setInput(suggestion); }}
                      className="inline-block px-3 py-1.5 bg-white border border-gray-200 hover:border-blue-300 hover:text-blue-600 rounded-full text-xs font-medium text-gray-600 transition-all shadow-sm active:scale-95"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>

              {/* Input Area */}
              <div className="p-4 bg-white border-t border-gray-100 shadow-[0_-4px_10px_rgba(0,0,0,0.02)]">
                <div className="flex gap-2 items-center bg-gray-50 border border-gray-200 rounded-xl p-1.5 focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-300 transition-all">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Tanya tentang anomali atau data..."
                    className="flex-1 bg-transparent px-3 py-2 text-sm focus:outline-none placeholder:text-gray-400"
                    disabled={isLoading}
                  />
                  <div className="flex gap-1">
                    <button
                      onClick={handleClear}
                      className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                      title="Bersihkan chat"
                    >
                      <Trash2 size={18} />
                    </button>
                    <button
                      onClick={handleSend}
                      disabled={!input.trim() || isLoading}
                      title="Kirim pesan"
                      className={`p-2 rounded-lg transition-all ${
                        input.trim() && !isLoading
                          ? 'bg-blue-600 text-white shadow-md'
                          : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      <Send size={18} />
                    </button>
                  </div>
                </div>
                <p className="text-[10px] text-center text-gray-400 mt-2">
                  GUARD AI can make mistakes. Verify important information.
                </p>
              </div>
            </>
          )}
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
