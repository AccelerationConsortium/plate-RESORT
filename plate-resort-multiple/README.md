# Plate Resort Control System

**Professional laboratory plate management system with REST API server-client architecture.**

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

# Use your API key from server installation
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY status
```

## 🎯 Usage

### 📡 Server (Runs automatically on Pi)

```bash
# Server auto-starts after installation
# Manual control if needed:
plate-resort-server                    # Start server
sudo systemctl stop plate-resort       # Stop service
sudo systemctl start plate-resort      # Start service
```

**Server automatically available at:** `http://YOUR_PI_IP:8000`
**API Documentation:** `http://YOUR_PI_IP:8000/docs`
### 💻 Client Commands

```bash
# Check server status
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY status

# Connect to motor
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY connect

# Activate hotel position
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY activate A

# Move to specific angle
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY move 90.0

# Get current position
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY position

# Disconnect motor
plate-resort-client --host YOUR_PI_IP --api-key YOUR_API_KEY disconnect
```

### 🐍 Python API

```python
from plate_resort.client import PlateResortClient

# Initialize client with your API key
client = PlateResortClient("http://YOUR_PI_IP:8000", "YOUR_API_KEY")

# Use the system
status = client.status()
client.connect()
client.activate_hotel("A")
position = client.get_position()
client.disconnect()
```

## � API Key Management

**Your API key is generated during installation and shown on screen.**

To regenerate or view your API key:
```bash
# On the Pi server
plate-resort-keygen --generate --update-config
```

## 📚 Documentation

- **Interactive API Docs:** `http://YOUR_PI_IP:8000/docs`
- **REST API:** 9 endpoints for complete motor control
- **Client Library:** Python package for easy integration

## 🧪 Testing & Development

### Test Scripts
```bash
# Test motor connection and functionality
cd test_scripts
python test_plate_resort.py      # Main functionality test
python test_motor_health.py      # Health monitoring
python test_dxl_ping.py          # Low-level motor test
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

## 🔒 Security Features

- **API Key Authentication:** All endpoints protected with secure keys
- **Request Validation:** Input sanitization and validation
- **Error Handling:** Graceful error responses
- **Rate Limiting:** Built-in FastAPI protections

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

## 🗂️ Package Structure

```
plate_resort/              # Professional Python package
├── core.py               # Motor control (unchanged from v1.x)
├── server/               # FastAPI REST API server  
│   ├── main.py          # Server application
│   └── wrapper.py       # Motor interface wrapper
├── client/              # Client library and CLI
│   ├── __init__.py      # Python client library
│   └── cli.py           # Command-line interface
├── setup.py             # Automated system setup
└── keygen.py            # API key generation

test_scripts/            # Hardware testing utilities
archived/                # Legacy components (v1.x)  
mechanical/              # Hardware documentation
install-pip.sh           # One-line installer
```

## 🐛 Troubleshooting

### Server Issues
```bash
# Check if server is running
curl http://localhost:8000/health

# View server logs  
sudo journalctl -u plate-resort -f

# Restart server service
sudo systemctl restart plate-resort
```

### Client Connection Issues
```bash
# Test network connectivity
ping YOUR_PI_IP

# Test API access (replace with your IP and key)
curl -H "X-API-Key: YOUR_API_KEY" http://YOUR_PI_IP:8000/status
```

### Motor Issues
```bash
# Check USB connection
ls /dev/ttyUSB*

# Test motor communication
cd test_scripts
python test_dxl_ping.py --device /dev/ttyUSB0 --id 1
```

## 🔄 Updates

To update the system:
```bash
# On the Pi server
pip install --upgrade git+https://github.com/AccelerationConsortium/plate-RESORT.git#subdirectory=plate-resort-multiple
sudo systemctl restart plate-resort
```

## 📝 Version History

- **v2.0**: Professional pip package with server-client architecture  
- **v1.x**: Direct script-based approach (archived)

---

## 💡 Key Improvement: Complete Automation

**Before (v1.x):** Complex manual setup with multiple scripts, Docker, and manual configuration.

**Now (v2.0):** One command installs everything and starts the server automatically. Just copy the API key to your client!

**Perfect for:** Laboratory automation, remote plate handling, integration with existing Python workflows.

### Server Won't Start
- Check if port 8000 is already in use
- Verify virtual environment is activated
- Check USB device connections

## 📄 License

See LICENSE file for details.

See [QUICK_SETUP.md](QUICK_SETUP.md) for details.

## Features

- **Automated Plate Rotation**: Precise Dynamixel motor control for hotel-based storage
- **Health Monitoring**: Real-time motor health and diagnostics
- **YAML Configuration**: Easy setup and customization
- **Simple Deployment**: Direct Python execution with dependency management
- **Safety Features**: Emergency stop with disconnect/reconnect recovery
- **Test Utilities**: Comprehensive motor testing tools

## Quick Start

### 1. Installation (Fresh Pi)
```bash
curl -fsSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/main/install.sh | bash
sudo reboot
```

### 2. Basic Usage (Server Only - No GUI)
```bash
cd ~/plate-resort

# Test motor connection
python3 test_scripts/test_dxl_ping.py --device /dev/ttyUSB0 --id 1

# Run basic example
python3 example_usage.py

# Use the core system directly
python3 -c "
from plate_resort import PlateResort
resort = PlateResort()
resort.connect()
print('Motor health:', resort.get_motor_health())
resort.activate_hotel('A')
"
```

Note: All commands should be run from `~/plate-resort/plate-resort-multiple` directory.

## Available Methods

The `PlateResort` class provides these core methods:

### Connection & Setup
- `connect()` - Connect to Dynamixel motor
- `disconnect()` - Disconnect from motor  
- `is_connected()` - Check connection status

### Motor Control
- `activate_hotel(hotel)` - Move to hotel position (A, B, C, D)
- `go_home()` - Return to home position
- `emergency_stop()` - Immediate motor stop
- `set_speed(speed)` - Change movement speed

### Status & Monitoring  
- `get_active_hotel()` - Get current hotel position
- `get_current_position()` - Get motor position in degrees
- `get_motor_health()` - Get health status dict
- `print_motor_health()` - Print formatted health info

### Example Usage
```python
from plate_resort import PlateResort

# Initialize and connect
resort = PlateResort("resort_config.yaml")
resort.connect()

# Move to hotel A
resort.activate_hotel('A')

# Check status
health = resort.get_motor_health()
current_hotel = resort.get_active_hotel()

# Emergency stop if needed
resort.emergency_stop()
```

## Core Functionality

- **Motor Control**: Direct Dynamixel servo control
- **Health Monitoring**: Real-time motor diagnostics  
- **Position Management**: Precise hotel positioning
- **Safety Features**: Emergency stop and error handling
- **Configuration**: YAML-based setup
```


## Configuration

Edit `resort_config.yaml` to customize:

```yaml
resort:
  # Hardware
  device: "/dev/ttyUSB0"
  baudrate: 57600
  motor_id: 1
  
  # Layout
  hotels: ["A", "B", "C", "D"]
  rooms_per_hotel: 20
  
  # Positioning
  offset_angle: 11.0
  rotation_direction: 1
  
  # Performance
  default_speed: 50
  position_tolerance: 0.5
  movement_timeout: 20
  
  # Safety
  goal_torque: 1023
  temperature_limit: 70
  current_limit: 2000
  voltage_min: 10.0
  voltage_max: 14.0
```

## Testing

```bash
# Basic functionality
python test_scripts/test_plate_resort.py

# Health monitoring
python test_scripts/test_motor_health.py

# Motor communication
python test_scripts/test_dxl_ping.py
```

## Hardware Setup

1. **Dynamixel Motor**: Robotis XM430-W210
2. **USB Interface**: USB2Dynamixel or equivalent
3. **Power**: 12V power supply for motor

## Troubleshooting

### Connection Issues
- Check USB device: `ls /dev/ttyUSB*`
- Verify permissions: `sudo chmod 666 /dev/ttyUSB0`
- Test ping: `python test_scripts/test_dxl_ping.py`

### Motor Issues
- Check power supply (12V)
- Verify motor ID (default: 1)
- Run health check: `python test_scripts/test_motor_health.py`

### Python Issues
- Check virtual environment activation
- Install dependencies: `pip install -r requirements.txt`
- Verify Python path and permissions

## Development

### File Structure
```
├── plate_resort.py        # Core motor control class
├── resort_config.yaml     # YAML configuration
├── example_usage.py       # Basic usage example
├── install.sh             # One-line installer
├── test_scripts/          # Test utilities and mock tests
├── archived_gui/          # Archived web interface components
├── mechanical/            # Hardware documentation
├── setup.sh               # Legacy system setup script
├── QUICK_SETUP.md         # Quick setup guide
├── PI_DEPLOYMENT.md       # Raspberry Pi setup guide
├── CHANGELOG.md           # Version history
└── requirements.txt       # Python dependencies
```

### Adding Features
1. Update `plate_resort.py` for new motor functions
2. Add test scripts in `test_scripts/` for validation
3. Update configuration in `resort_config.yaml` if needed
4. Document changes in `CHANGELOG.md`

## License

MIT License - See LICENSE file for details.