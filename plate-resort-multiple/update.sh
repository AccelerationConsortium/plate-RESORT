#!/bin/bash
#
# Plate Resort Server - Quick Update Script
# For existing installations only
# Usage: ./update.sh
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Plate Resort Server - Quick Update${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "plate_resort.py" ] || [ ! -f "requirements.txt" ]; then
    echo "Error: This doesn't appear to be the plate-resort directory"
    echo "Please run this script from the plate-resort-multiple directory"
    exit 1
fi

# Update git repository
echo -e "${BLUE}Updating repository...${NC}"
git stash push -m "Auto-stash before update $(date)" 2>/dev/null || true
git pull origin main
echo -e "${GREEN}Repository updated${NC}"

# Update Python packages if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${BLUE}Updating Python packages...${NC}"
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt --upgrade
    echo -e "${GREEN}Python packages updated${NC}"
else
    echo -e "${YELLOW}No virtual environment found. Run the full installer first.${NC}"
fi

# Test dependencies
echo -e "${BLUE}Testing dependencies...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    python -c "
import sys
required = ['dynamixel_sdk', 'yaml', 'fastapi', 'uvicorn']
missing = []

for module in required:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print(f'❌ Missing modules: {missing}')
    sys.exit(1)
else:
    print('✅ All dependencies OK')
"
fi

echo ""
echo -e "${GREEN}Update completed successfully!${NC}"
echo ""
echo -e "${BLUE}Ready to run:${NC}"
echo "  ./run_server.sh                    # Basic interface"
echo "  ./server/run_server.sh             # FastAPI server"
echo ""