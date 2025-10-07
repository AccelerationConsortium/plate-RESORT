#!/bin/bash
#
# Plate Resort - Pip Installation Script
# Usage: curl -fsSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/main/plate-resort-multiple/install-pip.sh | bash
#

set -e

echo "🚀 Plate Resort - Pip Installation"
echo "=================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    echo "Install Python 3: sudo apt install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Python version: $PYTHON_VERSION"

# Install pip and venv if not available
if ! command -v pip3 &> /dev/null; then
    echo "📦 Installing pip and venv..."
    sudo apt update
    sudo apt install -y python3-pip python3-venv python3-full
fi

# Create virtual environment
VENV_DIR="$HOME/plate-resort-env"
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install/upgrade plate-resort
echo "📦 Installing Plate Resort..."
pip install --upgrade git+https://github.com/AccelerationConsortium/plate-RESORT.git#subdirectory=plate-resort-multiple

# Add virtual environment bin to PATH if not already there
VENV_BIN="$VENV_DIR/bin"
if [[ ":$PATH:" != *":$VENV_BIN:"* ]]; then
    echo "🔧 Adding virtual environment to PATH..."
    echo "export PATH=\"$VENV_BIN:\$PATH\"" >> ~/.bashrc
    export PATH="$VENV_BIN:$PATH"
fi

# Run setup
echo "⚙️  Running system setup..."
plate-resort-setup

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 Quick start:"
echo "  plate-resort-server                    # Start server"
echo "  plate-resort-client --help             # Client help"
echo "  plate-resort-keygen --generate         # Generate API key"
echo ""
echo "📖 Documentation: http://localhost:8000/docs"
echo ""

# Option to start server
read -p "Start the server now? [y/N]: " start_server
if [ "$start_server" = "y" ] || [ "$start_server" = "Y" ]; then
    echo "Starting Plate Resort Server..."
    plate-resort-server
fi