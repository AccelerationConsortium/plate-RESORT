#!/bin/bash
# Plate Resort API Server Runner
set -e

cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Read configuration from YAML file
CONFIG_FILE="resort_config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    # Extract server configuration using Python
    SERVER_IP=$(python -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    print(config.get('server', {}).get('ip', 'localhost'))
except:
    print('localhost')
")
    SERVER_PORT=$(python -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    print(config.get('server', {}).get('port', 8000))
except:
    print('8000')
")
    API_KEY=$(python -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    print(config.get('server', {}).get('api_key', 'changeme'))
except:
    print('changeme')
")
else
    SERVER_IP="localhost"
    SERVER_PORT="8000"
    API_KEY="changeme"
fi

# Set API key (use config value or environment override)
export PLATE_API_KEY=${PLATE_API_KEY:-"$API_KEY"}

echo "Starting Plate Resort API Server..."
echo "API Key: $PLATE_API_KEY"
echo "Server will be available at: http://$SERVER_IP:$SERVER_PORT"
echo "Documentation at: http://$SERVER_IP:$SERVER_PORT/docs"
echo "Local access: http://localhost:$SERVER_PORT"
echo ""

# Install FastAPI if not already installed
pip install fastapi uvicorn[standard] --quiet

# Run the FastAPI server using config values
python -m uvicorn server.main:app --host 0.0.0.0 --port $SERVER_PORT --reload