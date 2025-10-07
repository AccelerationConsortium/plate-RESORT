# Plate Resort Control System

A complete plate storage automation system for laboratory well plate management.

## 🚀 Quick Setup (New Pi)

For a fresh Raspberry Pi, use the one-line installer:

# Plate Resort Control System

A complete plate storage automation system for laboratory well plate management with REST API server-client architecture.

## 🚀 Installation

### One-Line Installation (Server + Client)
```bash
# Installs both server and client tools with automatic setup
curl -fsSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/main/plate-resort-multiple/install-pip.sh | bash
```

### Manual Installation
```bash
# Install the package (works on any machine - Pi server or client)
pip install git+https://github.com/AccelerationConsortium/plate-RESORT.git#subdirectory=plate-resort-multiple

# Run setup (only needed on Pi server)
plate-resort-setup
```

## 🎯 Usage

### On Raspberry Pi (Server)
```bash
# Start the server
plate-resort-server

# Generate API key
plate-resort-keygen --generate --update-config
```

### On Any Machine (Client)
```bash
# Control the server remotely
plate-resort-client --host YOUR_PI_IP --api-key YOUR_KEY status
plate-resort-client --host YOUR_PI_IP --api-key YOUR_KEY connect
plate-resort-client --host YOUR_PI_IP --api-key YOUR_KEY activate A
```

### Python API (Any Machine)
```python
from plate_resort.client import PlateResortClient

client = PlateResortClient("http://YOUR_PI_IP:8000", "YOUR_API_KEY")
status = client.status()
client.connect()
client.activate_hotel("A")
```

## 📚 API Documentation

Visit `http://YOUR_PI_IP:8000/docs` for interactive API documentation.

## 🔧 Core Components

- **`plate_resort/`** - Professional Python package
  - `core.py` - Motor control logic (unchanged from v1.x)
  - `server/` - FastAPI REST API server
  - `client/` - Client library and CLI tools
  - `setup.py` - Automated system configuration
- **`test_scripts/`** - Hardware testing utilities  
- **`resort_config.yaml`** - Configuration template
- **`pyproject.toml`** - Modern Python packaging

## 🧪 Testing

```bash
# Test motor connection
source venv/bin/activate
python test_scripts/test_dxl_ping.py --device /dev/ttyUSB0

# Test core functionality  
python test_scripts/test_plate_resort.py

# Test motor health monitoring
python test_scripts/test_motor_health.py
```

## ⚙️ Configuration

Edit `resort_config.yaml` to configure:
- Motor settings and positions
- Hotel configurations
- Safety parameters
- Communication settings
- **Server IP and port**

### 🔐 API Key Setup

Generate a secure API key:
```bash
# Generate and update config file
python generate_api_key.py --generate --update-config

# Or set via environment variable
export PLATE_API_KEY="your-secure-key-here"
```
- Hotel configurations
- Safety parameters
- Communication settings

## 🔒 Security

The API uses API key authentication via the `X-API-Key` header. You can:

1. **Generate secure keys**: Use `generate_api_key.py` 
2. **Environment override**: Set `PLATE_API_KEY` environment variable
3. **Config file**: Update `api_key` in `resort_config.yaml`

⚠️ **Never commit real API keys to git!** The `.env` file is ignored by default.

## 📋 Hardware Requirements

- Raspberry Pi (3B+ or newer recommended)
- Dynamixel motors and controller
- USB-to-serial adapter for Dynamixel communication
- Power supply for motors

## 🗂️ Directory Structure

```
plate-resort-multiple/
├── server/              # FastAPI server
├── client/              # Python client library
├── test_scripts/        # Testing utilities
├── archived/           # Deprecated files
├── mechanical/         # Hardware documentation
├── plate_resort.py     # Core control class
├── install.sh          # One-line installer
└── update.sh           # Quick update script
```

## 🐛 Troubleshooting

### USB Permission Issues
```bash
sudo usermod -aG dialout $USER
sudo reboot
```

### Motor Not Responding
```bash
python test_scripts/test_dxl_ping.py --device /dev/ttyUSB0 --scan
```

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