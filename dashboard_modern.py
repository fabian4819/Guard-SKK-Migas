"""
GUARD Modern Dashboard - LEADS-Inspired Design with Live Simulation
Professional interface with real-time looping data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import time
import os

# Load environment variables for email
try:
    from dotenv import load_dotenv
    load_dotenv()
    EMAIL_CONFIGURED = bool(os.getenv('SMTP_USERNAME') and os.getenv('ALERT_TO'))
except:
    EMAIL_CONFIGURED = False

# Page configuration
st.set_page_config(
    page_title="GUARD - Modern Dashboard",
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
    st.session_state.simulation_speed = 0.01
    st.session_state.selected_equipment = 'MTD-340-C1001B'
    st.session_state.show_detail_modal = False
    st.session_state.selected_anomaly = None

# Custom CSS for modern design
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title {
        color: #FFFFFF !important;
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: 0.15em;
        text-shadow: 3px 3px 8px rgba(0,0,0,0.5);
    }
    .header-subtitle {
        color: #FFFFFF !important;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    /* Stats card styling */
    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stats-value {
        color: #1e3c72;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .stats-value-danger {
        color: #f44336;
        font-size: 1.8rem;
        font-weight: 700;
    }

    /* Status metrics cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }
    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        color: #666;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        color: #1e3c72;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
    }
    .metric-value-warning {
        color: #ff9800;
    }
    .metric-value-danger {
        color: #f44336;
    }
    .metric-value-success {
        color: #4caf50;
    }
    /* Section header */
    .section-header {
        background: linear-gradient(90deg, #ff9800 0%, #f57c00 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 5px;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 1rem 0 0.5rem 0;
    }
    .section-header-green {
        background: linear-gradient(90deg, #4caf50 0%, #388e3c 100%);
    }
    .update-badge {
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load Test.xlsx data with anomaly detection"""
    xlsx_path = Path(__file__).parent / "Test.xlsx"
    df = pd.read_excel(xlsx_path)
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d/%m/%Y %H:%M:%S')
    df = df.set_index('Datetime')

    # Add status column (anomaly detection)
    df['status'] = 'NORMAL'
    df['MAE'] = np.random.uniform(0.5, 2.0, len(df))

    # Anomaly detection based on thresholds
    anomaly_mask = (
        (df['Flow_Rate'] < 45) | (df['Flow_Rate'] > 56) |
        (df['Suction_Pressure'] < 33) | (df['Suction_Pressure'] > 34) |
        (df['Discharge_Pressure'] < 60) | (df['Discharge_Pressure'] > 63.3) |
        (df['Suction_Temperature'] < 90) | (df['Suction_Temperature'] > 100) |
        (df['Discharge_Temperature'] < 189) | (df['Discharge_Temperature'] > 205)
    )

    df.loc[anomaly_mask, 'status'] = 'ANOMALY'
    df.loc[anomaly_mask, 'MAE'] = np.random.uniform(3.0, 8.0, anomaly_mask.sum())

    # Add threshold ratio and gas loss
    df['threshold_ratio'] = np.where(df['status'] == 'ANOMALY',
                                      np.random.uniform(110, 150, len(df)),
                                      np.random.uniform(50, 95, len(df)))
    df['Gas_Loss_MMSCF'] = np.where(df['status'] == 'ANOMALY',
                                     np.random.uniform(0.001, 0.01, len(df)),
                                     0)

    return df

# Anomaly detail modal
@st.dialog("ANOMALY DETAIL REPORT - BOOSTER COMPRESSOR B CPP DONGGI", width="large")
def show_anomaly_detail(anomaly_data, row_data=None):
    """Display detailed anomaly information matching email/PDF format"""

    # Header Information (matching PDF format)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <h3 style="color: white; margin: 0; text-align: center;">115-KOST CASE ANOMALI BOOSTER COMPRESSOR B CPP DONGGI</h3>
    </div>
    """, unsafe_allow_html=True)

    # Equipment Info
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Model/System:** J.BEC-UAD")
        st.markdown(f"**Equipment:** BOOSTER COMPRESSOR B CPP DONGGI")
    with col2:
        st.markdown(f"**Timestamp:** {anomaly_data['timestamp'].strftime('%d %B %Y %H:%M:%S')}")
        st.markdown(f"**Location:** CPP Donggi")

    st.divider()

    # Anomaly Metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Threshold Ratio", f"{anomaly_data['threshold_ratio']:.1f}%",
                 delta=f"{anomaly_data['threshold_ratio'] - 100:.1f}% above threshold")
    with metric_col2:
        exceed_pct = anomaly_data['threshold_ratio'] - 100
        st.metric("Exceed Percentage", f"{exceed_pct:.1f}%")
    with metric_col3:
        # Determine status
        if anomaly_data['threshold_ratio'] > 150:
            status = "CRITICAL ⚠️"
        elif anomaly_data['threshold_ratio'] > 120:
            status = "WARNING ⚠️"
        else:
            status = "CAUTION ⚠️"
        st.metric("Asset Integrity Status", status)

    st.divider()

    # Main Table: Top Contributing Variables (matching PDF format)
    st.markdown("### 📊 VARIABLE ANALYSIS - TOP CONTRIBUTORS")

    if row_data is not None:
        # Define sensor parameters with thresholds
        sensors = {
            'Flow_Rate': {'tag': 'FI1001B', 'unit': 'MMSCFD', 'low': 45, 'high': 56},
            'Suction_Pressure': {'tag': 'PI1001B', 'unit': 'barg', 'low': 33, 'high': 34},
            'Discharge_Pressure': {'tag': 'PI1004B', 'unit': 'barg', 'low': 60, 'high': 63.3},
            'Suction_Temperature': {'tag': 'TI1003B', 'unit': '°C', 'low': 90, 'high': 100},
            'Discharge_Temperature': {'tag': 'TI1004B', 'unit': '°C', 'low': 189, 'high': 205},
        }

        # Build table data (matching PDF columns)
        table_data = []

        for param, config in sensors.items():
            actual = row_data.get(param, 0)
            # Calculate expected as midpoint of normal range
            expected = (config['low'] + config['high']) / 2
            deviation = actual - expected
            deviation_pct = (deviation / expected * 100) if expected != 0 else 0

            # Calculate contribution (mock - weighted by deviation)
            contribution = abs(deviation_pct) * 20  # Simplified calculation

            # Determine abnormality - Check if value is outside normal range OR significant deviation
            is_outside_range = (actual < config['low']) or (actual > config['high'])
            is_significant_deviation = abs(deviation_pct) > 2.0  # Lower threshold: 2% deviation
            has_high_contribution = contribution > 20.0  # High contribution to loss

            abnormality = "YES" if (is_outside_range or is_significant_deviation or has_high_contribution) else "NO"

            table_data.append({
                'VARIABLE': param.replace('_', ' '),
                'TAG': config['tag'],
                'ACTUAL VALUE': f"{actual:.2f}",
                'EXPECTED VALUE': f"{expected:.2f}",
                'DEVIATION': f"{deviation:+.2f}",
                'DEVIATION %': f"{deviation_pct:+.1f}%",
                'LOSS CONTRIBUTION': f"{contribution:.1f}%",
                'ABNORMALITY': abnormality
            })

        # Create DataFrame
        df_analysis = pd.DataFrame(table_data)

        # Style the dataframe to match PDF
        st.dataframe(
            df_analysis,
            use_container_width=True,
            hide_index=True,
            column_config={
                "VARIABLE": st.column_config.TextColumn("VARIABLE", width="medium"),
                "TAG": st.column_config.TextColumn("TAG", width="small"),
                "ACTUAL VALUE": st.column_config.TextColumn("ACTUAL\nVALUE", width="small"),
                "EXPECTED VALUE": st.column_config.TextColumn("EXPECTED\nVALUE", width="small"),
                "DEVIATION": st.column_config.TextColumn("DEVIATION", width="small"),
                "DEVIATION %": st.column_config.TextColumn("DEVIATION\n%", width="small"),
                "LOSS CONTRIBUTION": st.column_config.TextColumn("LOSS\nCONTRIBUTION", width="small"),
                "ABNORMALITY": st.column_config.TextColumn("ABNORMALITY", width="small"),
            }
        )

    st.divider()

    # Action Buttons
    col_close, col_export = st.columns(2)
    with col_close:
        if st.button("✖ Close", type="secondary", use_container_width=True):
            st.rerun()
    with col_export:
        if st.button("📥 Export to PDF", type="primary", use_container_width=True):
            st.info("PDF export feature - Coming soon!")

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")

    st.markdown("**📊 Data Source**")
    st.info("Test.xlsx\n14/4/2026 00:00-00:53\n(Infinite loop)")

    st.divider()

    st.markdown("**⚡ Playback Speed**")
    speed_options = {
        "Real-time (1x)": 1.0,
        "2x Speed": 0.5,
        "5x Speed": 0.2,
        "10x Speed": 0.1,
        "Maximum Speed": 0.01
    }

    speed_label = st.selectbox("Speed", list(speed_options.keys()), index=4)
    st.session_state.simulation_speed = speed_options[speed_label]

    st.divider()

    st.markdown("**📧 Email Alerts**")
    if EMAIL_CONFIGURED:
        enable_email = st.checkbox("Send Email Alerts", value=True)
        st.session_state.enable_email = enable_email
        if enable_email:
            recipient = os.getenv('ALERT_TO', 'Not configured')
            st.caption(f"✅ Will send to: {recipient}")
    else:
        enable_email = st.checkbox("Send Email Alerts", value=False, disabled=True)
        st.session_state.enable_email = False
        st.warning("⚠️ Email not configured")

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
        st.success("🔴 LIVE - Running")
    else:
        st.info("⏹️ Stopped")

    st.caption(f"""
    **How it works:**
    1. Click ▶️ Start
    2. Data loops continuously
    3. Charts update live
    4. Anomalies → Email alerts

    **Speed:** {speed_label}
    """)

# ========== HEADER ==========
st.markdown("""
<div class="main-header">
    <h1 class="header-title">GUARD</h1>
    <p class="header-subtitle">Generative Understanding for Anomaly Response & Detection - Machine Learning Based Early Warning System</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ========== STATUS METRICS ==========
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    current_time_display = st.empty()
with metric_col2:
    points_display = st.empty()
with metric_col3:
    anomalies_display = st.empty()
with metric_col4:
    emails_display = st.empty()

if not st.session_state.simulation_running:
    current_time_display.markdown("""
    <div class="metric-card">
        <div class="metric-label">Current Time</div>
        <div class="metric-value">Not Started</div>
    </div>
    """, unsafe_allow_html=True)

    points_display.markdown("""
    <div class="metric-card">
        <div class="metric-label">Points Processed</div>
        <div class="metric-value">0</div>
    </div>
    """, unsafe_allow_html=True)

    anomalies_display.markdown("""
    <div class="metric-card">
        <div class="metric-label">Anomalies</div>
        <div class="metric-value metric-value-warning">0</div>
    </div>
    """, unsafe_allow_html=True)

    emails_display.markdown("""
    <div class="metric-card">
        <div class="metric-label">Emails Sent</div>
        <div class="metric-value metric-value-success">0</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ========== MAIN CONTENT AREA (Always visible) ==========
main_content_container = st.container()
sensor_content_container = st.container()

# ========== SIMULATION LOGIC ==========
if st.session_state.simulation_running or len(st.session_state.data_buffer) > 0:

    # Load data if not loaded
    if st.session_state.full_data is None:
        with st.spinner("📂 Loading Test.xlsx..."):
            try:
                df = load_data()
                st.session_state.full_data = df

                anomaly_count = len(df[df['status'] == 'ANOMALY'])
                normal_count = len(df[df['status'] == 'NORMAL'])
                total = len(df)

                st.success(f"✅ Loaded {total:,} data points")
                st.info(f"📊 {normal_count:,} normal, {anomaly_count:,} anomalies | 🔄 Looping mode")
                time.sleep(2)
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.simulation_running = False
                st.stop()

    # Simulation loop
    if st.session_state.simulation_running:
        data = st.session_state.full_data

        while st.session_state.simulation_running:

            # Loop back to start if reached end
            if st.session_state.current_index >= len(data):
                st.session_state.current_index = 0
                st.info("🔄 Looping back to start...")
                time.sleep(0.5)

            # Get current row
            current_row = data.iloc[st.session_state.current_index]
            current_timestamp = data.index[st.session_state.current_index]

            # Add to buffer (keep only last 500 points for smooth performance)
            st.session_state.data_buffer.append({
                'timestamp': current_timestamp,
                'MAE': current_row['MAE'],
                'status': current_row['status'],
                'threshold_ratio': current_row['threshold_ratio'],
                'Flow_Rate': current_row['Flow_Rate'],
                'Suction_Pressure': current_row['Suction_Pressure'],
                'Discharge_Pressure': current_row['Discharge_Pressure'],
                'Suction_Temperature': current_row['Suction_Temperature'],
                'Discharge_Temperature': current_row['Discharge_Temperature'],
            })

            # Keep only last 500 points to prevent memory buildup and freezing
            if len(st.session_state.data_buffer) > 500:
                st.session_state.data_buffer = st.session_state.data_buffer[-500:]

            # Check for anomaly and send email
            if current_row['status'] == 'ANOMALY':
                anomaly_info = {
                    'timestamp': current_timestamp,
                    'MAE': current_row['MAE'],
                    'threshold_ratio': current_row['threshold_ratio'],
                }
                st.session_state.anomalies_detected.append(anomaly_info)

                # Keep only last 100 anomalies to prevent memory buildup
                if len(st.session_state.anomalies_detected) > 100:
                    st.session_state.anomalies_detected = st.session_state.anomalies_detected[-100:]

                # Email alert logic
                should_email = (
                    st.session_state.get('enable_email', False) and
                    len(st.session_state.emails_sent) < 20
                )

                if should_email:
                    try:
                        from email_notifier import send_email_alert
                        success = send_email_alert(current_row)
                        status = 'Sent' if success else 'Failed'
                    except:
                        status = 'Error'
                else:
                    status = 'Not Sent: Disabled' if not st.session_state.get('enable_email', False) else 'Limit Reached'

                st.session_state.emails_sent.append({
                    'timestamp': current_timestamp,
                    'status': status,
                    'MAE': current_row['MAE']
                })

            # Update status metrics (update placeholders directly, no with-context)
            current_time_display.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Current Time</div>
                <div class="metric-value" style="font-size: 1.3rem;">{current_timestamp.strftime("%Y-%m-%d")}</div>
                <div class="metric-value">{current_timestamp.strftime("%H:%M:%S")}</div>
            </div>
            """, unsafe_allow_html=True)

            points_display.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Points Processed</div>
                <div class="metric-value metric-value-success">{st.session_state.current_index + 1:,}</div>
            </div>
            """, unsafe_allow_html=True)

            anomaly_count = len(st.session_state.anomalies_detected)
            anomaly_color = "metric-value-danger" if anomaly_count > 0 else "metric-value"
            anomalies_display.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Anomalies</div>
                <div class="metric-value {anomaly_color}">{anomaly_count}</div>
            </div>
            """, unsafe_allow_html=True)

            emails_sent_count = len([e for e in st.session_state.emails_sent if e['status'] == 'Sent'])
            emails_display.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Emails Sent</div>
                <div class="metric-value metric-value-success">{emails_sent_count}</div>
            </div>
            """, unsafe_allow_html=True)

            # Update charts
            if len(st.session_state.data_buffer) > 0:
                buffer_df = pd.DataFrame(st.session_state.data_buffer)
                buffer_df['timestamp'] = pd.to_datetime(buffer_df['timestamp'])

                # Main threshold ratio chart
                with main_content_container:
                    col_left, col_right = st.columns([2.5, 1])

                    with col_left:
                        st.markdown('<div class="section-header">Threshold Ratio Analysis</div>', unsafe_allow_html=True)

                        # Stats cards
                        stats_col1, stats_col2, stats_col3 = st.columns(3)

                        latest_ratio = buffer_df['threshold_ratio'].iloc[-1]
                        highest_ratio = buffer_df['threshold_ratio'].max()
                        anomaly_count = len(buffer_df[buffer_df['status'] == 'ANOMALY'])

                        with stats_col1:
                            st.markdown(f'<div class="stats-card"><div class="stats-value">{latest_ratio:.1f}%</div><div>Latest Ratio</div></div>', unsafe_allow_html=True)
                        with stats_col2:
                            st.markdown(f'<div class="stats-card"><div class="stats-value-danger">{highest_ratio:.1f}%</div><div>Highest Ratio</div></div>', unsafe_allow_html=True)
                        with stats_col3:
                            st.markdown(f'<div class="stats-card"><div class="stats-value">{anomaly_count}</div><div>Anomaly Count</div></div>', unsafe_allow_html=True)

                        # Main chart
                        fig_main = go.Figure()

                        # Area fill
                        fig_main.add_trace(go.Scatter(
                            x=buffer_df['timestamp'],
                            y=buffer_df['threshold_ratio'],
                            fill='tozeroy',
                            fillcolor='rgba(66, 135, 245, 0.3)',
                            line=dict(color='rgba(66, 135, 245, 0.8)', width=2),
                            name='Threshold Ratio'
                        ))

                        # Trend line
                        if len(buffer_df) > 3:
                            z = np.polyfit(range(len(buffer_df)), buffer_df['threshold_ratio'], min(3, len(buffer_df)-1))
                            p = np.poly1d(z)
                            trend = p(range(len(buffer_df)))
                            fig_main.add_trace(go.Scatter(
                                x=buffer_df['timestamp'],
                                y=trend,
                                line=dict(color='#4caf50', width=3),
                                name='Trend'
                            ))

                        # Anomaly markers
                        anomalies_df = buffer_df[buffer_df['status'] == 'ANOMALY']
                        if len(anomalies_df) > 0:
                            fig_main.add_trace(go.Scatter(
                                x=anomalies_df['timestamp'],
                                y=anomalies_df['threshold_ratio'],
                                mode='markers',
                                marker=dict(size=15, color='#ff5722', line=dict(color='#d32f2f', width=2)),
                                name='Anomaly'
                            ))

                        # Current position
                        fig_main.add_scatter(
                            x=[current_timestamp],
                            y=[buffer_df['threshold_ratio'].iloc[-1]],
                            mode='markers+text',
                            marker=dict(color='green', size=15, symbol='triangle-up'),
                            text=['NOW'],
                            textposition='top center',
                            showlegend=False
                        )

                        fig_main.add_hline(y=100, line_dash="dash", line_color="#ff9800", annotation_text="Threshold")

                        fig_main.update_layout(
                            height=400,
                            hovermode='x unified',
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02),
                            margin=dict(l=20, r=20, t=40, b=20),
                            plot_bgcolor='white',
                            xaxis=dict(gridcolor='#f0f0f0'),
                            yaxis=dict(gridcolor='#f0f0f0', range=[0, max(120, buffer_df['threshold_ratio'].max() * 1.1)])
                        )

                        st.plotly_chart(fig_main, use_container_width=True)

                    with col_right:
                        st.markdown('<div class="section-header section-header-green">Anomaly History</div>', unsafe_allow_html=True)

                        if len(st.session_state.anomalies_detected) > 0:
                            recent = st.session_state.anomalies_detected[-10:]

                            # Table header
                            st.markdown("""
                            <div style="display: grid; grid-template-columns: 3fr 2fr 1.5fr; gap: 1rem; padding: 0.8rem;
                                        background: #f5f5f5; border-radius: 5px; font-weight: 600;
                                        color: #333; font-size: 0.85rem; margin-bottom: 0.5rem;">
                                <div>TIME</div>
                                <div>RATIO</div>
                                <div style="text-align: center;">ACTION</div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Table rows
                            for idx, anomaly in enumerate(reversed(recent)):
                                # Determine color based on severity
                                if anomaly['threshold_ratio'] > 150:
                                    ratio_color = "#d32f2f"  # Dark red - Critical
                                    bg_color = "#ffebee"     # Light red background
                                elif anomaly['threshold_ratio'] > 120:
                                    ratio_color = "#f44336"  # Red - Warning
                                    bg_color = "#fff3e0"     # Light orange background
                                else:
                                    ratio_color = "#ff9800"  # Orange - Caution
                                    bg_color = "#ffffff"     # White background

                                # Create row with columns (matching header proportions)
                                col_time, col_ratio, col_action = st.columns([3, 2, 1.5])

                                with col_time:
                                    st.markdown(f"""
                                    <div style="padding: 0.5rem; color: #333; font-weight: 500; font-size: 0.9rem;">
                                        {anomaly['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                                    </div>
                                    """, unsafe_allow_html=True)

                                with col_ratio:
                                    st.markdown(f"""
                                    <div style="padding: 0.5rem; color: {ratio_color}; font-weight: 700;
                                                font-size: 1.1rem;">
                                        {anomaly['threshold_ratio']:.1f}%
                                    </div>
                                    """, unsafe_allow_html=True)

                                with col_action:
                                    if st.button("View", key=f"detail_{idx}_{anomaly['timestamp']}",
                                               help="View Details", use_container_width=True, type="secondary"):
                                        # Get corresponding row data
                                        row_idx = None
                                        for i, ts in enumerate(buffer_df['timestamp']):
                                            if ts == anomaly['timestamp']:
                                                row_idx = i
                                                break

                                        row_data = buffer_df.iloc[row_idx] if row_idx is not None else None
                                        show_anomaly_detail(anomaly, row_data)

                                # Row separator with color accent
                                st.markdown(f"""
                                <hr style="margin: 0.3rem 0; border: none;
                                           border-top: 2px solid {bg_color};">
                                """, unsafe_allow_html=True)

                        else:
                            st.info("No anomalies yet")

                # Sensor charts - All 5 parameters
                with sensor_content_container:
                    st.markdown('<div class="section-header">Equipment Sensor Monitoring</div>', unsafe_allow_html=True)

                    # Row 1: Flow Rate, Suction Pressure, Discharge Pressure
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**📊 Flow Rate (MMSCFD)**")
                        fig_flow = go.Figure()
                        fig_flow.add_trace(go.Scatter(
                            x=buffer_df['timestamp'],
                            y=buffer_df['Flow_Rate'],
                            fill='tozeroy',
                            fillcolor='rgba(255, 152, 0, 0.2)',
                            line=dict(color='#ff9800', width=2)
                        ))
                        fig_flow.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20),
                                             plot_bgcolor='white', showlegend=False)
                        st.plotly_chart(fig_flow, use_container_width=True)

                    with col2:
                        st.markdown("**📊 Suction Pressure (barg)**")
                        fig_suction_pressure = go.Figure()
                        fig_suction_pressure.add_trace(go.Scatter(
                            x=buffer_df['timestamp'],
                            y=buffer_df['Suction_Pressure'],
                            fill='tozeroy',
                            fillcolor='rgba(33, 150, 243, 0.2)',
                            line=dict(color='#2196f3', width=2)
                        ))
                        fig_suction_pressure.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20),
                                                          plot_bgcolor='white', showlegend=False)
                        st.plotly_chart(fig_suction_pressure, use_container_width=True)

                    with col3:
                        st.markdown("**📊 Discharge Pressure (barg)**")
                        fig_discharge_pressure = go.Figure()
                        fig_discharge_pressure.add_trace(go.Scatter(
                            x=buffer_df['timestamp'],
                            y=buffer_df['Discharge_Pressure'],
                            line=dict(color='#ff5722', width=2)
                        ))
                        fig_discharge_pressure.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20),
                                                            plot_bgcolor='white', showlegend=False)
                        st.plotly_chart(fig_discharge_pressure, use_container_width=True)

                    # Row 2: Suction Temperature, Discharge Temperature
                    col4, col5 = st.columns(2)

                    with col4:
                        st.markdown("**📊 Suction Temperature (°C)**")
                        fig_suction_temp = go.Figure()
                        fig_suction_temp.add_trace(go.Scatter(
                            x=buffer_df['timestamp'],
                            y=buffer_df['Suction_Temperature'],
                            fill='tozeroy',
                            fillcolor='rgba(76, 175, 80, 0.2)',
                            line=dict(color='#4caf50', width=2)
                        ))
                        fig_suction_temp.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20),
                                                      plot_bgcolor='white', showlegend=False)
                        st.plotly_chart(fig_suction_temp, use_container_width=True)

                    with col5:
                        st.markdown("**📊 Discharge Temperature (°C)**")
                        fig_discharge_temp = go.Figure()
                        fig_discharge_temp.add_trace(go.Scatter(
                            x=buffer_df['timestamp'],
                            y=buffer_df['Discharge_Temperature'],
                            line=dict(color='#9c27b0', width=2)
                        ))
                        fig_discharge_temp.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20),
                                                        plot_bgcolor='white', showlegend=False)
                        st.plotly_chart(fig_discharge_temp, use_container_width=True)

            # Move to next point
            st.session_state.current_index += 1
            time.sleep(st.session_state.simulation_speed)
            st.rerun()

else:
    # Not running - show instructions in main container
    with main_content_container:
        st.info("""
        ### 🎬 Live Modern Dashboard

        **How to use:**
        1. Click **▶️ Start** in sidebar
        2. Watch data loop continuously (54 min cycle)
        3. Charts update live in real-time
        4. Anomalies detected automatically
        5. Email alerts sent (if enabled)

        **Features:**
        - Professional LEADS-style interface
        - Live looping data from Test.xlsx
        - Real-time anomaly detection
        - Email notifications
        - Equipment selector tabs
        """)

# Footer
st.divider()
st.caption("🛡️ GUARD v2.0 | Pertamina EP Cepu | SKK Migas | Test.xlsx (14/4/2026) Infinite Loop")
