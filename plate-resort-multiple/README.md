# Plate Resort Control System

A complete plate storage automation system with network control and touchscreen interface for laboratory well plate management.

## Features

- **🔄 Automated Plate Rotation**: Precise motor control for hotel-based storage
- **🌐 Network Control**: Web-based interface accessible from any device
- **🖥️ Touchscreen GUI**: Local 7" touchscreen interface optimized for lab use
- **📊 Health Monitoring**: Real-time motor health and diagnostics
- **⚙️ YAML Configuration**: Easy setup and customization
- **🐳 Docker Support**: Consistent deployment across environments
- **🔒 Safety Features**: Emergency stop and error handling

## Quick Start

### 1. Pull Latest Changes
```bash
git pull origin main
```

### 2. Docker Deployment (Recommended)
```bash
# Start web service only
docker-compose up --build

# Access web interface at: http://your-pi-ip:5000
```

### 3. Touchscreen Mode
```bash
# Build container
docker-compose build

# Run with GUI (requires X11 forwarding)
docker-compose run --rm plate-resort-app python touchscreen_app.py
```

### 4. Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Web service only
python app.py

# Touchscreen GUI
python touchscreen_app.py

# Manual control
python dxl_keyboard_test.py
```

## Usage

### Web Interface

Access the web interface at `http://your-pi-ip:5000` for:
- Remote hotel activation
- Real-time status monitoring
- Motor health diagnostics
- Speed control
- Emergency stop

### Touchscreen Interface

Perfect for barcode scanning and plate loading operations:
- Large, touch-friendly buttons
- Hotel selection grid
- Real-time status display
- Emergency stop accessible
- Speed adjustment

### API Endpoints

- `GET /api/status` - System status
- `POST /api/connect` - Connect to motor
- `POST /api/disconnect` - Disconnect motor
- `POST /api/hotel/<hotel>/activate` - Activate hotel
- `GET /api/health` - Motor health data
- `POST /api/emergency_stop` - Emergency stop
- `POST /api/speed` - Set motor speed

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
4. **Touchscreen**: 7" Raspberry Pi touchscreen (optional)

## Troubleshooting

### Connection Issues
- Check USB device: `ls /dev/ttyUSB*`
- Verify permissions: `sudo chmod 666 /dev/ttyUSB0`
- Test ping: `python test_scripts/test_dxl_ping.py`

### Motor Issues
- Check power supply (12V)
- Verify motor ID (default: 1)
- Run health check: `python test_scripts/test_motor_health.py`

### Docker Issues
- Ensure device access: `--device /dev/ttyUSB0:/dev/ttyUSB0`
- Check permissions: `--privileged`
- For GUI: Enable X11 forwarding

## Development

### File Structure
```
├── app.py                 # Main Flask application
├── gui.py                 # Touchscreen GUI
├── touchscreen_app.py     # Combined launcher
├── plate_resort.py        # Core motor control
├── resort_config.yaml     # Configuration
├── templates/
│   └── index.html         # Web interface
├── test_scripts/          # Test utilities
└── docker-compose.yml     # Container setup
```

### Adding Features
1. Update `plate_resort.py` for new motor functions
2. Add API endpoints in `app.py`
3. Update GUI in `gui.py` 
4. Modify web interface in `templates/index.html`
5. Test with provided test scripts

## License

MIT License - See LICENSE file for details.