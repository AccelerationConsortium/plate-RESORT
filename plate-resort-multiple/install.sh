#!/bin/bash
#
# Plate Resort - Prefect Workflow Installation Script
# Usage: curl -fsSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/copilot/replace-rest-api-with-prefect/plate-resort-multiple/install.sh | bash
#

set -e

echo "🚀 Plate Resort - Prefect Workflow Installation"
echo "=============================================="
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

# Install/upgrade plate-resort with Prefect
echo "📦 Installing Plate Resort with Prefect workflows..."
pip install --upgrade git+https://github.com/AccelerationConsortium/plate-RESORT.git@copilot/replace-rest-api-with-prefect#subdirectory=plate-resort-multiple

# Add virtual environment bin to PATH if not already there
VENV_BIN="$VENV_DIR/bin"
if [[ ":$PATH:" != *":$VENV_BIN:"* ]]; then
    echo "🔧 Adding virtual environment to PATH..."
    echo "export PATH=\"$VENV_BIN:\$PATH\"" >> ~/.bashrc
    export PATH="$VENV_BIN:$PATH"
fi

# Auto-activate venv in new shells
echo "🔄 Setting up automatic venv activation..."
BASHRC_LINE="source $VENV_DIR/bin/activate"
if ! grep -Fxq "$BASHRC_LINE" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Auto-activate plate-resort virtual environment" >> ~/.bashrc
    echo "$BASHRC_LINE" >> ~/.bashrc
    echo "✅ Added auto-activation to ~/.bashrc"
else
    echo "✅ Auto-activation already configured"
fi

# Create configuration directory
echo "⚙️  Setting up configuration..."
mkdir -p ~/plate-resort-config
cd ~/plate-resort-config

# Copy default configuration
python3 -c "
import shutil
import os
from pathlib import Path

# Find the installed package
import plate_resort
package_dir = Path(plate_resort.__file__).parent

# Copy config files
config_src = package_dir / 'config'
if config_src.exists():
    if (config_src / 'defaults.yaml').exists():
        shutil.copy(config_src / 'defaults.yaml', '.')
        print('✅ Copied defaults.yaml')
    if (config_src / 'secrets.ini.template').exists():
        shutil.copy(config_src / 'secrets.ini.template', '.')
        print('✅ Copied secrets.ini.template')
        # Create initial secrets.ini
        shutil.copy('secrets.ini.template', 'secrets.ini')
        print('✅ Created secrets.ini from template')
else:
    print('⚠️  Config directory not found in package')
"

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 Virtual environment will auto-activate in new terminals!"
echo "🔄 To activate in current terminal: source $VENV_DIR/bin/activate"
echo ""
echo "📖 Configuration: ~/plate-resort-config/"
echo "🔧 Edit ~/plate-resort-config/secrets.ini with your Pi's IP"
echo ""
echo "🎯 Available commands:"
echo "  plate-resort-interactive            # Interactive client"
echo "  plate-resort-demo                   # Demo flows"
echo "  plate-resort-worker                 # Start worker service"
echo ""

# Reload current shell to activate venv
echo "� Activating virtual environment for current session..."
source "$VENV_DIR/bin/activate"

# Option to start interactive client
read -p "Start the interactive client now? [y/N]: " start_client
if [ "$start_client" = "y" ] || [ "$start_client" = "Y" ]; then
    echo "Starting Plate Resort Interactive Client..."
    plate-resort-interactive
fi