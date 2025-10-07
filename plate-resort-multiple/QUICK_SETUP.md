# Plate Resort Server - Quick Setup

A streamlined Plate Resort control system for Raspberry Pi with one-line installation.

## One-Line Installation

On a fresh Raspberry Pi with Raspberry Pi OS, run:

```bash
curl -fsSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/main/install.sh | bash
```

This will:
- Clone the repository to `~/plate-resort`
- Install all required system dependencies
- Set up Python packages (dynamixel-sdk, pyyaml)
- Configure USB permissions for Dynamixel motors
- Create a simple runner script

## Quick Start

After installation and reboot:

```bash
cd ~/plate-resort
./run_server.sh
```

## Core Components

- `plate_resort.py` - Main motor control class
- `resort_config.yaml` - Configuration file
- `test_scripts/` - Motor testing utilities
- `requirements.txt` - Python dependencies (minimal)

## Basic Usage

### Test Motor Connection
```bash
python3 test_scripts/test_dxl_ping.py --device /dev/ttyUSB0 --id 1
```

### Run Core Control System
```bash
python3 plate_resort.py
```

### Check Motor Health
```bash
python3 test_scripts/test_motor_health.py
```

## Configuration

Edit `resort_config.yaml` to configure:
- Motor settings (ID, baudrate, device)
- Hotel positions
- Safety parameters

## Hardware Setup

1. Connect Dynamixel motor to power supply (12V)
2. Connect USB2Dynamixel or equivalent adapter
3. Connect adapter to Raspberry Pi USB port
4. Motor should appear as `/dev/ttyUSB0`

## Troubleshooting

### No USB Device Found
```bash
ls /dev/ttyUSB*
```
If nothing appears, check:
- USB adapter connection
- Power to motor
- USB cable

### Permission Issues
```bash
sudo usermod -aG dialout $USER
# Then reboot
```

### Motor Not Responding
```bash
python3 test_scripts/test_dxl_ping.py --device /dev/ttyUSB0 --baud 57600 --id 1
```

## Archived Components

GUI components have been moved to `archived_gui/` directory:
- Web interface (`web_gui.py`)
- Templates and static files
- Desktop launchers
- Web startup scripts

These can be restored if needed for future GUI development.

## Development

The system is designed to be minimal and extensible. Core functionality is in `plate_resort.py` with test utilities in `test_scripts/`.

## Support

- Check motor connections and power
- Verify USB permissions with `groups` command
- Test individual components with scripts in `test_scripts/`