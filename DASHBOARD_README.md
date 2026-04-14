# i2AIMS Interactive Dashboard

Real-time monitoring and visualization dashboard for booster compressor anomaly detection.

## Features

### 📊 Overview Metrics
- Total anomalies detected
- Cumulative gas loss (MMSCF)
- Current system status
- Data point statistics

### 🎛️ Real-Time Monitoring
- Live sensor readings with gauges
- Color-coded status indicators (GREEN/YELLOW/RED)
- Threshold visualization
- Individual sensor cards for:
  - Flow Rate (MMSCFD)
  - Suction Pressure (barg)
  - Discharge Pressure (barg)
  - Suction Temperature (°C)
  - Discharge Temperature (°C)

### 📈 Timeline View
- Interactive time series chart
- MAE (Mean Absolute Error) over time
- Anomaly markers
- Threshold line
- Zoomable and pannable

### 📊 Sensor Dashboard
- Multi-line chart for all sensors
- Sensor statistics table (mean, min, max, std dev)
- Threshold comparison
- Trend analysis

### 📋 Anomaly Table
- Sortable and filterable table
- Detailed anomaly information
- Export to CSV functionality
- Searchable data

### 🔍 Analysis Tools
- Anomaly contribution pie chart
- Scenario matching results
- Root cause analysis
- Recommended corrective actions
- Sensor deviation analysis

### 📉 Analytics
- Anomaly distribution by hour
- Gas loss trends
- Failure scenario frequency
- Performance metrics

## Quick Start

### 1. Install Dependencies

```bash
pip install streamlit plotly pandas numpy
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 2. Run Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

### 3. Navigate

- **Sidebar**: Configure date range, refresh data, access settings
- **Main View**: Overview metrics and real-time sensors
- **Tabs**: Switch between Timeline, Sensors, Anomalies, and Analysis views

## Dashboard Sections

### Overview Panel

Displays key metrics at a glance:
- **Total Anomalies**: Count of detected anomalies in selected period
- **Gas Loss**: Cumulative production loss in MMSCF
- **Current Status**: Real-time system status (NORMAL/ANOMALY)
- **Data Points**: Total number of data points analyzed

### Real-Time Sensors

Visual gauges showing:
- Current sensor value
- Normal operating range (green zone)
- Warning zones (red zones)
- Delta from target value
- Status badge (NORMAL/HIGH/LOW)

### Timeline Tab

Interactive chart features:
- Blue line: MAE values over time
- Red markers: Detected anomalies
- Dashed line: Threshold
- Hover info: Detailed values
- Click and drag to zoom
- Double-click to reset

### Sensors Tab

Multi-line chart showing:
- All sensor readings on one chart
- Individual sensor trends
- Correlation visualization
- Statistics table with:
  - Mean, Min, Max values
  - Standard deviation
  - Threshold ranges

### Anomalies Tab

Comprehensive anomaly table:
- Timestamp of detection
- MAE score
- Threshold ratio and exceedance
- Gas loss per anomaly
- All sensor readings
- Download as CSV button

**Detail View:**
- Select any anomaly for deep dive
- Contribution breakdown (pie chart)
- Matched scenarios
- Root cause explanation
- Recommended actions
- Sensor deviation table

### Analysis Tab

Advanced analytics:
- **Scenario Analysis**: Bar chart of most common failure patterns
- **Hourly Distribution**: When anomalies occur most frequently
- **Gas Loss Trend**: Cumulative impact over time
- **Pattern Recognition**: Identify recurring issues

## Configuration

### Date Range

Use sidebar to select:
- Start date
- End date
- Refresh data button

### Auto-Refresh

Data is cached for 5 minutes. Click "🔄 Refresh Data" to reload.

### Custom Paths

Edit `dashboard.py` to change data paths:

```python
DATA_DIR = BASE_DIR / "KODE_FIX" / "KODE FIX"
DEFAULT_CSV = DATA_DIR / "Historical_Data.csv"
DEFAULT_MODEL = DATA_DIR / "lstm_compressor_17.keras"
DEFAULT_SCALER = DATA_DIR / "scaler_17.pkl"
```

## Deployment Options

### Option 1: Local Development

```bash
streamlit run dashboard.py
```

Access at: `http://localhost:8501`

### Option 2: Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect repository
4. Deploy!

Free tier includes:
- 1 GB RAM
- Unlimited public apps
- Auto-deploy on git push

### Option 3: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t i2aims-dashboard .
docker run -p 8501:8501 i2aims-dashboard
```

### Option 4: Production Server

For production deployment with authentication:

```bash
# Install dependencies
pip install streamlit plotly pandas numpy

# Create systemd service
sudo nano /etc/systemd/system/i2aims-dashboard.service
```

Service file:

```ini
[Unit]
Description=i2AIMS Dashboard
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/skkmigas
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable i2aims-dashboard
sudo systemctl start i2aims-dashboard
```

### Option 5: Behind Nginx Reverse Proxy

Nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Customization

### Change Colors

Edit custom CSS in `dashboard.py`:

```python
st.markdown("""
<style>
    .main-header {
        color: #YOUR_COLOR;
    }
</style>
""", unsafe_allow_html=True)
```

### Add Logo

Replace placeholder image in sidebar:

```python
st.image("path/to/your/logo.png", use_container_width=True)
```

### Modify Metrics

Add custom metrics in `display_overview_metrics()`:

```python
with col5:
    st.metric(
        label="Your Metric",
        value=your_value,
        delta=your_delta
    )
```

### Add New Charts

Use Plotly for interactive charts:

```python
import plotly.express as px

fig = px.line(data, x='timestamp', y='value')
st.plotly_chart(fig, use_container_width=True)
```

## Performance Tips

### 1. Data Caching

The dashboard uses `@st.cache_data` to cache results for 5 minutes:

```python
@st.cache_data(ttl=300)
def load_anomaly_data(start_date, end_date):
    # Cached for 300 seconds
```

### 2. Limit Date Range

For large datasets, limit the date range to improve performance.

### 3. Pagination

For very large anomaly tables, consider adding pagination:

```python
page_size = 100
page = st.slider("Page", 1, len(anomalies) // page_size + 1)
start_idx = (page - 1) * page_size
end_idx = start_idx + page_size
st.dataframe(anomalies.iloc[start_idx:end_idx])
```

### 4. Lazy Loading

Load detailed analysis only when needed (already implemented in anomaly detail view).

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"

```bash
pip install streamlit plotly
```

### Dashboard is slow

- Reduce date range
- Clear cache with "Refresh Data" button
- Check data file size
- Consider pagination for large tables

### Plots not showing

- Check if plotly is installed: `pip install plotly`
- Verify data is loaded correctly
- Check browser console for errors

### Data not updating

- Click "🔄 Refresh Data" to clear cache
- Check file paths are correct
- Verify model and scaler files exist

## Keyboard Shortcuts

- `R`: Rerun the app
- `Ctrl+R` / `Cmd+R`: Refresh page
- `C`: Clear cache
- `?`: Show keyboard shortcuts

## Mobile Support

The dashboard is responsive and works on mobile devices:
- Touch-friendly controls
- Responsive layouts
- Optimized charts for small screens

## API Integration (Future)

To add REST API endpoints, consider using FastAPI alongside Streamlit:

```python
# api.py
from fastapi import FastAPI
from dashboard import load_anomaly_data

app = FastAPI()

@app.get("/api/anomalies")
def get_anomalies(start: str, end: str):
    anomalies, _, _ = load_anomaly_data(start, end)
    return anomalies.to_dict('records')
```

Run both:

```bash
# Terminal 1
streamlit run dashboard.py

# Terminal 2
uvicorn api:app --port 8000
```

## Security

### Authentication

Add basic authentication:

```python
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    credentials,
    'cookie_name',
    'signature_key',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Show dashboard
    main()
elif authentication_status == False:
    st.error('Username/password is incorrect')
```

### HTTPS

Use reverse proxy (Nginx/Caddy) for HTTPS in production.

### Environment Variables

Store sensitive data in `.env`:

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('API_KEY')
```

## Support

For issues or questions:
- Check this README
- Review error messages in terminal
- Check Streamlit logs: `~/.streamlit/`
- Streamlit docs: https://docs.streamlit.io

## Changelog

### Version 1.0 (2026-04-12)
- Initial release
- Real-time monitoring
- Anomaly timeline
- Sensor dashboard
- Analysis tools
- Export functionality

## License

Copyright © 2026 SKK Migas - CPP Donggi

---

**Built with:**
- [Streamlit](https://streamlit.io) - Interactive web app framework
- [Plotly](https://plotly.com) - Interactive charts
- [Pandas](https://pandas.pydata.org) - Data processing
- [TensorFlow](https://tensorflow.org) - ML inference
