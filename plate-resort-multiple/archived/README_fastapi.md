# Plate Resort Control System

**Professional laboratory plate management system with Prefect v3 workflow orchestration.**

## 🚀 Quick Setup

### Installation

```bash
# Install the package
pip install git+https://github.com/AccelerationConsortium/plate-RESORT.git#subdirectory=plate-resort-multiple

# Or for development
git clone https://github.com/AccelerationConsortium/plate-RESORT.git
cd plate-RESORT/plate-resort-multiple
pip install -e .
```

### Prefect Setup

1. **Install Prefect**
   ```bash
   pip install prefect
   ```

2. **Start Prefect Server** (if not using Prefect Cloud)
   ```bash
   prefect server start
   ```
   Server will be available at http://127.0.0.1:4200

3. **Create Work Pool** (via UI or CLI)
   ```bash
   prefect work-pool create plate-resort-pool --type process
   ```

4. **Start Worker**
   ```bash
   prefect worker start --pool plate-resort-pool --type process
   ```

📚 **See [PREFECT_README.md](PREFECT_README.md) for complete setup instructions**

## 🎯 Usage

### Direct Flow Execution (Local)

```python
from device import connect, status, activate_hotel, get_position, go_home

# Connect to motor
connect(device="/dev/ttyUSB0", baudrate=57600, motor_id=1)

# Get status
current_status = status()
print(current_status)

# Move to hotel A
activate_hotel("A")

# Get position
position = get_position()
print(position)

# Go home
go_home()
```

### Via Deployments (Scheduled/Remote)

```python
from plate_resort.client import PlateResortClient

# Initialize client with your API key
client = PlateResortClient("http://YOUR_PI_IP:8000", "YOUR_API_KEY")

# Motor control
client.connect()
status = client.status()
health = client.health()

# Movement
client.activate_hotel("A")          # Move to hotel A, B, C, or D
client.move_to_angle(90.0)         # Move to specific angle
position = client.get_position()    # Get current position
client.go_home()                    # Return to home position

# Safety
client.emergency_stop()
client.disconnect()
```

## � API Key Management

**Your API key is generated during installation and shown on screen.**

To regenerate or view your API key:
```bash
# On the Pi server
plate-resort-keygen --generate --update-config
```

## � Project Structure

```
plate-resort-multiple/
├── 📦 plate_resort/           # Main package
│   ├── core.py               # Motor control logic
│   ├── client/               # Client tools
│   ├── server/               # REST API server
│   ├── setup.py              # System configuration
│   ├── keygen.py             # API key management
│   └── update.py             # Update utilities
├── 🎮 interactive_client.py   # Interactive CLI tool
├── 📊 demo_client.py          # Automated demo
├── 🔧 test_scripts/           # Hardware testing
├── 🏗️ install-pip.sh          # One-line installer
├── 📚 README.md               # This file
└── ⚙️ pyproject.toml          # Package configuration
```

## 🧪 Testing & Development

### Test Scripts
```bash
# Test motor connection and functionality  
cd test_scripts
python test_plate_resort.py      # Main functionality test
python test_motor_health.py      # Health monitoring
python test_dxl_ping.py          # Low-level motor test
```

### Interactive Tools
```bash
python interactive_client.py     # Interactive command line
python demo_client.py           # Automated demonstration
```

### Development Installation
```bash
# For development work
git clone https://github.com/AccelerationConsortium/plate-RESORT.git
cd plate-RESORT/plate-resort-multiple
pip install -e .                 # Install in development mode
```

## ⚙️ Configuration

The system uses `resort_config.yaml` for motor and hotel configuration. The default configuration works with most setups, but you can customize:

- Motor communication settings (port, baud rate, ID)
- Hotel positions and angles  
- Safety limits and timeouts
- Server settings

## 🔒 Security & Features

- **🔐 API Key Authentication:** All endpoints protected with secure keys
- **✅ Request Validation:** Input sanitization and validation  
- **🛡️ Error Handling:** Graceful error responses
- **🌐 REST API:** 9 endpoints for complete motor control
- **📚 Auto-Documentation:** Interactive API docs at `/docs`
- **🔄 One-Command Updates:** `plate-resort-update`

## 📋 System Requirements

### Raspberry Pi (Server)
- Raspberry Pi 3B+ or newer
- Raspberry Pi OS (modern version)  
- USB port for Dynamixel adapter
- Network connection

### Client Machine  
- Python 3.8+
- Network access to Pi server
- API key from server installation

### Hardware
- Dynamixel motor (XC330 or compatible)
- USB-to-RS485 adapter (U2D2 or FTDI)
- 12V power supply for motors

## � API Endpoints

The REST API provides complete motor control:

- `POST /connect` - Connect to motor
- `POST /disconnect` - Disconnect motor
- `GET /status` - Get system status
- `GET /health` - Motor health diagnostics
- `POST /activate` - Move to hotel position (A, B, C, D)
- `POST /move_to_angle` - Move to specific angle
- `GET /position` - Get current position
- `POST /home` - Return to home position
- `POST /emergency_stop` - Emergency stop

## 📚 Documentation

- **Interactive API Docs:** `http://YOUR_PI_IP:8000/docs`
- **OpenAPI Spec:** `http://YOUR_PI_IP:8000/openapi.json`
- **Test Scripts:** `test_scripts/README.md`

## 🐛 Troubleshooting

### Server Issues
```bash
# Check if server is running
sudo systemctl status plate-resort-server

# View server logs  
sudo journalctl -u plate-resort-server -f

# Restart server service
sudo systemctl restart plate-resort-server
```

### Client Connection Issues
```bash
# Test network connectivity
ping YOUR_PI_IP

# Test API access (replace with your IP and key)
curl -H "X-API-Key: YOUR_API_KEY" http://YOUR_PI_IP:8000/status
```

### Updates
```bash
# Update server to latest version
plate-resort-update

# Update client tools
pip install --upgrade git+https://github.com/AccelerationConsortium/plate-RESORT.git#subdirectory=plate-resort-multiple
```

## 🤝 Support

- **Issues:** [GitHub Issues](https://github.com/AccelerationConsortium/plate-RESORT/issues)
- **Documentation:** Visit `/docs` on your server for complete API reference
- **Hardware:** See `mechanical/` directory for BOM and specifications

---

**Ready to manage plates like a pro! 🍽️🤖**

