#!/bin/bash

echo "🔍 GUARD Dashboard Setup Verification"
echo "======================================"
echo ""

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js installed: $NODE_VERSION"
else
    echo "❌ Node.js not found - install from https://nodejs.org/"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm installed: $NPM_VERSION"
else
    echo "❌ npm not found"
    exit 1
fi

echo ""
echo "📁 Checking project files..."

# Check key files
FILES=(
    "package.json"
    "next.config.js"
    "tailwind.config.ts"
    "tsconfig.json"
    "app/page.tsx"
    "app/layout.tsx"
    "components/StatsCard.tsx"
    "components/ControlPanel.tsx"
    "components/MAEChart.tsx"
    "components/SensorChart.tsx"
    "components/AlertsPanel.tsx"
    "components/Chatbot.tsx"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
    fi
done

echo ""
echo "📊 Checking data file..."
DATA_FILE="../KODE_FIX/KODE FIX/AnomalyDetected_Test.csv"
if [ -f "$DATA_FILE" ]; then
    LINE_COUNT=$(wc -l < "$DATA_FILE")
    echo "  ✅ Data file found ($LINE_COUNT lines)"
else
    echo "  ⚠️  Data file not found at: $DATA_FILE"
    echo "     Dashboard may not load data"
fi

echo ""
echo "📦 Checking node_modules..."
if [ -d "node_modules" ]; then
    echo "  ✅ Dependencies installed"
else
    echo "  ⚠️  Dependencies not installed"
    echo "     Run: npm install"
fi

echo ""
echo "🎯 Next Steps:"
echo "  1. If dependencies not installed: npm install"
echo "  2. Start the dashboard: ./run-dashboard.sh"
echo "  3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 Documentation:"
echo "  - QUICK_START.md - How to customize"
echo "  - README.md - Complete guide"
echo ""
