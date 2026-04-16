#!/bin/bash

# GUARD Modern Dashboard Launcher
# LEADS-inspired professional interface

echo "🛡️ Starting GUARD Modern Dashboard..."
echo "======================================"
echo ""

# Check if streamlit is installed
if ! python3 -m streamlit --version &> /dev/null; then
    echo "❌ Streamlit not found!"
    echo "   Install with: pip3 install streamlit plotly openpyxl"
    exit 1
fi

# Check if Test.xlsx exists
if [ ! -f "Test.xlsx" ]; then
    echo "⚠️  Warning: Test.xlsx not found"
    echo "   Expected at: ./Test.xlsx"
fi

echo ""
echo "🚀 Launching modern dashboard..."
echo "   URL: http://localhost:8502"
echo "   Press Ctrl+C to stop"
echo ""

# Run Streamlit with optimized settings
python3 -m streamlit run dashboard_modern.py \
    --server.port=8502 \
    --server.address=localhost \
    --browser.gatherUsageStats=false \
    --theme.base=light \
    --theme.primaryColor="#2a5298" \
    --theme.backgroundColor="#ffffff" \
    --theme.secondaryBackgroundColor="#f5f5f5"
