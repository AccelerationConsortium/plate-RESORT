# Plate Resort Control System - Prefect Workflows

**Laboratory plate management orchestrated via Prefect stateless function flows (no REST, no keygen).**

## 🎯 Overview

This system provides **Prefect-based workflow orchestration** for controlling the Plate Resort laboratory automation device. All operations are implemented as Prefect flows, enabling robust workflow management with retry logic, observability, and distributed execution.

## 🚀 Quick Setup

### Server Setup (Raspberry Pi)

Export Prefect Cloud credentials first (required for auto-deploy & worker start):

```bash
export PREFECT_API_URL="https://api.prefect.cloud/api/accounts/<account-id>/workspaces/<workspace-id>"
export PREFECT_API_KEY="pnu_XXXXXXXXXXXX"
```

Then install (auto deploy if env vars set):
```bash
curl -sSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/copilot/replace-rest-api-with-prefect/plate-resort-multiple/install.sh | bash
```

Automatic (with env vars): create venv, install, ensure work pool, deploy flows, start worker (nohup), add auto-activation.

### Client Setup (Any Machine)

```bash
# Install client tools
pip install git+https://github.com/AccelerationConsortium/plate-RESORT.git@copilot/replace-rest-api-with-prefect#subdirectory=plate-resort-multiple

# Interactive client
plate-resort-interactive

```

## 🎯 Usage

### 📊 Workflow Execution Modes

#### 1. Local Flow Execution
```bash
# Run flows directly (no server needed)
plate-resort-interactive
# Or
python -c "from plate_resort.core import PlateResort; resort = PlateResort(); resort.connect()"
```

#### 2. Remote Workflow Orchestration  
```bash
plate-resort-interactive --remote
python -c "from plate_resort.workflows import orchestrator; orchestrator.connect(device='/dev/ttyUSB0', baudrate=57600, motor_id=1)"
```

### 💻 Client Tools

#### Interactive Client
```bash
# Local mode (flows run directly)
plate-resort-interactive

# Remote mode (flows submitted to Prefect server)
plate-resort-interactive --remote
```


#### Available Commands
```
🔌 Connection:        connect, disconnect, status, health
🎯 Movement:          activate <hotel>, home, angle <degrees>, position  
⚙️  Settings:         speed <value>
🚨 Emergency:         stop
```

### 🔧 Workflow Management

#### Re-deploy Flows Manually
```bash
plate-resort-deploy
```

#### Start Worker Service
```bash
# Start persistent worker with hardware connection
plate-resort-worker
```

#### Monitor Workflows
```bash
# Access Prefect UI
# http://YOUR_PI_IP:4200
```

## 🏗️ Architecture

### Core Components

```
plate_resort/
├── core.py                 # Hardware controller class (not decorated with @flow)
├── client/
│   └── interactive.py         # Interactive client
├── workflows/
│   ├── orchestrator.py       # Remote flow submission
│   ├── worker_service.py     # Persistent worker
│   └── deploy.py            # Flow deployment
└── utils/
  └── __init__.py          # Utilities package placeholder
```

### Flow Architecture

Flows are pure functions in `workflows/flows.py`:
1. Instantiate `PlateResort`
2. Connect
3. Perform single action
4. Disconnect

No state retained between flow runs; avoids method signature mismatch.

## 🔐 Configuration

### Configuration Files

**Config Location**: `~/plate-resort-config/`

**defaults.yaml** - Hardware and Prefect settings
```yaml
resort:
  device: "/dev/ttyUSB0"
  hotels: ["A", "B", "C", "D"]
  # ... hardware settings

prefect:
  server_host: "0.0.0.0"
  server_port: 4200
  # Default work pool name; can be overridden at runtime by setting
  # the PLATE_RESORT_POOL environment variable.
  work_pool_name: "plate-resort-pool"
```

**secrets.ini** - Connection settings
```ini
[prefect]
server_api_url = http://YOUR_PI_IP:4200/api

[hardware]  
device = /dev/ttyUSB0
baudrate = 57600

[client]
default_host = YOUR_PI_IP
default_port = 4200
```

## 🔄 Development

### Update
Reinstall from source for latest version:
```bash
pip install --upgrade git+https://github.com/AccelerationConsortium/plate-RESORT.git@main#subdirectory=plate-resort-multiple
```

### Configuration
Environment variables (PREFECT_API_URL, PREFECT_API_KEY) replace any legacy key/REST configuration. No keygen required.

### Testing
```bash
python -c "from plate_resort.core import PlateResort; r=PlateResort(); r.connect(); print(r.get_current_position()); r.disconnect()" || echo "(Expected to fail without hardware)"
```

## 📊 Workflow Features

### Built-in Capabilities
- ✅ **Retry Logic**: Automatic retries on failures
- ✅ **Observability**: Full execution tracking in Prefect UI
- ✅ **Distributed**: Run workflows on remote workers
- ✅ **Persistent Connections**: Efficient hardware usage
- ✅ **Flow Scheduling**: Time-based and event-driven execution
- ✅ **Parameter Validation**: Type-safe workflow inputs

### Available Flows (function-based)
```python
from plate_resort.workflows.flows import (
  connect,
  disconnect,
  activate_hotel,
  move_to_angle,
  get_current_position,
  get_motor_health,
  go_home,
  emergency_stop,
  set_speed,
)
```

## 🎮 Examples

### Local Execution
```python
from plate_resort.workflows.flows import connect, activate_hotel, disconnect

connect(device="/dev/ttyUSB0", baudrate=57600, motor_id=1)
activate_hotel("A")
disconnect()
```

### Remote Workflow Orchestration
```python
from plate_resort.workflows import orchestrator

connect_run = orchestrator.connect(device="/dev/ttyUSB0", baudrate=57600, motor_id=1)
activate_run = orchestrator.activate_hotel("A")
position_run = orchestrator.get_position()
```

### Legacy Notes
REST/FastAPI + keygen removed. Keep stateless function flows only.
```

## 📚 Documentation

- **Prefect Docs**: https://docs.prefect.io/
- **Hardware Setup**: See mechanical/ directory
- **API Reference**: All PlateResort methods are documented flows

---

*Built with Prefect v3 for robust workflow orchestration and laboratory automation.*