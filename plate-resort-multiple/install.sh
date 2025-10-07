#!/bin/bash
#
# Plate Resort Server - One-line installer for fresh or existing Pi
# Usage: curl -fsSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/ma# Install Python dependencies in venv
echo -e "${BLUE}Installing/updating Python packages in virtual environment...${NC}"
pip install --upgrade pip

# Check if requirements changed or this is fresh install
REQUIREMENTS_CHANGED=false
if [ -f "requirements.installed" ]; then
    if ! cmp -s requirements.txt requirements.installed; then
        REQUIREMENTS_CHANGED=true
    fi
else
    REQUIREMENTS_CHANGED=true
fi

if [ "$REQUIREMENTS_CHANGED" = true ]; then
    echo "Installing Python dependencies from requirements.txt..."
    pip install -r requirements.txt
    cp requirements.txt requirements.installed
    echo -e "${GREEN}Python packages installed${NC}"
else
    echo -e "${GREEN}Python packages up to date${NC}"
    # Still upgrade pip and check critical packages
    pip install --upgrade dynamixel-sdk pyyaml 2>/dev/null || true
fi

# Set up USB permissions for Dynamixel (check if rules already exist)
UDEV_RULES_FILE="/etc/udev/rules.d/99-dynamixel.rules"
if [ ! -f "$UDEV_RULES_FILE" ]; then
    echo -e "${BLUE}Setting up USB device permissions...${NC}"
    sudo tee "$UDEV_RULES_FILE" > /dev/null << 'EOF'
# Dynamixel USB devices
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout"
# Generic USB-to-serial adapters
SUBSYSTEM=="tty", KERNEL=="ttyUSB*", MODE="0666", GROUP="dialout"
EOF

    sudo udevadm control --reload-rules
    sudo udevadm trigger
    echo -e "${GREEN}USB permissions configured${NC}"
else
    echo -e "${GREEN}USB permissions already configured${NC}"
fiultiple/install.sh | bash
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Plate Resort Server - Smart Installer${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Detect installation type
FRESH_INSTALL=true
PROJECT_DIR="$HOME/plate-resort"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}Existing installation detected at $PROJECT_DIR${NC}"
    FRESH_INSTALL=false
    
    echo "Installation options:"
    echo "1. Update existing installation (recommended)"
    echo "2. Clean reinstall (removes current setup)"
    echo "3. Exit without changes"
    echo ""
    read -p "Choose option [1-3]: " install_option
    
    case $install_option in
        1)
            echo -e "${GREEN}Updating existing installation...${NC}"
            ;;
        2)
            echo -e "${YELLOW}Performing clean reinstall...${NC}"
            read -p "This will delete $PROJECT_DIR. Are you sure? [y/N]: " confirm_delete
            if [ "$confirm_delete" != "y" ] && [ "$confirm_delete" != "Y" ]; then
                echo "Installation cancelled."
                exit 0
            fi
            rm -rf "$PROJECT_DIR"
            FRESH_INSTALL=true
            ;;
        3)
            echo "Installation cancelled."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Exiting.${NC}"
            exit 1
            ;;
    esac
fi

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? [y/N]: " continue_setup
    if [ "$continue_setup" != "y" ] && [ "$continue_setup" != "Y" ]; then
        exit 1
    fi
fi

# Create project directory
echo -e "${BLUE}Setting up project directory: $PROJECT_DIR${NC}"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Clone or update repository
if [ -d ".git" ]; then
    echo -e "${BLUE}Updating existing repository...${NC}"
    git stash push -m "Auto-stash before update $(date)" 2>/dev/null || true
    git pull origin main
    echo -e "${GREEN}Repository updated${NC}"
else
    echo -e "${BLUE}Cloning repository...${NC}"
    git clone https://github.com/AccelerationConsortium/plate-RESORT.git .
    echo -e "${GREEN}Repository cloned${NC}"
fi

# Navigate to the correct subdirectory
cd plate-resort-multiple

# Check for existing virtual environment
VENV_EXISTS=false
if [ -d "venv" ]; then
    VENV_EXISTS=true
    echo -e "${YELLOW}Existing virtual environment found${NC}"
    
    # Test if venv is working
    if source venv/bin/activate && python -c "import sys; print('Python:', sys.executable)" 2>/dev/null; then
        echo -e "${GREEN}Virtual environment is functional${NC}"
        echo "Options:"
        echo "1. Keep existing venv and update packages"
        echo "2. Recreate virtual environment"
        echo ""
        read -p "Choose option [1-2]: " venv_option
        
        case $venv_option in
            1)
                echo -e "${GREEN}Keeping existing virtual environment${NC}"
                ;;
            2)
                echo -e "${YELLOW}Recreating virtual environment${NC}"
                rm -rf venv
                VENV_EXISTS=false
                ;;
            *)
                echo -e "${RED}Invalid option. Keeping existing venv.${NC}"
                ;;
        esac
    else
        echo -e "${RED}Virtual environment appears corrupted. Recreating...${NC}"
        rm -rf venv
        VENV_EXISTS=false
    fi
fi

# Update system packages (only if this seems like a fresh system)
if [ "$FRESH_INSTALL" = true ] || [ ! -f "/var/lib/apt/lists/lock" ]; then
    echo -e "${BLUE}Updating system packages...${NC}"
    sudo apt update
    
    # Only upgrade if user confirms (to avoid long waits on existing systems)
    if [ "$FRESH_INSTALL" = true ]; then
        sudo apt upgrade -y
    else
        read -p "Run system package upgrade? This may take a while [y/N]: " do_upgrade
        if [ "$do_upgrade" = "y" ] || [ "$do_upgrade" = "Y" ]; then
            sudo apt upgrade -y
        fi
    fi
fi

# Install core dependencies (check if already installed)
echo -e "${BLUE}Installing core dependencies...${NC}"
PACKAGES_TO_INSTALL=""

for pkg in python3-pip python3-dev python3-yaml python3-venv git build-essential udev; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL $pkg"
    fi
done

if [ -n "$PACKAGES_TO_INSTALL" ]; then
    echo "Installing missing packages:$PACKAGES_TO_INSTALL"
    sudo apt install -y $PACKAGES_TO_INSTALL
else
    echo -e "${GREEN}All required packages already installed${NC}"
fi

# Add user to dialout group (check if already member)
if ! groups $USER | grep -q "\bdialout\b"; then
    echo -e "${BLUE}Adding user to dialout group for USB access...${NC}"
    sudo usermod -aG dialout $USER
    echo -e "${YELLOW}Note: You'll need to log out/in or reboot for group changes to take effect${NC}"
else
    echo -e "${GREEN}User already in dialout group${NC}"
fi

# Create or update virtual environment
if [ "$VENV_EXISTS" = false ]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

echo -e "${BLUE}Activating virtual environment and installing packages...${NC}"
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

# Create or update startup scripts
echo -e "${BLUE}Setting up startup scripts...${NC}"

# Update the basic run_server.sh if it exists, or create it
if [ -f "run_server.sh" ] && [ "$FRESH_INSTALL" = false ]; then
    echo -e "${YELLOW}Existing run_server.sh found. Backing up...${NC}"
    cp run_server.sh run_server.sh.backup.$(date +%Y%m%d_%H%M%S)
fi

cat > run_server.sh << 'EOF'
#!/bin/bash
# Plate Resort Server Runner
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

echo "Starting Plate Resort Server..."
echo "Project directory: $(pwd)"
echo "Python environment: $(which python)"
echo ""

# Check USB devices
if ls /dev/ttyUSB* >/dev/null 2>&1; then
    echo "USB devices found:"
    ls -la /dev/ttyUSB*
else
    echo "No USB devices found. Connect Dynamixel adapter."
fi

echo ""
echo "Available commands:"
echo "  python plate_resort.py          # Run core control system"
echo "  python test_scripts/test_dxl_ping.py  # Test motor connection"
echo "  ./server/run_server.sh          # Start FastAPI server"
echo ""

# Default action - you can modify this
echo "Use the above commands to control your plate resort system."
EOF

chmod +x run_server.sh

# Create FastAPI server runner if it doesn't exist
if [ ! -f "server/run_server.sh" ]; then
    mkdir -p server
    cat > server/run_server.sh << 'EOF'
#!/bin/bash
# FastAPI Server Runner
cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

echo "Starting FastAPI Plate Resort Server..."
echo "API Documentation: http://$(hostname -I | cut -d' ' -f1):8000/docs"
echo "Press Ctrl+C to stop"
echo ""

# Start the FastAPI server
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
EOF
    chmod +x server/run_server.sh
fi

# Test Python dependencies
echo -e "${BLUE}Testing Python dependencies...${NC}"
source venv/bin/activate

# Test core dependencies
python -c "
import sys
required = ['dynamixel_sdk', 'yaml', 'fastapi', 'uvicorn']
missing = []
working = []

for module in required:
    try:
        __import__(module)
        working.append(module)
    except ImportError:
        missing.append(module)

print(f'✅ Working: {working}')
if missing:
    print(f'❌ Missing: {missing}')
    print('\\n⚠️  Some dependencies missing. This may cause issues.')
    sys.exit(1)
else:
    print('\\n✅ All core dependencies available!')
"

# Test USB device access
echo -e "${BLUE}Checking USB device access...${NC}"
if ls /dev/ttyUSB* >/dev/null 2>&1; then
    echo -e "${GREEN}USB devices detected:${NC}"
    ls -la /dev/ttyUSB* 2>/dev/null || true
    
    # Test actual device access
    if [ -r "/dev/ttyUSB0" ]; then
        echo -e "${GREEN}USB device access: OK${NC}"
    else
        echo -e "${YELLOW}USB device access: May need reboot for group permissions${NC}"
    fi
else
    echo -e "${YELLOW}No USB devices currently connected${NC}"
fi

echo ""
echo -e "${GREEN}Setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}Installation Summary:${NC}"
echo "  Location: $PROJECT_DIR/plate-resort-multiple"
echo "  Virtual Environment: $([ "$VENV_EXISTS" = true ] && echo "Updated" || echo "Created")"
echo "  Installation Type: $([ "$FRESH_INSTALL" = true ] && echo "Fresh" || echo "Update")"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo "  cd $PROJECT_DIR/plate-resort-multiple"
echo "  ./run_server.sh                    # Basic interface"
echo "  ./server/run_server.sh             # Start FastAPI server"
echo ""
echo -e "${BLUE}Testing Commands:${NC}"
echo "  source venv/bin/activate"
echo "  python test_scripts/test_dxl_ping.py --device /dev/ttyUSB0"
echo ""

# Check if reboot might be needed
REBOOT_NEEDED=false
if ! groups $USER | grep -q "\bdialout\b"; then
    REBOOT_NEEDED=true
elif [ ! -r "/dev/ttyUSB0" ] 2>/dev/null && ls /dev/ttyUSB* >/dev/null 2>&1; then
    REBOOT_NEEDED=true
fi

if [ "$REBOOT_NEEDED" = true ]; then
    echo -e "${YELLOW}⚠️  Reboot recommended to apply USB permissions${NC}"
    echo ""
    read -p "Reboot now? [y/N]: " reboot_now
    if [ "$reboot_now" = "y" ] || [ "$reboot_now" = "Y" ]; then
        echo "Rebooting in 3 seconds... (Ctrl+C to cancel)"
        sleep 3
        sudo reboot
    fi
else
    echo -e "${GREEN}✅ System ready - no reboot needed${NC}"
fi

echo ""
echo "For documentation and troubleshooting, see README.md"