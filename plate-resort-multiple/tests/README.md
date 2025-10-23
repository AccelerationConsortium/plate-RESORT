# Test Scripts

Essential testing scripts for the Plate Resort system hardware and motor diagnostics.

## Prerequisites

Install the plate-resort package:
```bash
pip install -e .  # From the root directory
```

## Available Tests

### Hardware Tests
- **`test_dxl_ping.py`** - Test basic Dynamixel communication
- **`test_motor_health.py`** - Check motor health and diagnostics
- **`test_plate_resort.py`** - Complete system functionality test

### Interactive Tests  
- **`test_dxl_keyboard.py`** - Manual motor control with keyboard

## Usage

Run any test directly:
```bash
python test_scripts/test_dxl_ping.py
python test_scripts/test_motor_health.py
```

For interactive client testing, use the main client tools:
```bash
python interactive_client.py    # Interactive CLI
python demo_client.py          # Automated demo
```

### 🔧 `test_plate_resort.py`
Tests the main PlateResort functionality:
- Motor connection
- Hotel positions and movement
- Configuration loading

```bash
cd test_scripts
python test_plate_resort.py
```

### 🏥 `test_motor_health.py`
Monitors motor health during operations:
- Temperature, current, position tracking
- Health checks before/after movements
- Warning detection

```bash
cd test_scripts
python test_motor_health.py
```

### 🔍 `test_dxl_ping.py`
Low-level Dynamixel motor diagnostics:
- Motor connectivity testing
- Hardware error status checking
- Direct motor communication

```bash
cd test_scripts
python test_dxl_ping.py --device /dev/ttyUSB0 --id 1
```

### ⌨️ `test_dxl_keyboard.py`
Interactive motor control:
- Manual motor positioning
- Real-time position feedback
- Keyboard-based motor control

```bash
cd test_scripts
python test_dxl_keyboard.py
```

## Configuration

Most scripts use the default configuration included in the package. To use a custom configuration, place `resort_config.yaml` in the current directory.

## Troubleshooting

- **Import errors**: Make sure the package is installed (`pip install -e .`)
- **USB permission errors**: On Linux, add user to `dialout` group
- **Motor not found**: Check USB connection and device path
- **Configuration errors**: Verify YAML syntax and motor settings