#!/bin/bash
# MS-Oferta Performance Tester - Start Script

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     MS-Oferta Performance Tester - Starting...               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp .env.example .env
    echo "✅ .env created. Please edit it if needed."
fi

# Create necessary directories
mkdir -p database reports logs

echo ""
echo "🚀 Starting Performance Tester..."
echo ""

# Run the application
python run.py
