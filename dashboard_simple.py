"""
i2AIMS Dashboard - Simplified Version
Loads data on-demand to avoid startup freezing
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from pathlib import Path

# Page config
st.set_page_config(
    page_title="i2AIMS - CPP Donggi",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🏭 i2AIMS - CPP Donggi")
st.subheader("BOOSTER COMPRESSOR B CPP DONGGI")
st.write("**Anomaly Detection & Monitoring System**")

st.divider()

# Check if data should be loaded
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.anomalies = None
    st.session_state.all_results = None
    st.session_state.features = None

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Date range
    st.subheader("📅 Date Range")
    today = datetime.now()
    default_start = today - timedelta(days=7)

    start_date = st.date_input(
        "Start Date",
        value=default_start,
        max_value=today
    )

    end_date = st.date_input(
        "End Date",
        value=today,
        max_value=today
    )

    st.divider()

    # Load button
    if st.button("🔄 Load/Refresh Data", use_container_width=True, type="primary"):
        st.session_state.data_loaded = False  # Trigger reload

    st.divider()

    st.info("""
    **Equipment:** BOOSTER COMPRESSOR B CPP DONGGI

    **Field:** CPP Donggi

    **Monitoring:** Real-time anomaly detection using LSTM autoencoder
    """)

# Main content
if not st.session_state.data_loaded:
    st.warning("⚠️ Data not loaded yet")
    st.write("Click **'Load/Refresh Data'** in the sidebar to load anomaly detection results.")
    st.write(f"Selected date range: **{start_date}** to **{end_date}**")

    st.info("""
    ### What to expect:

    - **Loading time:** 30-60 seconds on first load
    - **Date range:** Smaller range = faster loading
    - **Process:** LSTM model inference + Rule-based classification

    The data will be cached for 5 minutes to improve performance.
    """)

    # Load data if button was clicked
    if st.sidebar.button("▶️ Start Loading", use_container_width=True, type="secondary"):
        with st.spinner(f"Loading data from {start_date} to {end_date}... Please wait..."):
            try:
                # Import modules (only when needed)
                from rca_pipeline import run_pipeline
                from rule_engine import THRESHOLDS

                # Paths
                BASE_DIR = Path(__file__).parent
                DATA_DIR = BASE_DIR / "KODE_FIX" / "KODE FIX"
                DEFAULT_CSV = DATA_DIR / "Historical_Data.csv"
                DEFAULT_MODEL = DATA_DIR / "lstm_compressor_17.keras"
                DEFAULT_SCALER = DATA_DIR / "scaler_17.pkl"

                # Run pipeline
                anomalies, all_results, features = run_pipeline(
                    csv_path=str(DEFAULT_CSV),
                    model_path=str(DEFAULT_MODEL),
                    scaler_path=str(DEFAULT_SCALER),
                    data_start=start_date.strftime("%Y-%m-%d"),
                    data_end=end_date.strftime("%Y-%m-%d"),
                )

                # Store in session state
                st.session_state.data_loaded = True
                st.session_state.anomalies = anomalies
                st.session_state.all_results = all_results
                st.session_state.features = features

                st.success("✅ Data loaded successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
                st.exception(e)
                st.error("""
                **Troubleshooting:**
                - Check that data files exist in KODE_FIX/KODE FIX/
                - Verify Historical_Data.csv has data in the selected date range
                - Ensure lstm_compressor_17.keras and scaler_17.pkl are present
                """)

else:
    # Data is loaded - show dashboard
    anomalies = st.session_state.anomalies
    all_results = st.session_state.all_results
    features = st.session_state.features

    st.success(f"✅ Data loaded: {len(all_results):,} records, {len(anomalies)} anomalies")

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
        st.metric("Current Status", current_status)

    with col4:
        st.metric("Data Points", f"{len(all_results):,}")

    st.divider()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Timeline", "📊 Sensors", "📋 Anomalies"])

    with tab1:
        st.subheader("Anomaly Detection Timeline")

        # Create timeline chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=all_results.index,
            y=all_results['MAE'],
            mode='lines',
            name='MAE',
            line=dict(color='#1976d2', width=1)
        ))

        # Anomalies
        if len(anomalies) > 0:
            fig.add_trace(go.Scatter(
                x=anomalies.index,
                y=anomalies['MAE'],
                mode='markers',
                name='Anomaly',
                marker=dict(color='#f44336', size=8, symbol='x')
            ))

        fig.update_layout(
            xaxis_title="Timestamp",
            yaxis_title="Mean Absolute Error (MAE)",
            hovermode='x unified',
            height=400
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

        # Multi-line chart
        fig = go.Figure()
        colors = ['#1976d2', '#ff9800', '#4caf50', '#9c27b0', '#f44336']

        for i, feature in enumerate(features):
            if feature in all_results.columns:
                fig.add_trace(go.Scatter(
                    x=all_results.index,
                    y=all_results[feature],
                    mode='lines',
                    name=feature,
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
        st.subheader("Anomaly Details")

        if len(anomalies) == 0:
            st.info("No anomalies detected in the selected period")
        else:
            # Display table
            display_cols = ['MAE', 'threshold_ratio', 'exceed_percent', 'Gas_Loss_MMSCF']

            for param in features:
                if param in anomalies.columns:
                    display_cols.append(param)

            df_display = anomalies[display_cols].copy()
            df_display.index = df_display.index.strftime('%Y-%m-%d %H:%M:%S')

            st.dataframe(df_display, use_container_width=True, height=400)

            # Download button
            csv = anomalies.to_csv()
            st.download_button(
                label="📥 Download Anomaly Data (CSV)",
                data=csv,
                file_name=f"anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
