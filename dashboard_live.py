"""
i2AIMS Live Simulation Dashboard
Replays historical data in real-time with live charts and email alerts
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import time
import numpy as np
import os
from chatbot_component import render_chatbot

# Load environment variables for email
try:
    from dotenv import load_dotenv
    load_dotenv()
    EMAIL_CONFIGURED = bool(os.getenv('SMTP_USERNAME') and os.getenv('ALERT_TO'))
except:
    EMAIL_CONFIGURED = False

# Page config
st.set_page_config(
    page_title="GUARD Live Demo - CPP Donggi",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False
    st.session_state.current_index = 0
    st.session_state.data_buffer = []
    st.session_state.anomalies_detected = []
    st.session_state.emails_sent = []
    st.session_state.full_data = None
    st.session_state.simulation_speed = 1.0
    st.session_state.last_rerun_time = time.time()
    st.session_state.update_batch_size = 5  # Update UI every 5 data points

# Title
st.title("🛡️ GUARD Live Simulation - CPP Donggi")
st.caption("**Generative Understanding for Anomaly Response & Detection**")
st.subheader("BOOSTER COMPRESSOR B CPP DONGGI")

# Sidebar
with st.sidebar:
    st.header("⚙️ Live Demo Settings")

    st.subheader("📅 Data Source")
    st.info("**Test.xlsx**\n14/4/2026 00:00 - 00:53\n(54 minutes, looping)")

    st.divider()

    st.subheader("⚡ Playback Speed")
    speed_options = {
        "Real-time (1 data point per second)": 1.0,
        "2x Speed": 0.5,
        "5x Speed": 0.2,
        "10x Speed": 0.1,
        "Maximum Speed": 0.01
    }

    speed_label = st.selectbox(
        "Speed",
        list(speed_options.keys()),
        index=4  # Default to Maximum Speed
    )
    st.session_state.simulation_speed = speed_options[speed_label]

    st.divider()

    st.subheader("📧 Email Alerts")

    if EMAIL_CONFIGURED:
        enable_email = st.checkbox("Send Email Alerts", value=True)
        st.session_state.enable_email = enable_email  # Store in session state
        if enable_email:
            recipient = os.getenv('ALERT_TO', 'Not configured')
            st.caption(f"✅ Will send to: {recipient}")
    else:
        enable_email = st.checkbox("Send Email Alerts", value=False, disabled=True)
        st.session_state.enable_email = False
        st.warning("⚠️ Email not configured. Set SMTP settings in .env file.")

    st.divider()

    # Control buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Start", use_container_width=True, type="primary"):
            st.session_state.simulation_running = True
            st.session_state.current_index = 0
            st.session_state.data_buffer = []
            st.session_state.anomalies_detected = []
            st.session_state.emails_sent = []

    with col2:
        if st.button("⏸️ Stop", use_container_width=True):
            st.session_state.simulation_running = False

    st.divider()

    if st.session_state.simulation_running:
        st.success("🔴 LIVE - Simulation Running")
    else:
        st.info("⏹️ Simulation Stopped")

    st.divider()

    st.caption(f"""
    **Data:** Test.xlsx (14/4/2026 00:00-00:53)
    **Mode:** Infinite Loop

    **How it works:**
    1. Click ▶️ Start
    2. Data plays forward (54 min loop)
    3. Charts update live
    4. Anomalies detected → Alert + Email
    5. Loops back to start automatically

    **Speed:** {speed_label}
    """)

# Load processed data
@st.cache_data
def load_processed_data():
    """Load real-time test data from Test.xlsx (14/4/2026 00:00 - 00:53)"""
    from pathlib import Path

    # Load Test.xlsx
    xlsx_path = Path(__file__).parent / "Test.xlsx"
    df = pd.read_excel(xlsx_path)

    # Parse datetime column
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d/%m/%Y %H:%M:%S')
    df = df.set_index('Datetime')

    # Add status column (mock anomaly detection for demo)
    # Mark as ANOMALY if any sensor reading is outside normal ranges
    df['status'] = 'NORMAL'
    df['MAE'] = np.random.uniform(0.5, 2.0, len(df))  # Mock MAE values

    # Simple anomaly detection based on thresholds
    anomaly_mask = (
        (df['Flow_Rate'] < 45) | (df['Flow_Rate'] > 56) |
        (df['Suction_Pressure'] < 33) | (df['Suction_Pressure'] > 34) |
        (df['Discharge_Pressure'] < 60) | (df['Discharge_Pressure'] > 63.3) |
        (df['Suction_Temperature'] < 90) | (df['Suction_Temperature'] > 100) |
        (df['Discharge_Temperature'] < 189) | (df['Discharge_Temperature'] > 205)
    )

    df.loc[anomaly_mask, 'status'] = 'ANOMALY'
    df.loc[anomaly_mask, 'MAE'] = np.random.uniform(3.0, 8.0, anomaly_mask.sum())

    # Add other required columns
    df['threshold_ratio'] = np.where(df['status'] == 'ANOMALY',
                                      np.random.uniform(110, 150, len(df)),
                                      np.random.uniform(50, 95, len(df)))
    df['Gas_Loss_MMSCF'] = np.where(df['status'] == 'ANOMALY',
                                     np.random.uniform(0.001, 0.01, len(df)),
                                     0)

    # Add deviation and contribution columns (required by email notifier)
    sensors = {
        'Flow_Rate': {'low': 45, 'high': 56},
        'Suction_Pressure': {'low': 33, 'high': 34},
        'Discharge_Pressure': {'low': 60, 'high': 63.3},
        'Suction_Temperature': {'low': 90, 'high': 100},
        'Discharge_Temperature': {'low': 189, 'high': 205},
    }

    for param, config in sensors.items():
        expected = (config['low'] + config['high']) / 2
        df[f'dev_{param}'] = df[param] - expected
        dev_pct = (df[f'dev_{param}'] / expected * 100)
        df[f'contrib_{param}'] = abs(dev_pct) / sum(
            abs((df[p] - ((sensors[p]['low'] + sensors[p]['high']) / 2)) /
                ((sensors[p]['low'] + sensors[p]['high']) / 2) * 100)
            for p in sensors.keys()
        ) * 100

    return df

# Main content
st.divider()

# Status bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    current_time = st.empty()
    if not st.session_state.simulation_running:
        current_time.metric("Current Time", "Not Started")
with col2:
    points_processed = st.empty()
    if not st.session_state.simulation_running:
        points_processed.metric("Points Processed", "0")
with col3:
    anomalies_count = st.empty()
    if not st.session_state.simulation_running:
        anomalies_count.metric("Anomalies Detected", "0")
with col4:
    emails_count = st.empty()
    if not st.session_state.simulation_running:
        emails_count.metric("Emails Sent", "0")

st.divider()

# Create placeholders for live updating charts
chart_placeholder = st.empty()
sensor_chart_placeholder = st.empty()

st.divider()

# Alert log
alert_placeholder = st.empty()

# Simulation logic
if st.session_state.simulation_running or len(st.session_state.data_buffer) > 0:

    # Load processed data if not already loaded
    if st.session_state.full_data is None:
        with st.spinner("📂 Loading Test.xlsx data..."):
            try:
                processed_data = load_processed_data()

                if len(processed_data) == 0:
                    st.error("No data available in Test.xlsx")
                    st.session_state.simulation_running = False
                    st.stop()

                st.session_state.full_data = processed_data

                # Count statuses (silent load - no messages displayed)
                anomaly_count = len(processed_data[processed_data['status'] == 'ANOMALY'])
                normal_count = len(processed_data[processed_data['status'] == 'NORMAL'])
                total = len(processed_data)
                anomaly_rate = (anomaly_count / total * 100) if total > 0 else 0

                # Data loaded silently - removed display messages
                time.sleep(0.5)

            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                st.exception(e)
                st.session_state.simulation_running = False
                st.stop()

    # Simulation loop
    if st.session_state.simulation_running:

        data = st.session_state.full_data

        # Infinite loop with data wraparound
        while st.session_state.simulation_running:

            # Loop back to start if we reached the end
            if st.session_state.current_index >= len(data):
                st.session_state.current_index = 0
                st.info("🔄 Looping back to start...")
                time.sleep(0.5)

            # Get current row
            current_row = data.iloc[st.session_state.current_index]
            current_timestamp = data.index[st.session_state.current_index]

            # Add to buffer
            st.session_state.data_buffer.append({
                'timestamp': current_timestamp,
                'MAE': current_row['MAE'],
                'status': current_row['status'],
                'Flow_Rate': current_row.get('Flow_Rate', 0),
                'Suction_Pressure': current_row.get('Suction_Pressure', 0),
                'Discharge_Pressure': current_row.get('Discharge_Pressure', 0),
                'Suction_Temperature': current_row.get('Suction_Temperature', 0),
                'Discharge_Temperature': current_row.get('Discharge_Temperature', 0),
                'threshold_ratio': current_row.get('threshold_ratio', 0),
                'Gas_Loss_MMSCF': current_row.get('Gas_Loss_MMSCF', 0),
                # Deviation and contribution columns for email notifier
                'dev_Flow_Rate': current_row.get('dev_Flow_Rate', 0),
                'dev_Suction_Pressure': current_row.get('dev_Suction_Pressure', 0),
                'dev_Discharge_Pressure': current_row.get('dev_Discharge_Pressure', 0),
                'dev_Suction_Temperature': current_row.get('dev_Suction_Temperature', 0),
                'dev_Discharge_Temperature': current_row.get('dev_Discharge_Temperature', 0),
                'contrib_Flow_Rate': current_row.get('contrib_Flow_Rate', 0),
                'contrib_Suction_Pressure': current_row.get('contrib_Suction_Pressure', 0),
                'contrib_Discharge_Pressure': current_row.get('contrib_Discharge_Pressure', 0),
                'contrib_Suction_Temperature': current_row.get('contrib_Suction_Temperature', 0),
                'contrib_Discharge_Temperature': current_row.get('contrib_Discharge_Temperature', 0),
            })

            # Check for anomaly
            if current_row['status'] == 'ANOMALY':
                anomaly_info = {
                    'timestamp': current_timestamp,
                    'MAE': current_row['MAE'],
                    'threshold_ratio': current_row.get('threshold_ratio', 0),
                    'gas_loss': current_row.get('Gas_Loss_MMSCF', 0)
                }
                st.session_state.anomalies_detected.append(anomaly_info)

                # Send email alert for each anomaly (or limit if too many)
                should_email = (
                    st.session_state.get('enable_email', False) and
                    len(st.session_state.emails_sent) < 20  # Limit to 20 emails max
                )

                # Debug: Always add to emails_sent to show attempt
                if should_email:
                    import sys
                    try:
                        # Load environment variables
                        from dotenv import load_dotenv
                        load_dotenv()

                        # Debug info
                        smtp_user = os.getenv('SMTP_USERNAME')
                        alert_to = os.getenv('ALERT_TO')

                        if not smtp_user or not alert_to:
                            st.session_state.emails_sent.append({
                                'timestamp': current_timestamp,
                                'status': 'Config Missing',
                                'MAE': current_row['MAE']
                            })
                        else:
                            from email_notifier import send_email_alert

                            # Try to send email
                            success = send_email_alert(current_row)

                            email_status = 'Sent' if success else 'Send Failed'
                            st.session_state.emails_sent.append({
                                'timestamp': current_timestamp,
                                'status': email_status,
                                'MAE': current_row['MAE']
                            })

                    except ImportError as e:
                        st.session_state.emails_sent.append({
                            'timestamp': current_timestamp,
                            'status': f'Import Err',
                            'MAE': current_row['MAE']
                        })
                    except Exception as e:
                        error_msg = str(e)[:50]
                        st.session_state.emails_sent.append({
                            'timestamp': current_timestamp,
                            'status': f'Err: {error_msg}',
                            'MAE': current_row['MAE']
                        })
                else:
                    # Debug: show why email not attempted
                    if not st.session_state.get('enable_email', False):
                        reason = 'Disabled'
                    elif len(st.session_state.emails_sent) >= 20:
                        reason = 'Limit Reached'
                    else:
                        reason = 'Unknown'

                    st.session_state.emails_sent.append({
                        'timestamp': current_timestamp,
                        'status': f'Not Sent: {reason}',
                        'MAE': current_row['MAE']
                    })

            # Update status
            current_time.metric("Current Time", current_timestamp.strftime("%Y-%m-%d %H:%M"))
            points_processed.metric("Points Processed", f"{st.session_state.current_index + 1:,}")
            anomalies_count.metric("Anomalies Detected", len(st.session_state.anomalies_detected))
            emails_count.metric("Emails Sent", len([e for e in st.session_state.emails_sent if e['status'] == 'Sent']))

            # Update charts
            if len(st.session_state.data_buffer) > 0:
                buffer_df = pd.DataFrame(st.session_state.data_buffer)
                buffer_df['timestamp'] = pd.to_datetime(buffer_df['timestamp'])

                # MAE Timeline Chart
                with chart_placeholder.container():
                    fig = go.Figure()

                    # MAE line
                    fig.add_trace(go.Scatter(
                        x=buffer_df['timestamp'],
                        y=buffer_df['MAE'],
                        mode='lines',
                        name='MAE',
                        line=dict(color='#1976d2', width=2)
                    ))

                    # Anomalies
                    anomalies_df = buffer_df[buffer_df['status'] == 'ANOMALY']
                    if len(anomalies_df) > 0:
                        fig.add_trace(go.Scatter(
                            x=anomalies_df['timestamp'],
                            y=anomalies_df['MAE'],
                            mode='markers',
                            name='Anomaly',
                            marker=dict(color='#f44336', size=10, symbol='x')
                        ))

                    # Current position marker
                    fig.add_scatter(
                        x=[current_timestamp],
                        y=[buffer_df['MAE'].iloc[-1]],
                        mode='markers+text',
                        marker=dict(color='green', size=15, symbol='triangle-up'),
                        text=['NOW'],
                        textposition='top center',
                        showlegend=False,
                        name='Current'
                    )

                    fig.update_layout(
                        title="📈 Live Anomaly Detection",
                        xaxis_title="Time",
                        yaxis_title="MAE",
                        height=350,
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                # Sensor Charts
                with sensor_chart_placeholder.container():
                    fig = go.Figure()

                    sensors = ['Flow_Rate', 'Suction_Pressure', 'Discharge_Pressure',
                              'Suction_Temperature', 'Discharge_Temperature']
                    colors = ['#1976d2', '#ff9800', '#4caf50', '#9c27b0', '#f44336']

                    for i, sensor in enumerate(sensors):
                        fig.add_trace(go.Scatter(
                            x=buffer_df['timestamp'],
                            y=buffer_df[sensor],
                            mode='lines',
                            name=sensor.replace('_', ' '),
                            line=dict(color=colors[i], width=2)
                        ))

                    # Current position marker (use last value from each sensor)
                    last_idx = len(buffer_df) - 1
                    fig.add_scatter(
                        x=[current_timestamp],
                        y=[buffer_df['Flow_Rate'].iloc[last_idx]],
                        mode='markers',
                        marker=dict(color='green', size=12, symbol='diamond'),
                        showlegend=False,
                        name='Current Position'
                    )

                    fig.update_layout(
                        title="📊 Live Sensor Readings",
                        xaxis_title="Time",
                        yaxis_title="Value",
                        height=350,
                        hovermode='x unified',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02)
                    )

                    st.plotly_chart(fig, use_container_width=True)

            # Show recent alerts
            with alert_placeholder.container():
                if len(st.session_state.anomalies_detected) > 0:
                    st.subheader("🚨 Recent Anomaly Alerts")

                    recent = st.session_state.anomalies_detected[-5:]  # Last 5

                    for alert in reversed(recent):
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                        with col1:
                            st.write(f"⚠️ **{alert['timestamp'].strftime('%Y-%m-%d %H:%M')}**")
                        with col2:
                            try:
                                mae_val = float(str(alert['MAE']).replace('%', ''))
                                st.write(f"MAE: {mae_val:.4f}")
                            except:
                                st.write(f"MAE: {alert['MAE']}")
                        with col3:
                            try:
                                ratio_str = str(alert['threshold_ratio']).replace('%', '')
                                ratio_val = float(ratio_str)
                                st.write(f"Ratio: {ratio_val:.1f}%")
                            except:
                                st.write(f"Ratio: {alert['threshold_ratio']}")
                        with col4:
                            # Check email status for this timestamp
                            email_status = None
                            for e in st.session_state.emails_sent:
                                if e['timestamp'] == alert['timestamp']:
                                    email_status = e['status']
                                    break

                            if email_status == 'Sent':
                                st.success("📧 Sent")
                            elif email_status:
                                st.error(f"📧 {email_status}")
                            else:
                                st.warning("📧 No Status")

                        st.divider()

            # Move to next point
            st.session_state.current_index += 1

            # Sleep based on speed
            time.sleep(st.session_state.simulation_speed)

            # Smart batching: Adjust update frequency based on simulation speed
            # Real-time (1.0s): Update every point (no batching needed)
            # Fast speeds (<0.5s): Batch updates to reduce chart re-rendering overhead
            if st.session_state.simulation_speed >= 0.5:
                # Real-time or slow speeds: Always update
                st.rerun()
            else:
                # Fast speeds: Batch updates every N points to prevent buffering
                if st.session_state.current_index % st.session_state.update_batch_size == 0:
                    st.rerun()

else:
    # Not running - show instructions
    st.info("""
    ### 🎬 Live Looping Demo Mode

    **How to use:**

    1. **Choose playback speed** in sidebar (Maximum Speed recommended)
    2. **Enable email alerts** if desired
    3. **Click ▶️ Start** to begin live simulation

    **What happens:**
    - Data from Test.xlsx plays forward (14/4/2026 00:00 - 00:53)
    - Charts update live as time progresses
    - Anomalies detected automatically
    - Email alerts sent when anomaly found
    - **Loops continuously** - when reaching 00:53, jumps back to 00:00
    - Runs infinitely until you click ⏸️ Stop

    **Data:** 54 minutes of real sensor data, repeating in a loop

    **Tip:** Use Maximum Speed to see results quickly, or Real-time for dramatic effect.
    """)

st.divider()
st.caption("GUARD (Generative Understanding for Anomaly Response & Detection)")

# Render floating chatbot
render_chatbot()
