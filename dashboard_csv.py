"""
i2AIMS Dashboard - CSV Reader Version
Reads pre-generated anomaly detection results from CSV
No TensorFlow loading - fast and responsive!
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
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

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("📁 Data Source")

    csv_file = st.selectbox(
        "Select CSV file:",
        ["dashboard_data.csv", "RCA_Report.csv"],
        help="Pre-generated anomaly detection results"
    )

    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    st.info("""
    **Equipment:** BOOSTER COMPRESSOR B CPP DONGGI

    **Field:** CPP Donggi

    **Note:** This dashboard reads pre-generated CSV files.

    To generate new data, run:
    ```
    python3 main.py --no-llm
    ```
    """)


@st.cache_data
def load_csv_data(filepath):
    """Load anomaly data from CSV file."""
    try:
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None


# Load data
data_path = Path(__file__).parent / csv_file

with st.spinner(f"Loading {csv_file}..."):
    df = load_csv_data(data_path)

if df is None:
    st.error(f"❌ File not found: {csv_file}")
    st.write("**To generate the data file, run:**")
    st.code("python3 main.py --no-llm --output dashboard_data.csv", language="bash")

    st.write("**Or check if these files exist:**")
    st.write("- dashboard_data.csv")
    st.write("- RCA_Report.csv")

    st.stop()

# Filter anomalies
anomalies = df[df['status'] == 'ANOMALY'].copy() if 'status' in df.columns else df

st.success(f"✅ Loaded: {len(df):,} records, {len(anomalies)} anomalies")

# Overview metrics
col1, col2, col3, col4 = st.columns(4)

total_anomalies = len(anomalies)
total_gas_loss = anomalies['Gas_Loss_MMSCF'].sum() if 'Gas_Loss_MMSCF' in anomalies.columns and len(anomalies) > 0 else 0
anomaly_rate = (total_anomalies / len(df) * 100) if len(df) > 0 else 0
current_status = df.iloc[-1].get('status', 'UNKNOWN') if len(df) > 0 else "UNKNOWN"

with col1:
    st.metric("Total Anomalies", total_anomalies, f"{anomaly_rate:.1f}%")

with col2:
    st.metric("Gas Loss (MMSCF)", f"{total_gas_loss:.3f}")

with col3:
    st.metric("Current Status", current_status)

with col4:
    st.metric("Data Points", f"{len(df):,}")

st.divider()

# Sensor columns
sensor_cols = ['Flow_Rate', 'Suction_Pressure', 'Discharge_Pressure',
               'Suction_Temperature', 'Discharge_Temperature']
available_sensors = [col for col in sensor_cols if col in df.columns]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Timeline", "📊 Sensors", "📋 Anomalies", "🔍 Analysis"])

with tab1:
    st.subheader("Anomaly Detection Timeline")

    if 'MAE' in df.columns:
        # Create timeline chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MAE'],
            mode='lines',
            name='MAE',
            line=dict(color='#1976d2', width=1),
            hovertemplate='%{x}<br>MAE: %{y:.4f}<extra></extra>'
        ))

        # Anomalies
        if len(anomalies) > 0 and 'MAE' in anomalies.columns:
            fig.add_trace(go.Scatter(
                x=anomalies.index,
                y=anomalies['MAE'],
                mode='markers',
                name='Anomaly',
                marker=dict(color='#f44336', size=8, symbol='x'),
                hovertemplate='%{x}<br>MAE: %{y:.4f}<br>ANOMALY<extra></extra>'
            ))

        # Threshold line
        if len(df) > 0:
            threshold = df['MAE'].quantile(0.95)
            fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                          annotation_text="Threshold (95th percentile)")

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
            st.metric("Total Data Points", f"{len(df):,}")
        with col2:
            st.metric("Anomalies Detected", len(anomalies))
        with col3:
            avg_mae = df['MAE'].mean()
            st.metric("Average MAE", f"{avg_mae:.4f}")
    else:
        st.warning("MAE column not found in data")

with tab2:
    st.subheader("Sensor Readings Over Time")

    if available_sensors:
        # Multi-line chart
        fig = go.Figure()
        colors = ['#1976d2', '#ff9800', '#4caf50', '#9c27b0', '#f44336']

        for i, sensor in enumerate(available_sensors):
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[sensor],
                mode='lines',
                name=sensor.replace('_', ' '),
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

        # Sensor statistics
        st.subheader("Sensor Statistics")

        stats_data = []
        for sensor in available_sensors:
            stats_data.append({
                "Sensor": sensor.replace('_', ' '),
                "Mean": f"{df[sensor].mean():.2f}",
                "Min": f"{df[sensor].min():.2f}",
                "Max": f"{df[sensor].max():.2f}",
                "Std Dev": f"{df[sensor].std():.2f}"
            })

        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No sensor columns found in data")

with tab3:
    st.subheader("Anomaly Details")

    if len(anomalies) == 0:
        st.info("No anomalies detected in this dataset")
    else:
        # Display columns selection
        all_cols = anomalies.columns.tolist()

        # Default columns to show
        default_cols = ['MAE', 'threshold_ratio', 'exceed_percent', 'Gas_Loss_MMSCF'] + available_sensors
        display_cols = [col for col in default_cols if col in anomalies.columns]

        # Display table
        df_display = anomalies[display_cols].copy()

        # Format datetime index
        if isinstance(df_display.index, pd.DatetimeIndex):
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

        # Show column info
        with st.expander("📊 Available Columns"):
            st.write(f"Total columns: {len(all_cols)}")
            st.write("Columns:", ", ".join(all_cols[:20]))
            if len(all_cols) > 20:
                st.write(f"... and {len(all_cols) - 20} more")

with tab4:
    st.subheader("Analysis & Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Anomaly Distribution by Hour")
        if len(anomalies) > 0 and isinstance(anomalies.index, pd.DatetimeIndex):
            anomalies_copy = anomalies.copy()
            anomalies_copy['hour'] = anomalies_copy.index.hour
            hour_counts = anomalies_copy['hour'].value_counts().sort_index()

            fig = px.bar(
                x=hour_counts.index,
                y=hour_counts.values,
                labels={'x': 'Hour of Day', 'y': 'Anomaly Count'},
                title="Anomalies by Hour"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No time-based data available")

    with col2:
        st.markdown("### Gas Loss Over Time")
        if len(anomalies) > 0 and 'Gas_Loss_MMSCF' in anomalies.columns:
            anomalies_sorted = anomalies.sort_index()
            cumulative_loss = anomalies_sorted['Gas_Loss_MMSCF'].cumsum()

            fig = px.line(
                x=cumulative_loss.index,
                y=cumulative_loss.values,
                labels={'x': 'Timestamp', 'y': 'Cumulative Gas Loss (MMSCF)'},
                title="Cumulative Gas Loss"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No gas loss data available")

    # Summary statistics
    st.divider()
    st.markdown("### Summary Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Date Range",
                  f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")

    with col2:
        if len(anomalies) > 0:
            avg_loss = anomalies['Gas_Loss_MMSCF'].mean() if 'Gas_Loss_MMSCF' in anomalies.columns else 0
            st.metric("Avg Gas Loss per Anomaly", f"{avg_loss:.6f} MMSCF")
        else:
            st.metric("Avg Gas Loss per Anomaly", "0 MMSCF")

    with col3:
        if len(df) > 0 and 'MAE' in df.columns:
            max_mae = df['MAE'].max()
            st.metric("Max MAE", f"{max_mae:.4f}")
        else:
            st.metric("Max MAE", "N/A")

st.divider()
st.caption(f"Data source: {csv_file} | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
