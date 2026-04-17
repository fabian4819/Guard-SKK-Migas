# 🤖 AI-Powered GUARD Chatbot Guide

## ✨ What's New

The GUARD chatbot has been upgraded from simple keyword matching to a **fully AI-powered assistant** using **Groq (Llama 3.3 70B)**!

## 🧠 AI Capabilities

### 1. **Deep RCA Knowledge**
The chatbot now has complete knowledge of:
- **All 32 RCA scenarios** (ANML000-ANML031) across 5 divisions
- **Equipment specifications** (Booster Compressor B CPP Donggi)
- **Normal operating ranges** for all 5 sensors
- **Root causes and corrective actions** for every anomaly pattern

### 2. **Intelligent Conversations**
- Natural language understanding (not just keyword matching)
- Context-aware responses based on current sensor data
- Explains complex technical concepts in simple terms
- Provides safety-critical recommendations

### 3. **Real-time Data Analysis**
- Accesses live sensor readings
- Calculates statistics on the fly
- Identifies which RCA scenario matches current anomalies
- Suggests immediate actions for critical conditions

## 💬 Example Questions You Can Ask

### About RCA Scenarios
- "What does ANML001 mean?"
- "If discharge temperature is high but nothing else, what's the problem?"
- "Show me all critical scenarios"
- "What should I do if I see ANML031?"

### About Current Data
- "What's the current system status?"
- "Show me the latest anomaly"
- "How many anomalies have we detected today?"
- "Is the suction pressure normal?"
- "Calculate total gas loss"

### Technical Questions
- "Explain what causes discharge overheating"
- "Why is compression ratio important?"
- "What happens during surge?"
- "How does the anti-surge valve work?"

### Troubleshooting
- "Suction pressure is low and discharge temp is high, what's wrong?"
- "All sensors are showing anomalies, what should I do immediately?"
- "The compressor is making noise and temperature is rising"
- "How do I check if the dry gas seal is failing?"

## 🚀 How to Use

1. **Start the dashboard:**
   ```bash
   npm run dev
   ```

2. **Click the floating chatbot button** (bottom right, purple gradient with 💬)

3. **Ask anything!** The AI understands:
   - Technical questions
   - Data queries
   - RCA analysis requests
   - Troubleshooting scenarios

## 🔧 Technical Implementation

### Files Modified/Created
1. **`.env.local`** - Groq API credentials
2. **`lib/rcaContext.ts`** - Complete RCA knowledge base (32 scenarios)
3. **`app/api/chat/route.ts`** - API endpoint for AI chat
4. **`components/Chatbot.tsx`** - Updated to use AI API

### API Details
- **Model**: Llama 3.3 70B Versatile (via Groq)
- **Speed**: Ultra-fast (~1-2 seconds response time)
- **Context**: Full RCA knowledge + current sensor data
- **Fallback**: If AI fails, falls back to keyword matching

## 🎯 Key Features

### Smart Context Injection
The AI receives:
```
✅ All 32 RCA scenarios with symptoms and actions
✅ Normal ranges for all 5 sensors
✅ Current sensor readings with status indicators
✅ Real-time anomaly statistics
✅ Gas loss calculations
```

### Safety-First Responses
For critical scenarios (ANML007, ANML015, ANML031), the AI will:
- Flag them as HIGH RISK or CRITICAL
- Suggest IMMEDIATE or EMERGENCY actions
- Prioritize safety over optimization

### Conversation Memory
The chatbot remembers the conversation within a session, so you can:
- Ask follow-up questions
- Reference previous answers
- Build on context

## 🧪 Testing the Chatbot

### Test 1: RCA Knowledge
**Ask:** "What causes ANML005?"
**Expected:** Explanation of Discharge Pressure + Temperature anomaly, back-pressure issue

### Test 2: Data Query
**Ask:** "Show me statistics"
**Expected:** Total records, anomaly count, gas loss, date range

### Test 3: Critical Scenario
**Ask:** "What if all sensors show anomalies?"
**Expected:** Reference to ANML031, EMERGENCY response, ESD mention

### Test 4: Natural Language
**Ask:** "The temperature at discharge is super high but pressure is normal, what's going on?"
**Expected:** AI should identify ANML001 (mechanical friction/seal issue)

## 🆚 Before vs After

| Feature | Before | After |
|---------|--------|-------|
| **Intelligence** | Keyword matching | Full AI reasoning |
| **RCA Knowledge** | Hardcoded list | 32 scenarios with details |
| **Context Awareness** | None | Real-time sensor data |
| **Conversation** | One-shot responses | Memory + follow-ups |
| **Technical Depth** | Surface level | Expert-level analysis |
| **Response Quality** | Generic | Contextual + personalized |

## 📊 Performance

- **Response Time**: ~1-2 seconds (thanks to Groq's ultra-fast inference)
- **Accuracy**: High (Llama 3.3 70B is very capable)
- **Cost**: Very low (Groq offers generous free tier)

## 🔮 Future Enhancements

Potential additions:
- [ ] Voice input/output
- [ ] Multi-turn RCA troubleshooting wizard
- [ ] Predictive maintenance suggestions
- [ ] Historical pattern analysis
- [ ] Integration with email alert system
- [ ] Export chat history to PDF

## 🛠️ Troubleshooting

### Chatbot shows "Thinking..." forever
- Check if `.env.local` exists with correct `GROQ_API_KEY`
- Verify internet connection
- Check browser console for errors

### Responses are generic/fallback
- API might be down - chatbot falls back to keyword matching
- Check API key validity
- Verify Groq service status

### TypeScript errors
```bash
npm install --save-dev @types/node
```

## 📝 Notes

- The chatbot loads RCA context on every request (ensures always up-to-date)
- Sensor data is passed from the main page component
- Fallback mechanism ensures chatbot always works (even if AI fails)
- All 32 RCA scenarios are embedded in the system prompt

---

**Built with ❤️ using Groq AI, Llama 3.3 70B, Next.js, and comprehensive RCA knowledge**
