# Plate Resort Control System - Prefect Workflows

**Professional laboratory plate management system with Prefect workflow orchestration.**

## 🎯 Overview

This system provides **Prefect-based workflow orchestration** for controlling the Plate Resort laboratory automation device. All operations are implemented as Prefect flows, enabling robust workflow management with retry logic, observability, and distributed execution.

## 🚀 Quick Setup

### Server Setup (Raspberry Pi)

**One command installs everything:**

```bash
curl -sSL https://raw.githubusercontent.com/AccelerationConsortium/plate-RESORT/copilot/replace-rest-api-with-prefect/plate-resort-multiple/install.sh | bash
```

**What gets installed:**
- ✅ Plate Resort package with Prefect flows
- ✅ Prefect v3.0+ workflow engine
- ✅ All client tools and utilities
- ✅ Configuration templates

### Client Setup (Any Machine)

```bash
# Install client tools
pip install git+https://github.com/AccelerationConsortium/plate-RESORT.git@copilot/replace-rest-api-with-prefect#subdirectory=plate-resort-multiple

# Interactive client
plate-resort-interactive

# Demo workflows
plate-resort-demo
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
# On Pi: Start Prefect server and worker
prefect server start --host 0.0.0.0 --port 4200 &
plate-resort-worker

# From any machine: Submit workflows remotely
plate-resort-interactive --remote
# Or
python -c "from plate_resort.workflows import orchestrator; orchestrator.connect()"
```

### 💻 Client Tools

#### Interactive Client
```bash
# Local mode (flows run directly)
plate-resort-interactive

# Remote mode (flows submitted to Prefect server)
plate-resort-interactive --remote
```

#### Demo Workflows
```bash
# Demonstrate local flows
plate-resort-demo

# Demonstrate remote orchestration
plate-resort-demo --remote
```

#### Available Commands
```
🔌 Connection:        connect, disconnect, status, health
🎯 Movement:          activate <hotel>, home, angle <degrees>, position  
⚙️  Settings:         speed <value>
🚨 Emergency:         stop
```

### 🔧 Workflow Management

#### Deploy Flows to Work Pool
```bash
# Create work pool and deploy all flows
prefect work-pool create --type process plate-resort-pool
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
├── core.py                    # Hardware controller with @flow decorators
├── config/
│   ├── defaults.yaml          # Default configuration
│   └── secrets.ini.template   # Connection settings template
├── client/
│   ├── interactive.py         # Interactive client
│   └── demo.py               # Demo workflows
├── workflows/
│   ├── orchestrator.py       # Remote flow submission
│   ├── worker_service.py     # Persistent worker
│   └── deploy.py            # Flow deployment
└── utils/
    ├── keygen.py             # Key generation
    └── update.py            # Update utilities
```

### Flow Architecture

**Every PlateResort method is a Prefect flow:**
- `@flow` decorators enable workflow orchestration
- Direct method calls run flows locally
- Remote execution via work pools and workers
- Built-in retry logic and error handling

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

### Update System
```bash
plate-resort-update
```

### Generate Configuration
```bash
plate-resort-keygen --generate
```

### Testing
```bash
# Test all workflows
plate-resort-demo

# Test specific flows
python -c "
from plate_resort.core import PlateResort
resort = PlateResort()
resort.get_current_position()  # Runs as Prefect flow
"
```

## 📊 Workflow Features

### Built-in Capabilities
- ✅ **Retry Logic**: Automatic retries on failures
- ✅ **Observability**: Full execution tracking in Prefect UI
- ✅ **Distributed**: Run workflows on remote workers
- ✅ **Persistent Connections**: Efficient hardware usage
- ✅ **Flow Scheduling**: Time-based and event-driven execution
- ✅ **Parameter Validation**: Type-safe workflow inputs

### Available Flows
```python
# All PlateResort methods are Prefect flows:
resort.connect()              # @flow
resort.activate_hotel("A")    # @flow  
resort.move_to_angle(45.0)    # @flow
resort.get_current_position() # @flow
resort.get_motor_health()     # @flow
resort.go_home()              # @flow
resort.disconnect()           # @flow
```

## 🎮 Examples

### Local Workflow Execution
```python
from plate_resort.core import PlateResort

# Each method call runs as a Prefect flow
resort = PlateResort()
resort.connect()
resort.activate_hotel("A")
position = resort.get_current_position()
resort.disconnect()
```

### Remote Workflow Orchestration
```python
from plate_resort.workflows import orchestrator

# Submit flows to remote Prefect work pool
connect_run = orchestrator.connect()
activate_run = orchestrator.activate_hotel("A")
position_run = orchestrator.get_position()
```

### Workflow Composition
```python
from prefect import flow
from plate_resort.core import PlateResort

@flow
def complete_cycle():
    resort = PlateResort()
    resort.connect()
    for hotel in ["A", "B", "C", "D"]:
        resort.activate_hotel(hotel)
        # Process plates...
    resort.go_home()
    resort.disconnect()

# Run the composed workflow
complete_cycle()
```

## 📚 Documentation

- **Prefect Docs**: https://docs.prefect.io/
- **Hardware Setup**: See mechanical/ directory
- **API Reference**: All PlateResort methods are documented flows

---

*Built with Prefect v3 for robust workflow orchestration and laboratory automation.*