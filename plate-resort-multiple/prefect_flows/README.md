# Plate Resort Prefect Integration

This directory contains Prefect v3 flows for controlling the Plate Resort device.

## Overview

The Prefect implementation replaces the REST API with a more robust workflow orchestration system:

- **device.py**: Contains Prefect flows that run on the device (Raspberry Pi) with physical motor access
- **orchestrator.py**: Functions for submitting flow runs from a remote machine

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

Or specify a custom work pool name:

```bash
python deploy_flows.py my-custom-pool
```

Alternatively, deploy manually:

```bash
python -c "
from device import *

connect_flow.deploy(name='plate-resort-connect', work_pool_name='plate-resort-pool')
disconnect_flow.deploy(name='plate-resort-disconnect', work_pool_name='plate-resort-pool')
status_flow.deploy(name='plate-resort-status', work_pool_name='plate-resort-pool')
health_flow.deploy(name='plate-resort-health', work_pool_name='plate-resort-pool')
activate_hotel_flow.deploy(name='plate-resort-activate-hotel', work_pool_name='plate-resort-pool')
go_home_flow.deploy(name='plate-resort-go-home', work_pool_name='plate-resort-pool')
move_to_angle_flow.deploy(name='plate-resort-move-to-angle', work_pool_name='plate-resort-pool')
set_speed_flow.deploy(name='plate-resort-set-speed', work_pool_name='plate-resort-pool')
emergency_stop_flow.deploy(name='plate-resort-emergency-stop', work_pool_name='plate-resort-pool')
get_hotels_flow.deploy(name='plate-resort-get-hotels', work_pool_name='plate-resort-pool')
get_position_flow.deploy(name='plate-resort-get-position', work_pool_name='plate-resort-pool')
"
```

### 5. Start Worker on Device

On the Raspberry Pi (or device with motor access), start a worker:

```bash
# Run in foreground for testing
prefect worker start --pool plate-resort-pool

# Or run in background (production)
nohup prefect worker start --pool plate-resort-pool > worker.log 2>&1 &
```

The worker will continuously poll the work pool for new flow runs to execute.

### 6. Submit Flow Runs

From any machine with Prefect configured (pointing to the same server/cloud):

```python
from orchestrator import connect, activate_hotel, get_status

# Connect to motor
result = connect(device="/dev/ttyUSB0", baudrate=57600, motor_id=1)

# Activate hotel A
result = activate_hotel("A")

# Get status
status = get_status()
```

Or use the Prefect CLI:

```bash
prefect deployment run connect/plate-resort-connect --param device=/dev/ttyUSB0
```

## Architecture

```
Remote Machine                    Raspberry Pi (Device)
┌─────────────────┐              ┌──────────────────────┐
│  orchestrator.py│              │     device.py        │
│  (submit jobs)  │              │  (Prefect flows)     │
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
