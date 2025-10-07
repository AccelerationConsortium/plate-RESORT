#!/bin/bash
#
# Plate Resort Server - One-line setup for Raspberry Pi
# Usage: curl -fsSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/main/plate-resort-multiple/install.sh | bash
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Plate Resort Server - Quick Setup${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? [y/N]: " continue_setup
    if [ "$continue_setup" != "y" ] && [ "$continue_setup" != "Y" ]; then
        exit 1
    fi
fi

# Create project directory
PROJECT_DIR="$HOME/plate-resort"
echo -e "${YELLOW}📁 Setting up project directory: $PROJECT_DIR${NC}"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Clone or update repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}📥 Updating existing repository...${NC}"
    git pull origin main
else
    echo -e "${YELLOW}📥 Cloning repository...${NC}"
    git clone https://github.com/AccelerationConsortium/plate-RESORT.git .
fi

# Update system packages
echo -e "${YELLOW}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install core dependencies (no GUI packages)
echo -e "${YELLOW}📦 Installing core dependencies...${NC}"
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-yaml \
    python3-venv \
    git \
    build-essential \
    udev

# Add user to dialout group for USB access
sudo usermod -aG dialout $USER

# Create and activate virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies in venv
echo -e "${YELLOW}� Installing Python packages in virtual environment...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Set up USB permissions for Dynamixel
echo -e "${YELLOW}🔌 Setting up USB device permissions...${NC}"
sudo tee /etc/udev/rules.d/99-dynamixel.rules > /dev/null << 'EOF'
# Dynamixel USB devices
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout"
# Generic USB-to-serial adapters
SUBSYSTEM=="tty", KERNEL=="ttyUSB*", MODE="0666", GROUP="dialout"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger

# Create simple startup script
echo -e "${YELLOW}🔧 Creating startup script...${NC}"
cat > run_server.sh << 'EOF'
#!/bin/bash
# Plate Resort Server Runner
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

echo "🚀 Starting Plate Resort Server..."
echo "Project directory: $(pwd)"
echo "Python environment: $(which python)"
echo ""

# Check USB devices
if ls /dev/ttyUSB* >/dev/null 2>&1; then
    echo "✅ USB devices found:"
    ls -la /dev/ttyUSB*
else
    echo "⚠️  No USB devices found. Connect Dynamixel adapter."
fi

echo ""
echo "Available commands:"
echo "  python plate_resort.py          # Run core control system"
echo "  python test_scripts/test_dxl_ping.py  # Test motor connection"
echo ""

# Default action - you can modify this
echo "Use the above commands to control your plate resort system."
EOF

chmod +x run_server.sh

# Test Python dependencies
echo -e "${YELLOW}🧪 Testing Python dependencies...${NC}"
source venv/bin/activate
python -c "
import sys
required = ['dynamixel_sdk', 'yaml']
missing = []

for module in required:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module} - MISSING')
        missing.append(module)

if missing:
    print(f'\\n❌ Missing modules: {missing}')
    sys.exit(1)
else:
    print('\\n✅ All core dependencies available!')
"

echo ""
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo ""
echo "📍 Installation location: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "1. 🔌 Connect your Dynamixel motor and USB adapter"
echo "2. 🔄 Reboot to apply group membership: sudo reboot"
echo "3. 🚀 After reboot, run: cd $PROJECT_DIR && ./run_server.sh"
echo ""
echo "Quick test commands:"
echo "  cd $PROJECT_DIR"
echo "  source venv/bin/activate"
echo "  python test_scripts/test_dxl_ping.py --device /dev/ttyUSB0"
echo ""
echo -e "${BLUE}📖 For documentation, see README.md${NC}"

# Option to reboot
echo ""
read -p "Reboot now to apply USB permissions? [y/N]: " reboot_now
if [ "$reboot_now" = "y" ] || [ "$reboot_now" = "Y" ]; then
    echo "Rebooting in 3 seconds... (Ctrl+C to cancel)"
    sleep 3
    sudo reboot
fi