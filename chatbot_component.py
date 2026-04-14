"""
GUARD Chatbot Component
Floating modal chatbot that can answer general questions and query data
"""

import streamlit as st
from datetime import datetime
import pandas as pd


def initialize_chatbot():
    """Initialize chatbot session state"""
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {
                'role': 'assistant',
                'content': '👋 Hi! I\'m GUARD Assistant. Ask me anything about the system or your data!',
                'timestamp': datetime.now().strftime('%H:%M')
            }
        ]
    if 'chat_input_key' not in st.session_state:
        st.session_state.chat_input_key = 0


def query_data_with_natural_language(query: str, data: pd.DataFrame) -> str:
    """Process natural language query about the data"""
    query_lower = query.lower()

    try:
        # Statistics queries
        if "statistic" in query_lower or "summary" in query_lower or "overview" in query_lower:
            total = len(data)
            anomalies = len(data[data['status'] == 'ANOMALY'])
            normal = len(data[data['status'] == 'NORMAL'])
            total_gas_loss = data[data['status'] == 'ANOMALY']['Gas_Loss_MMSCF'].sum()

            return f"""📊 **Data Summary:**
- Total records: {total:,}
- Anomalies: {anomalies:,} ({anomalies/total*100:.1f}%)
- Normal: {normal:,} ({normal/total*100:.1f}%)
- Total gas loss: {total_gas_loss:.3f} MMSCF
- Date range: {data.index.min()} to {data.index.max()}"""

        # Top anomalies
        elif "top" in query_lower and ("anomal" in query_lower or "mae" in query_lower):
            import re
            numbers = re.findall(r'\d+', query_lower)
            n = int(numbers[0]) if numbers else 5

            anomalies = data[data['status'] == 'ANOMALY'].nlargest(n, 'MAE')
            result = f"🔝 **Top {n} Anomalies by MAE:**\n\n"
            for idx, (timestamp, row) in enumerate(anomalies.iterrows(), 1):
                result += f"{idx}. {timestamp.strftime('%Y-%m-%d %H:%M')} - MAE: {row['MAE']:.4f}\n"
            return result

        # Latest anomaly
        elif "latest" in query_lower or "recent" in query_lower or "last" in query_lower:
            anomalies = data[data['status'] == 'ANOMALY']
            if len(anomalies) > 0:
                latest = anomalies.iloc[-1]
                return f"""🕐 **Latest Anomaly:**
- Timestamp: {latest.name.strftime('%Y-%m-%d %H:%M:%S')}
- MAE: {latest['MAE']:.4f}
- Gas Loss: {latest['Gas_Loss_MMSCF']:.4f} MMSCF"""

        # Current status
        elif "current" in query_lower or "now" in query_lower or "status" in query_lower:
            if len(data) > 0:
                current = data.iloc[-1]
                return f"""⚡ **Current Status:**
- Time: {current.name.strftime('%Y-%m-%d %H:%M:%S')}
- Status: {current['status']}
- MAE: {current['MAE']:.4f}
- Flow Rate: {current['Flow_Rate']:.2f} MMSCFD"""

        else:
            return "🤔 I can help you with:\n- Statistics and summaries\n- Top anomalies\n- Latest anomalies\n- Current status\n\nTry: 'Show me statistics' or 'Top 5 anomalies'"

    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_general_chat_response(query: str) -> str:
    """Get response for general chat questions"""
    query_lower = query.lower()

    if "what is guard" in query_lower or "about guard" in query_lower:
        return """🛡️ **GUARD** = Generative Understanding for Anomaly Response & Detection

An advanced system for monitoring BOOSTER COMPRESSOR B at CPP Donggi using LSTM anomaly detection and comprehensive RCA."""

    elif "how does it work" in query_lower or "how it works" in query_lower:
        return """⚙️ **How GUARD Works:**

1. Monitors 5 sensors continuously
2. LSTM compares actual vs predicted values
3. Detects anomalies when MAE exceeds threshold
4. Generates RCA report by division
5. Sends email alerts with PDF"""

    elif "help" in query_lower or "what can you do" in query_lower:
        return """💬 **I can help you with:**

**Data Queries:**
- Show statistics
- Top anomalies
- Latest anomaly
- Current status

**General Questions:**
- What is GUARD?
- How does it work?
- Explain MAE
- Tell me about sensors

Just ask me anything! 😊"""

    elif "mae" in query_lower and ("what" in query_lower or "explain" in query_lower):
        return """📊 **MAE** = Mean Absolute Error

Measures how different actual sensor readings are from predicted "normal" values:
- Low MAE → Normal operation
- High MAE → Anomaly detected"""

    elif "sensor" in query_lower:
        return """📡 **Monitored Sensors:**

1. FI1001B - Flow Rate (MMSCFD)
2. PI1001B - Suction Pressure (barg)
3. PI1004B - Discharge Pressure (barg)
4. TI1003B - Suction Temperature (°C)
5. TI1004B - Discharge Temperature (°C)"""

    else:
        return """👋 I'm GUARD Assistant! Ask me:

**About GUARD:**
- What is GUARD?
- How does it work?
- Tell me about sensors

**About Data:**
- Show statistics
- Top 5 anomalies
- Latest anomaly
- Current status"""


def render_chatbot():
    """Render floating chatbot button and modal"""
    initialize_chatbot()

    # Floating button CSS
    st.markdown("""
        <style>
        /* Float button container at bottom right */
        .floating-chat-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 999999;
        }

        .stButton button[kind="secondary"] {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            font-size: 35px;
            transition: all 0.3s ease;
            animation: pulse-animation 2s infinite;
        }

        .stButton button[kind="secondary"]:hover {
            transform: scale(1.15);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.9);
        }

        @keyframes pulse-animation {
            0%, 100% { box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6); }
            50% { box-shadow: 0 8px 35px rgba(102, 126, 234, 1); }
        }

        /* Modal overlay */
        .chat-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            z-index: 1000000;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Modal container */
        .chat-modal {
            background: white;
            border-radius: 20px;
            width: 90%;
            max-width: 500px;
            height: 75vh;
            max-height: 700px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* Chat header */
        .chat-modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Messages */
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }

        .message-bubble {
            margin: 10px 0;
            padding: 12px 18px;
            border-radius: 18px;
            max-width: 75%;
            word-wrap: break-word;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .user-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            border-radius: 18px 18px 5px 18px;
        }

        .bot-bubble {
            background: white;
            color: #333;
            margin-right: auto;
            border: 1px solid #e0e0e0;
            border-radius: 18px 18px 18px 5px;
        }

        .message-time {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Show floating button OR modal (not both)
    if not st.session_state.chat_open:
        # Floating button
        st.markdown('<div class="floating-chat-button">', unsafe_allow_html=True)
        if st.button("💬", key="chat_toggle", type="secondary", help="Chat with GUARD Assistant"):
            st.session_state.chat_open = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Modal popup
        st.markdown('<div class="chat-modal-overlay">', unsafe_allow_html=True)
        st.markdown('<div class="chat-modal">', unsafe_allow_html=True)

        # Header
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown("### 🛡️ GUARD Assistant")
        with col2:
            if st.button("✕", key="close_chat", help="Close"):
                st.session_state.chat_open = False
                st.rerun()

        st.divider()

        # Messages
        for msg in st.session_state.chat_messages:
            if msg['role'] == 'user':
                st.markdown(f"""
                    <div class="message-bubble user-bubble">
                        {msg['content']}
                        <div class="message-time">{msg['timestamp']}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="message-bubble bot-bubble">
                        {msg['content']}
                        <div class="message-time">{msg['timestamp']}</div>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()

        # Input
        col1, col2, col3 = st.columns([6, 1, 1])

        with col1:
            user_input = st.text_input("", key=f"chat_input_{st.session_state.chat_input_key}",
                                      placeholder="Type your message...", label_visibility="collapsed")

        with col2:
            send = st.button("📤", key="send_btn", use_container_width=True)

        with col3:
            clear = st.button("🗑️", key="clear_btn", use_container_width=True)

        # Handle input
        if send and user_input:
            # Add user message
            st.session_state.chat_messages.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().strftime('%H:%M')
            })

            # Generate response
            if st.session_state.get('full_data') is not None:
                response = query_data_with_natural_language(user_input, st.session_state.full_data)
                if "can help you with" in response:
                    response = get_general_chat_response(user_input)
            else:
                response = get_general_chat_response(user_input)

            # Add bot response
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().strftime('%H:%M')
            })

            st.session_state.chat_input_key += 1
            st.rerun()

        if clear:
            st.session_state.chat_messages = [{
                'role': 'assistant',
                'content': '👋 Chat cleared! How can I help you?',
                'timestamp': datetime.now().strftime('%H:%M')
            }]
            st.session_state.chat_input_key += 1
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
