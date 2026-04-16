#!/bin/bash

# GUARD Dashboard Launcher - Next.js/React Version
# Starts the Next.js development server

echo "🛡️  Starting GUARD Dashboard (Next.js/React)"
echo "============================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found!"
    echo "   Install from: https://nodejs.org/"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check if data file exists
DATA_FILE="../KODE_FIX/KODE FIX/AnomalyDetected_Test.csv"
if [ ! -f "$DATA_FILE" ]; then
    echo "⚠️  Warning: Data file not found"
    echo "   Expected at: $DATA_FILE"
    echo "   The dashboard may not load data correctly."
    echo ""
fi

echo "🚀 Launching Next.js development server..."
echo "   URL: http://localhost:3000"
echo "   Press Ctrl+C to stop"
echo ""
echo "✨ Features:"
echo "   - Real-time simulation playback"
echo "   - Interactive charts (MAE & sensors)"
echo "   - Live anomaly detection"
echo "   - AI chatbot assistant"
echo "   - Fully customizable UI"
echo ""

# Run Next.js development server
npm run dev
