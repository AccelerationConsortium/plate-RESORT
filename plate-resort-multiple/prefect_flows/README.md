# Plate Resort Prefect Integration

This directory contains Prefect v3 flows for controlling the Plate Resort device.

## Overview

The Prefect implementation uses flow decorators directly on the PlateResort class methods:

- **PlateResort class methods** (in `plate_resort/core.py`): Decorated with @flow for direct Prefect orchestration
- **orchestrator.py**: Functions for submitting flow runs from a remote machine
- **deploy_flows.py**: Helper script to deploy all flows to a work pool using `flow.from_source()` (no hardware initialization required)
- **worker_service.py**: Custom worker that maintains a persistent PlateResort instance for efficient hardware usage

## Architecture Options

### Option 1: Standard Worker (Reconnect per Flow)
Each flow run creates a new PlateResort instance and reconnects to hardware. Simple but has connection overhead.

### Option 2: Custom Worker with Persistent Connection (Recommended)
Uses `worker_service.py` to maintain a single PlateResort instance across all flow runs, avoiding reconnection overhead while keeping work pool architecture.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install prefect
```

Or update the existing installation:

```bash
cd plate-resort-multiple
pip install -e .
```

### 2. Start Prefect Server (Optional)

For local development, you can use Prefect Cloud or run a local server:

```bash
# For local server (development only)
prefect server start
```

For production, consider using [Prefect Cloud](https://www.prefect.io/cloud) (free tier available).

### 3. Create Work Pool

Create a work pool for the Plate Resort device:

```bash
prefect work-pool create plate-resort-pool --type process
```

Verify it was created:

```bash
prefect work-pool ls
```

### 4. Deploy Flows

From the `prefect_flows` directory, deploy the flows using the helper script:

```bash
cd prefect_flows
python deploy_flows.py
```

This script uses `flow.from_source()` to deploy flows without initializing the hardware, making it safe to run from any machine.

### 5. Start Worker on Device

#### Option A: Standard Worker (Simple)
```bash
prefect worker start --pool plate-resort-pool
```
Each flow run will create a new PlateResort instance and connect/disconnect.

#### Option B: Custom Worker (Recommended for persistent connection)
```bash
cd prefect_flows
python worker_service.py
```
This maintains a persistent PlateResort instance across all flow runs, avoiding reconnection overhead.

The custom worker provides:
- Deploy-like permissions (work pool architecture)
- Serve-like persistence (single hardware connection)
- Automatic connection management in setup/teardown

For production, run as a systemd service:
```bash
# Create service file at /etc/systemd/system/plate-resort-worker.service
[Unit]
Description=Plate Resort Prefect Worker
After=network.target

[Service]
Type=simple
User=prefect
WorkingDirectory=/path/to/plate-resort-multiple/plate_resort
ExecStart=/usr/bin/python3 /path/to/plate-resort-multiple/prefect_flows/worker_service.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 6. Submit Flow Runs

From any machine with Prefect configured (pointing to the same server/cloud):

```python
from orchestrator import connect, activate_hotel, get_health

# Connect to motor
result = connect(device="/dev/ttyUSB0", baudrate=57600, motor_id=1)

# Activate hotel A
result = activate_hotel("A")

# Get health
health = get_health()
```

Or use the Prefect CLI:

```bash
prefect deployment run connect/plate-resort-connect --param device=/dev/ttyUSB0
```

## Architecture

```
Remote Machine                    Raspberry Pi (Device)
┌─────────────────┐              ┌──────────────────────┐
│  orchestrator.py│              │  PlateResort class   │
│  (submit jobs)  │              │  (@flow decorated)   │
└────────┬────────┘              └─────────┬────────────┘
         │                                  │
         │                                  │
         └──────┐    Prefect    ┌──────────┘
                │ Server/Cloud  │
                └───────┬───────┘
                        │
                  Work Pool Queue
```

## Benefits over REST API

- **Automatic Retry**: Flows can retry on failure
- **State Management**: Built-in tracking of flow runs and their states
- **Scheduling**: Can schedule recurring operations
- **Observability**: Built-in UI for monitoring flow runs
- **Async Execution**: Non-blocking job submission
- **Security**: No need to expose HTTP endpoints on device

## Manual Steps Required

1. Set up a work pool using the Prefect UI or CLI
2. Deploy flows from device.py
3. Start worker on the device
4. Configure Prefect API connection on both device and remote machine

## Troubleshooting

If flows fail to execute:

1. Check worker is running: `prefect worker ls`
2. Check work pool exists: `prefect work-pool ls`
3. Check deployments exist: `prefect deployment ls`
4. View logs: `prefect deployment logs <deployment-name>`

For more information, see [Prefect Documentation](https://docs.prefect.io/).
