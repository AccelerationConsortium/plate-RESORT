# Plate Resort Control System

**Professional laboratory plate management system with REST API and Prefect workflow orchestration.**

## 🎯 Control Options

This system offers two ways to control the Plate Resort:

1. **REST API** (Traditional) - Simple HTTP endpoints for basic operations
2. **Prefect Workflows** (Recommended) - Robust workflow orchestration with retry logic, observability, and async execution

See [`prefect_flows/README.md`](prefect_flows/README.md) for Prefect setup and usage.

## 🚀 Quick Setup

### Server Setup (Raspberry Pi)

**One command installs everything and starts the server:**

```bash
curl -sSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/main/plate-resort-multiple/install-pip.sh | bash
```

**That's it!** The installer:
- ✅ Installs the package and dependencies
- ✅ Configures system permissions 
- ✅ Generates a secure API key
- ✅ **Automatically starts the server**
- ✅ Sets up systemd service for auto-start

**Your API key will be displayed during installation - save it for client access!**

### Client Setup (Any Machine)

```bash
# Install client tools
pip install git+https://github.com/AccelerationConsortium/plate-RESORT.git#subdirectory=plate-resort-multiple

# Configure client credentials (recommended)
cp secrets.ini.template secrets.ini
# Edit secrets.ini with your Pi IP and API key

# Or use command line directly
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY status
```

### 🔐 Client Configuration

**Option 1: secrets.ini file (recommended)**
```bash
# Copy and edit the template
cp secrets.ini.template secrets.ini

# Edit secrets.ini:
[server]
api_key = YOUR_API_KEY_FROM_PI_INSTALLATION

[client]  
default_host = YOUR_PI_IP
default_port = 8000
```

**Option 2: Environment variables**
```bash
export PLATE_API_KEY=YOUR_API_KEY
export PLATE_HOST=YOUR_PI_IP
export PLATE_PORT=8000
```

**Option 3: Command line arguments**
```bash
python interactive_client.py YOUR_PI_IP YOUR_API_KEY
python demo_client.py YOUR_PI_IP YOUR_API_KEY
```

## 🎯 Usage

### 📡 Server Management

```bash
# Server auto-starts after installation
plate-resort-update                    # Update to latest version
sudo systemctl status plate-resort-server  # Check status
sudo systemctl restart plate-resort-server # Restart service
```

**Server automatically available at:** `http://YOUR_PI_IP:8000`  
**API Documentation:** `http://YOUR_PI_IP:8000/docs`

### 💻 Client Tools

#### Command Line Interface
```bash
# Motor control
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY connect
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY status
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY health

# Movement commands
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY activate A
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY move 90
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY position
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY home

# Emergency stop
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY stop
```

#### Interactive Client
```bash
# Start interactive session
python interactive_client.py

# Then use commands like:
# connect, status, move 90, position, activate A, home, stop, quit
```

#### Demo Client
```bash
# Run automated demonstration
python demo_client.py
```

### 🐍 Python API

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

## 🌊 Prefect Workflow Orchestration (Recommended)

For production use, Prefect provides superior reliability and observability:

```bash
# Install with Prefect support
pip install git+https://github.com/AccelerationConsortium/plate-RESORT.git#subdirectory=plate-resort-multiple

# Setup work pool
prefect work-pool create plate-resort-pool --type process

# Deploy flows
cd prefect_flows
python deploy_flows.py

# Start worker on device
prefect worker start --pool plate-resort-pool
```

**Benefits over REST API:**
- Automatic retry on failure
- Built-in observability and monitoring
- Async execution with better performance
- No exposed HTTP endpoints needed
- Workflow scheduling capabilities

See [`prefect_flows/README.md`](prefect_flows/README.md) for complete setup guide.

## 🌐 API Endpoints

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

