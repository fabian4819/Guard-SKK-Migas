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
    st.session_state.last_rerun_time = time.time()
    st.session_state.update_batch_size = 5  # Update UI every 5 data points

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

# Anomaly detail modal
@st.dialog("ANOMALY DETAIL REPORT - BOOSTER COMPRESSOR B CPP DONGGI", width="large")
def show_anomaly_detail(anomaly_data, row_data=None):
    """Display detailed anomaly information matching email/PDF format"""

    # Header Information
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <h3 style="color: white; margin: 0; text-align: center;">ANOMALY DETECTION BOOSTER COMPRESSOR B CPP DONGGI</h3>
        <p style="color: white; margin: 0.5rem 0 0 0; text-align: center; font-size: 0.9rem; opacity: 0.9;">
            {anomaly_data['timestamp'].strftime('%d %B %Y %H:%M:%S')} | CPP Donggi
        </p>
    </div>
    """, unsafe_allow_html=True)

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

    # Table 1: Top Contributing Variables - removed icon
    st.markdown("### VARIABLE ANALYSIS - TOP CONTRIBUTORS")

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

    # Table 2: RCA Division Analysis (matching PDF second table)
    st.markdown("### ROOT CAUSE ANALYSIS - PROBABLE SCENARIOS")

    if row_data is not None:
        from rca_knowledge_base import get_applicable_rca_scenarios

        # Get RCA scenarios
        scenarios = get_applicable_rca_scenarios(row_data, top_n=5)

        if len(scenarios) > 0:
            # Build RCA table data
            rca_table_data = []

            for scenario in scenarios:
                vars_dict = scenario.get("variables", {})
                rca_table_data.append({
                    'DIVISION': scenario.get('division', ''),
                    'PROB': scenario.get('id', '').split('-')[1] if '-' in scenario.get('id', '') else '',
                    'RCA': scenario.get('rca', ''),
                    'ACTIONS': scenario.get('actions', ''),
                    'Flow Rate': 'YES' if vars_dict.get('Flow_Rate', False) else 'NO',
                    'Suction Press': 'YES' if vars_dict.get('Suction_Pressure', False) else 'NO',
                    'Discharge Press': 'YES' if vars_dict.get('Discharge_Pressure', False) else 'NO',
                    'Suction Temp': 'YES' if vars_dict.get('Suction_Temperature', False) else 'NO',
                    'Discharge Temp': 'YES' if vars_dict.get('Discharge_Temperature', False) else 'NO',
                    'SYMPTOM': scenario.get('symptom', '')
                })

            # Display RCA table
            df_rca = pd.DataFrame(rca_table_data)
            st.dataframe(
                df_rca,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "DIVISION": st.column_config.TextColumn("DIVISION", width="small"),
                    "PROB": st.column_config.TextColumn("PROB", width="small"),
                    "RCA": st.column_config.TextColumn("RCA", width="large"),
                    "ACTIONS": st.column_config.TextColumn("ACTIONS", width="large"),
                    "Flow Rate": st.column_config.TextColumn("Flow\nRate", width="small"),
                    "Suction Press": st.column_config.TextColumn("Suction\nPress", width="small"),
                    "Discharge Press": st.column_config.TextColumn("Discharge\nPress", width="small"),
                    "Suction Temp": st.column_config.TextColumn("Suction\nTemp", width="small"),
                    "Discharge Temp": st.column_config.TextColumn("Discharge\nTemp", width="small"),
                    "SYMPTOM": st.column_config.TextColumn("SYMPTOM", width="medium"),
                }
            )
        else:
            st.info("No specific RCA scenarios matched. General investigation recommended.")

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")

    st.markdown("** Data Source**")
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
    with current_time_display.container():
        st.markdown("""
        <div style="background: white; padding: 1.2rem; border-radius: 8px;
                    border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="color: #888; font-size: 0.75rem; font-weight: 600;
                        letter-spacing: 0.5px; margin-bottom: 0.5rem; text-transform: uppercase;">Current Time</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #1e3c72; line-height: 1;">Not Started</div>
        </div>
        """, unsafe_allow_html=True)

    with points_display.container():
        st.markdown("""
        <div style="background: white; padding: 1.2rem; border-radius: 8px;
                    border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="color: #888; font-size: 0.75rem; font-weight: 600;
                        letter-spacing: 0.5px; margin-bottom: 0.5rem; text-transform: uppercase;">Points Processed</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #4caf50; line-height: 1;">0</div>
        </div>
        """, unsafe_allow_html=True)

    with anomalies_display.container():
        st.markdown("""
        <div style="background: white; padding: 1.2rem; border-radius: 8px;
                    border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="color: #888; font-size: 0.75rem; font-weight: 600;
                        letter-spacing: 0.5px; margin-bottom: 0.5rem; text-transform: uppercase;">Anomalies</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #ff5722; line-height: 1;">0</div>
        </div>
        """, unsafe_allow_html=True)

    with emails_display.container():
        st.markdown("""
        <div style="background: white; padding: 1.2rem; border-radius: 8px;
                    border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="color: #888; font-size: 0.75rem; font-weight: 600;
                        letter-spacing: 0.5px; margin-bottom: 0.5rem; text-transform: uppercase;">Emails Sent</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #4caf50; line-height: 1;">0</div>
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

                # Data loaded silently - removed display messages
                time.sleep(0.5)
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

            # Update status metrics - styled cards matching image
            with current_time_display.container():
                date_str = current_timestamp.strftime("%Y-%m-%d")
                time_str = current_timestamp.strftime("%H:%M:%S")
                st.markdown(f"""
                <div style="background: white; padding: 1.2rem; border-radius: 8px;
                            border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="color: #888; font-size: 0.75rem; font-weight: 600;
                                letter-spacing: 0.5px; margin-bottom: 0.5rem; text-transform: uppercase;">Current Time</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #1e3c72; line-height: 1.2;">{date_str}</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #1e3c72; line-height: 1.1;">{time_str}</div>
                </div>
                """, unsafe_allow_html=True)

            with points_display.container():
                points_val = st.session_state.current_index + 1
                st.markdown(f"""
                <div style="background: white; padding: 1.2rem; border-radius: 8px;
                            border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="color: #888; font-size: 0.75rem; font-weight: 600;
                                letter-spacing: 0.5px; margin-bottom: 0.5rem; text-transform: uppercase;">Points Processed</div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: #4caf50; line-height: 1;">{points_val:,}</div>
                </div>
                """, unsafe_allow_html=True)

            anomaly_count = len(st.session_state.anomalies_detected)
            with anomalies_display.container():
                st.markdown(f"""
                <div style="background: white; padding: 1.2rem; border-radius: 8px;
                            border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="color: #888; font-size: 0.75rem; font-weight: 600;
                                letter-spacing: 0.5px; margin-bottom: 0.5rem; text-transform: uppercase;">Anomalies</div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: #ff5722; line-height: 1;">{anomaly_count}</div>
                </div>
                """, unsafe_allow_html=True)

            emails_sent_count = len([e for e in st.session_state.emails_sent if e['status'] == 'Sent'])
            with emails_display.container():
                st.markdown(f"""
                <div style="background: white; padding: 1.2rem; border-radius: 8px;
                            border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="color: #888; font-size: 0.75rem; font-weight: 600;
                                letter-spacing: 0.5px; margin-bottom: 0.5rem; text-transform: uppercase;">Emails Sent</div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: #4caf50; line-height: 1;">{emails_sent_count}</div>
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

                        # Main chart - optimized rendering
                        fig_main = go.Figure()

                        # Area fill - use fewer points if buffer is large
                        plot_df = buffer_df if len(buffer_df) <= 200 else buffer_df.iloc[::2]  # Skip every other point if >200

                        fig_main.add_trace(go.Scatter(
                            x=plot_df['timestamp'],
                            y=plot_df['threshold_ratio'],
                            fill='tozeroy',
                            fillcolor='rgba(66, 135, 245, 0.3)',
                            line=dict(color='rgba(66, 135, 245, 0.8)', width=2),
                            name='Threshold Ratio',
                            hoverinfo='x+y'
                        ))

                        # Anomaly markers only (removed trend line for performance)
                        anomalies_df = buffer_df[buffer_df['status'] == 'ANOMALY']
                        if len(anomalies_df) > 0:
                            fig_main.add_trace(go.Scatter(
                                x=anomalies_df['timestamp'],
                                y=anomalies_df['threshold_ratio'],
                                mode='markers',
                                marker=dict(size=12, color='#ff5722', symbol='circle'),
                                name='Anomaly',
                                hoverinfo='x+y'
                            ))

                        # Current position
                        fig_main.add_scatter(
                            x=[current_timestamp],
                            y=[buffer_df['threshold_ratio'].iloc[-1]],
                            mode='markers',
                            marker=dict(color='green', size=12, symbol='triangle-up'),
                            showlegend=False,
                            hoverinfo='skip'
                        )

                        fig_main.add_hline(y=100, line_dash="dash", line_color="#ff9800",
                                         annotation_text="Threshold", annotation_position="right")

                        fig_main.update_layout(
                            height=400,
                            hovermode='x',
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02),
                            margin=dict(l=20, r=20, t=40, b=20),
                            plot_bgcolor='white',
                            xaxis=dict(gridcolor='#f0f0f0', showgrid=False),
                            yaxis=dict(gridcolor='#f0f0f0', showgrid=True,
                                     range=[0, max(120, buffer_df['threshold_ratio'].max() * 1.1)])
                        )

                        st.plotly_chart(fig_main, use_container_width=True, key=f"main_chart_{st.session_state.current_index}")

                    with col_right:
                        st.markdown('<div class="section-header section-header-green">Anomaly History</div>', unsafe_allow_html=True)

                        if len(st.session_state.anomalies_detected) > 0:
                            # Show only last 5 anomalies to reduce rendering load
                            recent = st.session_state.anomalies_detected[-5:]

                            # Table header - matching image style
                            st.markdown("""
                            <div style="display: grid; grid-template-columns: 3fr 1.5fr 1.5fr; gap: 0.5rem;
                                        padding: 0.5rem; background: #f5f5f5; font-weight: 600;
                                        font-size: 0.85rem; color: #333; margin-bottom: 0.5rem;">
                                <div>TIME</div>
                                <div style="text-align: center;">RATIO</div>
                                <div style="text-align: center;">ACTION</div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Table rows - matching image format exactly
                            for idx, anomaly in enumerate(reversed(recent)):
                                row_cols = st.columns([3, 1.5, 1.5])

                                with row_cols[0]:
                                    # Full timestamp with date and time like in image
                                    full_time = anomaly['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                                    st.markdown(f"<div style='font-size: 0.9rem; color: #333;'>{full_time}</div>",
                                              unsafe_allow_html=True)

                                with row_cols[1]:
                                    ratio_val = anomaly['threshold_ratio']
                                    # Color coding based on severity
                                    if ratio_val > 130:
                                        color = "#d32f2f"  # Dark red
                                    elif ratio_val > 120:
                                        color = "#f44336"  # Red
                                    else:
                                        color = "#ff9800"  # Orange
                                    st.markdown(f"<div style='text-align: center; font-weight: 700; font-size: 1rem; color: {color};'>{ratio_val:.1f}%</div>",
                                              unsafe_allow_html=True)

                                with row_cols[2]:
                                    if st.button("View", key=f"view_{idx}_{anomaly['timestamp']}",
                                               use_container_width=True):
                                        # Get corresponding row data
                                        row_idx = None
                                        for i, ts in enumerate(buffer_df['timestamp']):
                                            if ts == anomaly['timestamp']:
                                                row_idx = i
                                                break
                                        row_data = buffer_df.iloc[row_idx] if row_idx is not None else None
                                        show_anomaly_detail(anomaly, row_data)

                        else:
                            st.info("No anomalies yet")

                # Sensor charts - All 5 parameters
                with sensor_content_container:
                    st.markdown('<div class="section-header">Equipment Sensor Monitoring</div>', unsafe_allow_html=True)

                    # Row 1: Flow Rate, Suction Pressure, Discharge Pressure
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("<b>Flow Rate (MMSCFD)</b>", unsafe_allow_html=True)
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
                        st.markdown("<b>Suction Pressure (barg)</b>", unsafe_allow_html=True)
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
                        st.markdown("<b>Discharge Pressure (barg)</b>", unsafe_allow_html=True)
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
                        st.markdown("<b>Suction Temperature (°C)</b>", unsafe_allow_html=True)
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
                        st.markdown("<b>Discharge Temperature (°C)</b>", unsafe_allow_html=True)
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
st.caption("🛡️ GUARD | SKK Migas")
