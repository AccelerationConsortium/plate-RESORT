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

### Optional: Prefect UI (for monitoring)

```bash
# Start Prefect server for UI monitoring
prefect server start
```
Then visit http://127.0.0.1:4200 to view flow runs

📚 **See [PREFECT_README.md](PREFECT_README.md) for detailed Prefect features**

## 🎯 Usage

### Basic Usage

All `PlateResort` methods are Prefect flows, so use them normally:

```python
from plate_resort.core import PlateResort

# Create instance
resort = PlateResort()

# Use methods - they're automatically Prefect flows
resort.connect()
resort.activate_hotel("A")
position = resort.get_current_position()
print(f"Current position: {position}")
resort.go_home()
resort.disconnect()
```

### Example Scripts

```bash
# Simple usage example
python example_usage.py

# Orchestration example
python orchestrator.py
```

### Available Methods (All are Prefect Flows)

- `connect()` - Connect to Dynamixel motor
- `disconnect()` - Disconnect from motor
- `activate_hotel(hotel)` - Move to specified hotel (A, B, C, D)
- `go_home()` - Return to home position
- `move_to_angle(angle)` - Move to specific angle in degrees
- `get_current_position()` - Get current motor position
- `get_motor_health()` - Get motor health diagnostics
- `set_speed(speed)` - Set motor movement speed
- `emergency_stop()` - Emergency stop motor

## 📦 Project Structure

```
plate-resort-multiple/
├── plate_resort/          # Core package
│   ├── core.py           # PlateResort class with @flow decorated methods
│   ├── setup.py          # System configuration
│   ├── keygen.py         # API key management (legacy)
│   └── update.py         # Update utilities
├── example_usage.py       # Simple usage example
├── orchestrator.py        # Orchestration example
├── PREFECT_README.md      # Detailed Prefect guide
├── test_scripts/          # Hardware testing
├── archived/              # Legacy REST API code
└── pyproject.toml         # Package configuration
```

## 🧪 Testing & Development

### Test Motor Hardware

```bash
cd test_scripts
python test_plate_resort.py      # Main functionality test
python test_motor_health.py      # Health monitoring
python test_dxl_ping.py          # Low-level motor test
```

### Development Installation

```bash
git clone https://github.com/AccelerationConsortium/plate-RESORT.git
cd plate-RESORT/plate-resort-multiple
pip install -e .
```

## ⚙️ Configuration

The system uses `plate_resort/resort_config.yaml` for motor and hotel configuration:

- Motor communication settings (port, baud rate, ID)
- Hotel positions and angles
- Safety limits and timeouts

## 🔒 Features

- **Simple API**: Use methods normally, Prefect handles orchestration
- **Automatic Tracking**: All method calls tracked if Prefect server is running
- **Monitoring**: View execution in Prefect UI
- **Retry Logic**: Built-in retry capabilities
- **State Management**: Track flow run states

## 📋 System Requirements

### Hardware
- Dynamixel motor (XC330 or compatible)
- USB-to-RS485 adapter (U2D2 or FTDI)
- 12V power supply for motors

### Software
- Python 3.8+
- Prefect v3
- dynamixel-sdk
- pyyaml

## 📚 Documentation

- **Prefect UI**: http://127.0.0.1:4200 (if server running)
- **Setup Guide**: [PREFECT_README.md](PREFECT_README.md)
- **Test Scripts**: [test_scripts/](test_scripts/)
- **Hardware**: [mechanical/](mechanical/) for BOM

## 🐛 Troubleshooting

### Method calls not showing in UI
Start the Prefect server:
```bash
prefect server start
```

### Connection issues
Check hardware connections and verify config in `plate_resort/resort_config.yaml`

## 🔄 Migration from v2.x (REST API)

If upgrading from v2.x:

1. REST API replaced with direct method calls
2. No need for API keys or server/client setup
3. Methods are now Prefect flows for better orchestration
4. Legacy code preserved in `archived/` directory

See [CHANGELOG.md](CHANGELOG.md) for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/AccelerationConsortium/plate-RESORT/issues)
- **Prefect Docs**: https://docs.prefect.io/
- **Hardware**: See `mechanical/` directory

---

**Workflow-powered plate management! 🍽️🤖**
