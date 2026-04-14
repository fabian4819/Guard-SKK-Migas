"""
i2AIMS Dashboard - Anomaly Detection & Monitoring System
Streamlit-based interactive dashboard for booster compressor monitoring
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from pathlib import Path

# Import your modules
from rca_pipeline import run_pipeline, run_lstm_detection, load_data, load_lstm_artifacts
from rule_engine import THRESHOLDS, match_scenario, get_non_normal_rules
from email_notifier import send_email_alert, EQUIPMENT_NAME, FIELD_NAME

# Page config
st.set_page_config(
    page_title="i2AIMS - CPP Donggi",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1976d2;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1976d2;
    }
    .status-normal {
        background-color: #4caf50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: 600;
    }
    .status-warning {
        background-color: #ff9800;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: 600;
    }
    .status-critical {
        background-color: #f44336;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "KODE_FIX" / "KODE FIX"
DEFAULT_CSV = DATA_DIR / "Historical_Data.csv"
DEFAULT_MODEL = DATA_DIR / "lstm_compressor_17.keras"
DEFAULT_SCALER = DATA_DIR / "scaler_17.pkl"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_anomaly_data(start_date, end_date):
    """Load and process anomaly data with caching."""
    try:
        anomalies, all_results, features = run_pipeline(
            csv_path=str(DEFAULT_CSV),
            model_path=str(DEFAULT_MODEL),
            scaler_path=str(DEFAULT_SCALER),
            data_start=start_date,
            data_end=end_date,
        )
        return anomalies, all_results, features
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None


def create_gauge_chart(value, min_val, max_val, low_thresh, high_thresh, title, unit):
    """Create a gauge chart for sensor reading."""

    # Determine color based on thresholds
    if value < low_thresh:
        color = "#f44336"  # Red
    elif value > high_thresh:
        color = "#f44336"  # Red
    else:
        color = "#4caf50"  # Green

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': f"{title}<br><span style='font-size:0.8em'>{unit}</span>"},
        delta={'reference': (low_thresh + high_thresh) / 2},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': color},
            'steps': [
                {'range': [min_val, low_thresh], 'color': "#ffebee"},
                {'range': [low_thresh, high_thresh], 'color': "#e8f5e9"},
                {'range': [high_thresh, max_val], 'color': "#ffebee"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': high_thresh
            }
        }
    ))

    fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def create_anomaly_timeline(all_results):
    """Create timeline chart showing MAE and anomalies."""

    fig = go.Figure()

    # MAE line
    fig.add_trace(go.Scatter(
        x=all_results.index,
        y=all_results['MAE'],
        mode='lines',
        name='MAE',
        line=dict(color='#1976d2', width=1),
        hovertemplate='%{x}<br>MAE: %{y:.4f}<extra></extra>'
    ))

    # Anomalies
    anomalies = all_results[all_results['status'] == 'ANOMALY']
    fig.add_trace(go.Scatter(
        x=anomalies.index,
        y=anomalies['MAE'],
        mode='markers',
        name='Anomaly',
        marker=dict(color='#f44336', size=8, symbol='x'),
        hovertemplate='%{x}<br>MAE: %{y:.4f}<br>ANOMALY<extra></extra>'
    ))

    # Threshold line (approximate)
    threshold = all_results['MAE'].quantile(0.95)
    fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                  annotation_text="Threshold")

    fig.update_layout(
        title="Anomaly Detection Timeline",
        xaxis_title="Timestamp",
        yaxis_title="Mean Absolute Error (MAE)",
        hovermode='x unified',
        height=400
    )

    return fig


def create_sensor_trends(all_results, features):
    """Create multi-line chart for sensor trends."""

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
        title="Sensor Readings Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Value",
        hovermode='x unified',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def create_contribution_chart(row):
    """Create pie chart showing contribution of each sensor to anomaly."""

    contributions = []
    labels = []

    for param in THRESHOLDS.keys():
        contrib_col = f"contrib_{param}"
        if contrib_col in row:
            contrib = row[contrib_col]
            if contrib > 0:
                contributions.append(contrib)
                labels.append(param)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=contributions,
        hole=0.3,
        marker=dict(colors=px.colors.qualitative.Set3)
    )])

    fig.update_layout(
        title="Anomaly Contribution by Sensor",
        height=350
    )

    return fig


def display_header():
    """Display dashboard header."""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f'<h1 class="main-header">🏭 i2AIMS - {FIELD_NAME}</h1>', unsafe_allow_html=True)
        st.markdown(f"**{EQUIPMENT_NAME}**")

    with col2:
        st.markdown(f"**Last Updated**")
        st.info(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def display_overview_metrics(anomalies, all_results):
    """Display overview metrics cards."""

    col1, col2, col3, col4 = st.columns(4)

    total_anomalies = len(anomalies)
    total_gas_loss = anomalies['Gas_Loss_MMSCF'].sum() if len(anomalies) > 0 else 0
    anomaly_rate = (total_anomalies / len(all_results) * 100) if len(all_results) > 0 else 0

    # Calculate current status
    if len(all_results) > 0:
        latest = all_results.iloc[-1]
        current_status = latest['status']
    else:
        current_status = "UNKNOWN"

    with col1:
        st.metric(
            label="Total Anomalies",
            value=total_anomalies,
            delta=f"{anomaly_rate:.1f}% of total"
        )

    with col2:
        st.metric(
            label="Gas Loss (MMSCF)",
            value=f"{total_gas_loss:.3f}",
            delta="Critical" if total_gas_loss > 10 else "Normal",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            label="Current Status",
            value=current_status,
            delta="Active" if current_status == "ANOMALY" else "Clear"
        )

    with col4:
        st.metric(
            label="Data Points",
            value=f"{len(all_results):,}",
            delta=f"Range: {len(all_results)} pts"
        )


def display_real_time_sensors(all_results):
    """Display real-time sensor readings with gauges."""

    st.subheader("📊 Real-Time Sensor Readings")

    if len(all_results) == 0:
        st.warning("No data available")
        return

    latest = all_results.iloc[-1]

    cols = st.columns(5)

    for i, (param, config) in enumerate(THRESHOLDS.items()):
        with cols[i]:
            value = latest.get(param, 0)

            # Calculate gauge range
            min_val = config['low'] * 0.8
            max_val = config['high'] * 1.2

            fig = create_gauge_chart(
                value=value,
                min_val=min_val,
                max_val=max_val,
                low_thresh=config['low'],
                high_thresh=config['high'],
                title=param.replace('_', ' '),
                unit=config['unit']
            )

            st.plotly_chart(fig, use_container_width=True)

            # Status badge
            rule_col = f"{param}_rule"
            if rule_col in latest:
                status = latest[rule_col]
                if status == "NORMAL":
                    st.markdown(f'<span class="status-normal">NORMAL</span>', unsafe_allow_html=True)
                elif status in ["HIGH", "LOW"]:
                    st.markdown(f'<span class="status-warning">{status}</span>', unsafe_allow_html=True)


def display_anomaly_table(anomalies):
    """Display detailed anomaly table."""

    st.subheader("📋 Anomaly Details")

    if len(anomalies) == 0:
        st.info("No anomalies detected in the selected period")
        return

    # Prepare display dataframe
    display_cols = ['MAE', 'threshold_ratio', 'exceed_percent', 'Gas_Loss_MMSCF']

    # Add sensor values
    for param in THRESHOLDS.keys():
        if param in anomalies.columns:
            display_cols.append(param)

    df_display = anomalies[display_cols].copy()
    df_display.index = df_display.index.strftime('%Y-%m-%d %H:%M:%S')

    # Format numbers
    df_display['MAE'] = df_display['MAE'].apply(lambda x: f"{x:.4f}")
    df_display['threshold_ratio'] = df_display['threshold_ratio'].apply(lambda x: f"{x:.1f}%")
    df_display['exceed_percent'] = df_display['exceed_percent'].apply(lambda x: f"{x:.1f}%")
    df_display['Gas_Loss_MMSCF'] = df_display['Gas_Loss_MMSCF'].apply(lambda x: f"{x:.6f}")

    st.dataframe(df_display, use_container_width=True, height=400)

    # Download button
    csv = anomalies.to_csv()
    st.download_button(
        label="📥 Download Anomaly Data (CSV)",
        data=csv,
        file_name=f"anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def display_scenario_analysis(anomalies):
    """Display scenario matching analysis."""

    st.subheader("🔍 Scenario Analysis")

    if len(anomalies) == 0:
        st.info("No scenarios to analyze")
        return

    # Count scenario matches
    scenario_counts = {}

    for idx, row in anomalies.iterrows():
        matches = match_scenario(row)
        if matches:
            for m in matches:
                name = m['name']
                severity = m['severity']
                key = f"{name} ({severity})"
                scenario_counts[key] = scenario_counts.get(key, 0) + 1

    if scenario_counts:
        # Create bar chart
        df_scenarios = pd.DataFrame(list(scenario_counts.items()),
                                     columns=['Scenario', 'Count'])
        df_scenarios = df_scenarios.sort_values('Count', ascending=True)

        fig = px.bar(df_scenarios, x='Count', y='Scenario', orientation='h',
                     title="Most Common Failure Scenarios",
                     color='Count',
                     color_continuous_scale='Reds')

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No known scenarios matched. Anomalies detected by LSTM but sensor values within rule thresholds.")


def display_anomaly_detail(row):
    """Display detailed analysis of a single anomaly."""

    st.subheader(f"🔬 Anomaly Detail: {row.name}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Basic Info")
        st.write(f"**MAE:** {row['MAE']:.4f}")
        st.write(f"**Threshold Ratio:** {row['threshold_ratio']:.1f}%")
        st.write(f"**Exceed Percent:** {row['exceed_percent']:.1f}%")
        st.write(f"**Gas Loss:** {row['Gas_Loss_MMSCF']:.6f} MMSCF")

        # Matched scenarios
        scenarios = match_scenario(row)
        if scenarios:
            st.markdown("### Matched Scenario")
            s = scenarios[0]
            st.error(f"**{s['name']}** (Severity: {s['severity']})")
            st.write(f"**Root Cause:** {s['root_cause']}")
            st.markdown("**Recommended Actions:**")
            for action in s['actions']:
                st.write(f"• {action}")

    with col2:
        st.markdown("### Contribution Analysis")
        fig = create_contribution_chart(row)
        st.plotly_chart(fig, use_container_width=True)

    # Sensor deviations
    st.markdown("### Sensor Deviations")

    dev_data = []
    for param, config in THRESHOLDS.items():
        value = row.get(param, 0)
        dev = row.get(f"dev_{param}", 0)
        expected = value - dev
        contrib = row.get(f"contrib_{param}", 0)
        rule = row.get(f"{param}_rule", "UNKNOWN")

        dev_pct = (dev / expected * 100) if expected != 0 else 0

        dev_data.append({
            "Parameter": param,
            "Tag": config['tag'],
            "Actual": f"{value:.2f} {config['unit']}",
            "Expected": f"{expected:.2f} {config['unit']}",
            "Deviation": f"{dev:+.2f} ({dev_pct:+.1f}%)",
            "Contribution": f"{contrib:.1f}%",
            "Status": rule
        })

    df_dev = pd.DataFrame(dev_data)
    st.dataframe(df_dev, use_container_width=True, hide_index=True)


def main():
    """Main dashboard application."""

    # Add title immediately so page isn't blank
    st.title("🏭 i2AIMS Dashboard")
    st.write("Loading...")

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1976d2/ffffff?text=i2AIMS", use_container_width=True)
        st.title("⚙️ Settings")

        # Date range selector
        st.subheader("Date Range")

        today = datetime.now()
        default_start = today - timedelta(days=7)  # Reduced to 7 days for faster initial load

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

        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.divider()

        # Email alert section
        st.subheader("📧 Email Alerts")

        if st.button("Send Test Email", use_container_width=True):
            st.info("Email alert feature - integrate with test_email.py")

        st.divider()

        # Info
        st.markdown("### About")
        st.info(f"""
        **Equipment:** {EQUIPMENT_NAME}

        **Field:** {FIELD_NAME}

        **Monitoring:** Real-time anomaly detection using LSTM autoencoder
        """)

    # Main content
    display_header()

    # Load data with progress indicator
    try:
        with st.spinner(f"Loading data from {start_date} to {end_date}... This may take 30-60 seconds on first load."):
            anomalies, all_results, features = load_anomaly_data(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        st.error("Please check:")
        st.write("- Data files exist in KODE_FIX/KODE FIX/")
        st.write("- Historical_Data.csv")
        st.write("- lstm_compressor_17.keras")
        st.write("- scaler_17.pkl")
        st.exception(e)
        return

    if all_results is None or len(all_results) == 0:
        st.error("No data loaded. Check file paths and date range.")
        return

    # Overview metrics
    display_overview_metrics(anomalies, all_results)

    st.divider()

    # Real-time sensors
    display_real_time_sensors(all_results)

    st.divider()

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Timeline", "📊 Sensors", "📋 Anomalies", "🔍 Analysis"])

    with tab1:
        st.plotly_chart(create_anomaly_timeline(all_results), use_container_width=True)

        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Data Points", f"{len(all_results):,}")
        with col2:
            st.metric("Anomalies Detected", len(anomalies))
        with col3:
            avg_mae = all_results['MAE'].mean()
            st.metric("Average MAE", f"{avg_mae:.4f}")

    with tab2:
        st.plotly_chart(create_sensor_trends(all_results, features), use_container_width=True)

        # Sensor statistics
        st.subheader("Sensor Statistics")

        sensor_stats = []
        for param, config in THRESHOLDS.items():
            if param in all_results.columns:
                values = all_results[param]
                sensor_stats.append({
                    "Parameter": param,
                    "Tag": config['tag'],
                    "Unit": config['unit'],
                    "Mean": f"{values.mean():.2f}",
                    "Min": f"{values.min():.2f}",
                    "Max": f"{values.max():.2f}",
                    "Std Dev": f"{values.std():.2f}",
                    "Low Thresh": config['low'],
                    "High Thresh": config['high']
                })

        df_stats = pd.DataFrame(sensor_stats)
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

    with tab3:
        display_anomaly_table(anomalies)

        # Detail view
        if len(anomalies) > 0:
            st.divider()
            selected_idx = st.selectbox(
                "Select anomaly for detailed analysis:",
                options=range(len(anomalies)),
                format_func=lambda i: f"{anomalies.index[i]} - MAE: {anomalies.iloc[i]['MAE']:.4f}"
            )

            if selected_idx is not None:
                display_anomaly_detail(anomalies.iloc[selected_idx])

    with tab4:
        display_scenario_analysis(anomalies)

        # Additional analytics
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Anomaly Distribution by Hour")
            if len(anomalies) > 0:
                anomalies_hour = anomalies.copy()
                anomalies_hour['hour'] = anomalies_hour.index.hour
                hour_counts = anomalies_hour['hour'].value_counts().sort_index()

                fig = px.bar(x=hour_counts.index, y=hour_counts.values,
                             labels={'x': 'Hour of Day', 'y': 'Anomaly Count'},
                             title="Anomalies by Hour of Day")
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Gas Loss Trend")
            if len(anomalies) > 0:
                fig = px.line(anomalies, y='Gas_Loss_MMSCF',
                              title="Cumulative Gas Loss Over Time")
                st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
