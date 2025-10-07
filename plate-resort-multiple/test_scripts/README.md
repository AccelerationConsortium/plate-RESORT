# Test Scripts

These scripts test various aspects of the Plate Resort system and are compatible with both the installed package and development setups.

## Prerequisites

For the scripts to work, you need either:

1. **Installed package** (recommended):
   ```bash
   pip install -e .  # From the root directory
   ```

2. **Development setup** with dependencies:
   ```bash
   pip install dynamixel-sdk pyyaml
   ```

## Available Tests

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