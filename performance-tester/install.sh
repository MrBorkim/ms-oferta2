#!/bin/bash
# MS-Oferta Performance Tester - Installation Script

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     MS-Oferta Performance Tester - Installation              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $PYTHON_VERSION"

# Check required Python version (3.9+)
REQUIRED_VERSION="3.9"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.9+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create .env file
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "⚠️  .env file already exists, skipping..."
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p database reports logs static/css
echo "✅ Directories created"

# Make scripts executable
echo ""
echo "🔐 Making scripts executable..."
chmod +x start.sh
chmod +x run.py
echo "✅ Scripts are now executable"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              Installation completed successfully!            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env file if needed: nano .env"
echo "   2. Make sure MS-Oferta API is running on port 8000"
echo "   3. Start the tester: ./start.sh"
echo "   4. Open browser: http://localhost:5000"
echo ""
