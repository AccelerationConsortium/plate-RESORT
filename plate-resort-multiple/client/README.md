# Server-Client API Examples

## Quick Examples

### Start the server:
```bash
cd ~/plate-resort/plate-resort-multiple
source venv/bin/activate
./server/run_server.sh
```

### Use the Python client:
```bash
# Connect to motor
python client/client.py connect

# Check status
python client/client.py status

# Move to hotel A
python client/client.py activate A

# Get motor health
python client/client.py health

# Emergency stop
python client/client.py stop
```

### Use curl directly:
```bash
# Set API key
API_KEY="changeme"
API_URL="http://your-pi-ip:8000"

# Connect
curl -X POST "$API_URL/connect" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"device": "/dev/ttyUSB0", "baudrate": 57600, "motor_id": 1}'

# Activate hotel A
curl -X POST "$API_URL/activate" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"hotel": "A"}'

# Get status
curl -X GET "$API_URL/status" -H "x-api-key: $API_KEY"
```

## Configuration

Set environment variables:
```bash
export PLATE_API_KEY="your-secret-key"
export PLATE_API_URL="http://your-pi-ip:8000"
```