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

# Title
st.title("🛡️ GUARD Live Simulation - CPP Donggi")
st.caption("**Generative Understanding for Anomaly Response & Detection**")
st.subheader("BOOSTER COMPRESSOR B CPP DONGGI")

# Sidebar
with st.sidebar:
    st.header("⚙️ Live Demo Settings")

    st.subheader("📅 Simulation Period")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime(2025, 8, 7),
            min_value=datetime(2025, 1, 1),
            max_value=datetime(2025, 12, 31),
            key="start"
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime(2025, 8, 15),
            min_value=datetime(2025, 1, 1),
            max_value=datetime(2025, 12, 31),
            key="end"
        )

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
    **Period:** {start_date} to {end_date}

    **How it works:**
    1. Click ▶️ Start
    2. Data plays forward in time
    3. Charts update live
    4. Anomalies detected → Alert + Email

    **Speed:** {speed_label}
    """)

# Load processed data
@st.cache_data
def load_processed_data(start_date, end_date):
    """Load real test data from notebook (NORMAL + ANOMALY)"""
    from pathlib import Path

    # Use actual test dataset from notebook
    DATA_DIR = Path(__file__).parent / "KODE_FIX" / "KODE FIX"
    df = pd.read_csv(DATA_DIR / "AnomalyDetected_Test.csv", parse_dates=['datetime'])
    df = df.set_index('datetime')

    # Filter to date range
    mask = (df.index.date >= start_date) & (df.index.date <= end_date)
    filtered = df[mask].copy()

    return filtered

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
        with st.spinner("📂 Loading processed data..."):
            try:
                processed_data = load_processed_data(start_date, end_date)

                if len(processed_data) == 0:
                    st.error(f"No data available for {start_date} to {end_date}")
                    st.session_state.simulation_running = False
                    st.stop()

                st.session_state.full_data = processed_data

                # Count statuses
                anomaly_count = len(processed_data[processed_data['status'] == 'ANOMALY'])
                normal_count = len(processed_data[processed_data['status'] == 'NORMAL'])
                total = len(processed_data)
                anomaly_rate = (anomaly_count / total * 100) if total > 0 else 0

                st.success(f"✅ Loaded {total:,} data points: {normal_count:,} normal ({100-anomaly_rate:.1f}%), {anomaly_count:,} anomalies ({anomaly_rate:.1f}%)")
                st.info("ℹ️ Using real test data from training notebook")
                time.sleep(1)

            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                st.exception(e)
                st.session_state.simulation_running = False
                st.stop()

    # Simulation loop
    if st.session_state.simulation_running:

        data = st.session_state.full_data

        while (st.session_state.current_index < len(data) and
               st.session_state.simulation_running):

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

            # Rerun to update display
            st.rerun()

        # Simulation complete
        if st.session_state.current_index >= len(data):
            st.session_state.simulation_running = False
            st.success("✅ Simulation Complete!")
            st.balloons()

else:
    # Not running - show instructions
    st.info("""
    ### 🎬 Live Demonstration Mode

    **How to use:**

    1. **Select date range** in sidebar (e.g., Aug 7-15, 2025)
    2. **Choose playback speed** (Maximum Speed recommended for demo)
    3. **Enable email alerts** if desired
    4. **Click ▶️ Start** to begin live simulation

    **What happens:**
    - Data plays forward in real-time
    - Charts update live as time progresses
    - Anomalies detected automatically
    - Email alerts sent instantly when anomaly found
    - See the entire period unfold before your eyes!

    **Tip:** Use Maximum Speed to see results quickly, or Real-time for dramatic effect.
    """)

st.divider()
st.caption("GUARD (Generative Understanding for Anomaly Response & Detection) | Real historical data, simulated live playback")

# Render floating chatbot
render_chatbot()
