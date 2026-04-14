#!/bin/bash

# i2AIMS Dashboard Launcher
# Starts the Streamlit dashboard with proper configuration

echo "🏭 Starting i2AIMS Dashboard..."
echo "================================"
echo ""

# Check if streamlit is installed
if ! python3 -m streamlit --version &> /dev/null; then
    echo "❌ Streamlit not found!"
    echo "   Install with: pip3 install streamlit plotly"
    exit 1
fi

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "✓ Loading .env configuration"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if required files exist
if [ ! -f "KODE_FIX/KODE FIX/Historical_Data.csv" ]; then
    echo "⚠️  Warning: Historical_Data.csv not found"
    echo "   Expected at: KODE_FIX/KODE FIX/Historical_Data.csv"
fi

if [ ! -f "KODE_FIX/KODE FIX/lstm_compressor_17.keras" ]; then
    echo "⚠️  Warning: LSTM model not found"
    echo "   Expected at: KODE_FIX/KODE FIX/lstm_compressor_17.keras"
fi

echo ""
echo "🚀 Launching dashboard..."
echo "   URL: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

# Run Streamlit with optimized settings
python3 -m streamlit run dashboard.py \
    --server.port=8501 \
    --server.address=localhost \
    --browser.gatherUsageStats=false \
    --theme.base=light \
    --theme.primaryColor="#1976d2" \
    --theme.backgroundColor="#ffffff" \
    --theme.secondaryBackgroundColor="#f5f5f5"
