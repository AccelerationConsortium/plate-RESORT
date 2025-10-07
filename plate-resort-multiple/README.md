# Plate Resort Control System

A complete plate storage automation system for laboratory well plate management.

## 🚀 Quick Setup (New Pi)

For a fresh Raspberry Pi, use the one-line installer:

```bash
curl -fsSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/main/install.sh | bash
```

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