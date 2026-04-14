"""
i2AIMS Demonstration Dashboard
- Select timeframe from historical data
- Detect anomalies
- Send email alerts
- Visualize results
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path
import sys
import os

# Pre-load heavy modules at startup
import warnings
warnings.filterwarnings('ignore')

# Import pipeline modules (loads TensorFlow - takes time but only once)
try:
    from rca_pipeline import run_pipeline
    from rule_engine import THRESHOLDS, match_scenario
    from email_notifier import send_email_alert
    MODULES_LOADED = True
except Exception as e:
    MODULES_LOADED = False
    MODULE_ERROR = str(e)

# Page config
st.set_page_config(
    page_title="GUARD Demo - CPP Donggi",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🛡️ GUARD - CPP Donggi")
st.caption("**Generative Understanding for Anomaly Response & Detection**")
st.subheader("BOOSTER COMPRESSOR B CPP DONGGI")
st.markdown("**Anomaly Detection & Email Alert Demonstration**")

st.divider()

# Initialize session state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
    st.session_state.anomalies = None
    st.session_state.all_results = None
    st.session_state.features = None
    st.session_state.emails_sent = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Demo Settings")

    st.subheader("📅 Select Timeframe")
    st.write("Available data: Jan 1, 2025 - Dec 31, 2025")

    start_date = st.date_input(
        "Start Date",
        value=datetime(2025, 8, 1),
        min_value=datetime(2025, 1, 1),
        max_value=datetime(2025, 12, 31)
    )

    end_date = st.date_input(
        "End Date",
        value=datetime(2025, 8, 31),
        min_value=datetime(2025, 1, 1),
        max_value=datetime(2025, 12, 31)
    )

    st.divider()

    st.subheader("📧 Email Alerts")

    send_emails = st.checkbox("Send Email Alerts", value=True)

    if send_emails:
        max_emails = st.slider("Max emails to send", 1, 20, 5)
        st.caption(f"Will send up to {max_emails} email alerts for detected anomalies")
    else:
        max_emails = 0
        st.caption("Email alerts disabled for this demo")

    st.divider()

    # Run analysis button
    if st.button("🚀 Run Analysis", use_container_width=True, type="primary"):
        if end_date < start_date:
            st.error("End date must be after start date!")
        else:
            st.session_state.analysis_done = False
            st.session_state.run_requested = True

    st.divider()

    st.info("""
    **How it works:**
    1. Select date range
    2. Enable/disable email alerts
    3. Click 'Run Analysis'
    4. Wait for results (~30s)
    5. View anomalies + alerts
    """)

# Main content
if not st.session_state.analysis_done and not st.session_state.get('run_requested', False):
    # Welcome screen
    st.info("👈 **Configure settings in sidebar and click 'Run Analysis' to start**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 What This Demo Shows")
        st.write("""
        - **Anomaly Detection** using LSTM autoencoder
        - **Rule-Based Classification** (HIGH/LOW/NORMAL)
        - **Email Alerts** for detected anomalies
        - **Real-time Visualization** of sensor data
        - **Production Impact** (gas loss calculation)
        """)

    with col2:
        st.markdown("### 📧 Email Alert Features")
        st.write("""
        - HTML-formatted emails
        - Top contributing sensors
        - Deviation analysis
        - Threshold exceedance details
        - Sent to configured recipients
        """)

    st.divider()

    st.markdown("### 📅 Suggested Demo Periods")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("""
        **Period 1: August 2025**
        - Start: 2025-08-01
        - End: 2025-08-31
        - Expected: Multiple anomalies
        """)

    with col2:
        st.success("""
        **Period 2: September 2025**
        - Start: 2025-09-01
        - End: 2025-09-30
        - Expected: Fewer anomalies
        """)

    with col3:
        st.warning("""
        **Period 3: July-August 2025**
        - Start: 2025-07-01
        - End: 2025-08-31
        - Expected: High activity
        """)

elif st.session_state.get('run_requested', False) and not st.session_state.analysis_done:
    # Run analysis
    st.session_state.run_requested = False

    with st.spinner(f"🔄 Analyzing data from {start_date} to {end_date}... This will take 30-60 seconds..."):

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Check if modules loaded
            if not MODULES_LOADED:
                st.error(f"Failed to load modules: {MODULE_ERROR}")
                st.session_state.analysis_done = False
                st.stop()

            # Step 1: Run pipeline
            status_text.text("Running LSTM anomaly detection...")
            progress_bar.progress(20)

            BASE_DIR = Path(__file__).parent
            DATA_DIR = BASE_DIR / "KODE_FIX" / "KODE FIX"

            anomalies, all_results, features = run_pipeline(
                csv_path=str(DATA_DIR / "Historical_Data.csv"),
                model_path=str(DATA_DIR / "lstm_compressor_17.keras"),
                scaler_path=str(DATA_DIR / "scaler_17.pkl"),
                data_start=start_date.strftime("%Y-%m-%d"),
                data_end=end_date.strftime("%Y-%m-%d"),
            )

            progress_bar.progress(70)
            status_text.text("Anomaly detection complete!")

            # Step 3: Send email alerts
            if send_emails and len(anomalies) > 0:
                status_text.text(f"Sending email alerts (max {max_emails})...")
                progress_bar.progress(80)

                emails_sent = []
                for idx, (timestamp, row) in enumerate(anomalies.head(max_emails).iterrows()):
                    try:
                        success = send_email_alert(row)
                        emails_sent.append({
                            'timestamp': timestamp,
                            'status': 'Sent' if success else 'Failed',
                            'mae': row.get('MAE', 0),
                            'threshold_ratio': row.get('threshold_ratio', 0)
                        })
                    except Exception as e:
                        emails_sent.append({
                            'timestamp': timestamp,
                            'status': f'Error: {str(e)[:50]}',
                            'mae': row.get('MAE', 0),
                            'threshold_ratio': row.get('threshold_ratio', 0)
                        })

                st.session_state.emails_sent = emails_sent
            else:
                st.session_state.emails_sent = []

            # Step 4: Store results
            progress_bar.progress(90)
            status_text.text("Preparing visualization...")

            st.session_state.analysis_done = True
            st.session_state.anomalies = anomalies
            st.session_state.all_results = all_results
            st.session_state.features = features
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date

            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.exception(e)
            st.session_state.analysis_done = False

else:
    # Show results
    anomalies = st.session_state.anomalies
    all_results = st.session_state.all_results
    features = st.session_state.features
    emails_sent = st.session_state.emails_sent

    # Success message
    st.success(f"✅ Analysis Complete: {start_date} to {end_date}")

    # Email alert summary
    if len(emails_sent) > 0:
        sent_count = len([e for e in emails_sent if e['status'] == 'Sent'])
        if sent_count > 0:
            st.success(f"📧 {sent_count} email alert(s) sent successfully!")
        else:
            st.warning(f"⚠️ Email alerts were attempted but none sent successfully")

    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)

    total_anomalies = len(anomalies)
    total_gas_loss = anomalies['Gas_Loss_MMSCF'].sum() if len(anomalies) > 0 else 0
    anomaly_rate = (total_anomalies / len(all_results) * 100) if len(all_results) > 0 else 0
    current_status = all_results.iloc[-1]['status'] if len(all_results) > 0 else "UNKNOWN"

    with col1:
        st.metric("Total Anomalies", total_anomalies, f"{anomaly_rate:.1f}%")

    with col2:
        st.metric("Gas Loss (MMSCF)", f"{total_gas_loss:.3f}")

    with col3:
        st.metric("Email Alerts Sent", len([e for e in emails_sent if e['status'] == 'Sent']))

    with col4:
        st.metric("Data Points", f"{len(all_results):,}")

    st.divider()

    # Email alert details
    if len(emails_sent) > 0:
        with st.expander("📧 Email Alert Log", expanded=True):
            email_df = pd.DataFrame(emails_sent)
            email_df['timestamp'] = pd.to_datetime(email_df['timestamp'])
            email_df['timestamp'] = email_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            email_df['mae'] = email_df['mae'].apply(lambda x: f"{x:.4f}")
            email_df['threshold_ratio'] = email_df['threshold_ratio'].apply(lambda x: f"{x:.1f}%")

            st.dataframe(email_df, use_container_width=True, hide_index=True)

    st.divider()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Timeline", "📊 Sensors", "📋 Anomalies", "🔍 Details"])

    with tab1:
        st.subheader("Anomaly Detection Timeline")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=all_results.index,
            y=all_results['MAE'],
            mode='lines',
            name='MAE',
            line=dict(color='#1976d2', width=1),
            hovertemplate='%{x}<br>MAE: %{y:.4f}<extra></extra>'
        ))

        if len(anomalies) > 0:
            fig.add_trace(go.Scatter(
                x=anomalies.index,
                y=anomalies['MAE'],
                mode='markers',
                name='Anomaly',
                marker=dict(color='#f44336', size=8, symbol='x'),
                hovertemplate='%{x}<br>MAE: %{y:.4f}<br>ANOMALY<extra></extra>'
            ))

        # Mark emailed anomalies
        if len(emails_sent) > 0:
            emailed_times = [e['timestamp'] for e in emails_sent if e['status'] == 'Sent']
            emailed_data = anomalies[anomalies.index.isin(emailed_times)]

            if len(emailed_data) > 0:
                fig.add_trace(go.Scatter(
                    x=emailed_data.index,
                    y=emailed_data['MAE'],
                    mode='markers',
                    name='Email Sent',
                    marker=dict(color='#4caf50', size=12, symbol='star'),
                    hovertemplate='%{x}<br>MAE: %{y:.4f}<br>📧 EMAIL SENT<extra></extra>'
                ))

        threshold = all_results['MAE'].quantile(0.95)
        fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                      annotation_text="Threshold")

        fig.update_layout(
            xaxis_title="Timestamp",
            yaxis_title="Mean Absolute Error (MAE)",
            hovermode='x unified',
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Data Points", f"{len(all_results):,}")
        with col2:
            st.metric("Anomalies Detected", len(anomalies))
        with col3:
            avg_mae = all_results['MAE'].mean()
            st.metric("Average MAE", f"{avg_mae:.4f}")

    with tab2:
        st.subheader("Sensor Readings Over Time")

        fig = go.Figure()
        colors = ['#1976d2', '#ff9800', '#4caf50', '#9c27b0', '#f44336']

        for i, feature in enumerate(features):
            if feature in all_results.columns:
                fig.add_trace(go.Scatter(
                    x=all_results.index,
                    y=all_results[feature],
                    mode='lines',
                    name=feature.replace('_', ' '),
                    line=dict(color=colors[i % len(colors)], width=2)
                ))

        fig.update_layout(
            xaxis_title="Timestamp",
            yaxis_title="Value",
            hovermode='x unified',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Detected Anomalies")

        if len(anomalies) == 0:
            st.info("No anomalies detected in the selected period")
        else:
            display_cols = ['MAE', 'threshold_ratio', 'exceed_percent', 'Gas_Loss_MMSCF']
            for f in features:
                if f in anomalies.columns:
                    display_cols.append(f)

            df_display = anomalies[display_cols].copy()
            df_display.index = df_display.index.strftime('%Y-%m-%d %H:%M:%S')

            st.dataframe(df_display, use_container_width=True, height=400)

            csv = anomalies.to_csv()
            st.download_button(
                label="📥 Download Anomaly Data (CSV)",
                data=csv,
                file_name=f"anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with tab4:
        st.subheader("Anomaly Analysis")

        if len(anomalies) > 0:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Hourly Distribution")
                anomalies_copy = anomalies.copy()
                anomalies_copy['hour'] = anomalies_copy.index.hour
                hour_counts = anomalies_copy['hour'].value_counts().sort_index()

                fig = px.bar(x=hour_counts.index, y=hour_counts.values,
                             labels={'x': 'Hour of Day', 'y': 'Count'})
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("### Gas Loss Trend")
                cumulative = anomalies.sort_index()['Gas_Loss_MMSCF'].cumsum()
                fig = px.line(x=cumulative.index, y=cumulative.values,
                              labels={'x': 'Time', 'y': 'Cumulative (MMSCF)'})
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No anomalies to analyze")

st.divider()
st.caption(f"GUARD (Generative Understanding for Anomaly Response & Detection) | Demo Period: {start_date} to {end_date} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
