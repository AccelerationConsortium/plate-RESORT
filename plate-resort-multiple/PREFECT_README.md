# Plate Resort - Prefect Workflow Orchestration

This system uses **Prefect v3** for workflow orchestration to control the Plate Resort motor system.

## Setup

### 1. Install Dependencies

```bash
cd /home/runner/work/plate-RESORT/plate-RESORT/plate-resort-multiple
pip install prefect dynamixel-sdk pyyaml
```

### 2. Start Prefect Server (if not using Prefect Cloud)

In a terminal, start the Prefect server:

```bash
prefect server start
```

The server will be available at http://127.0.0.1:4200

### 3. Create Work Pool

You can create a work pool via the UI or CLI:

**Option A: Via UI**
1. Open http://127.0.0.1:4200
2. Navigate to Work Pools
3. Click "Create Work Pool"
4. Name it `plate-resort-pool`
5. Type: `process`

**Option B: Via CLI**
```bash
prefect work-pool create plate-resort-pool --type process
```

### 4. Deploy Flows

Deploy all flows to the work pool:

```bash
cd /home/runner/work/plate-RESORT/plate-RESORT/plate-resort-multiple
python -c "
from device import *
from prefect import flow

# Deploy each flow
connect.from_source(
    source='.',
    entrypoint='device.py:connect'
).deploy(name='connect', work_pool_name='plate-resort-pool')

disconnect.from_source(
    source='.',
    entrypoint='device.py:disconnect'
).deploy(name='disconnect', work_pool_name='plate-resort-pool')

status.from_source(
    source='.',
    entrypoint='device.py:status'
).deploy(name='status', work_pool_name='plate-resort-pool')

health.from_source(
    source='.',
    entrypoint='device.py:health'
).deploy(name='health', work_pool_name='plate-resort-pool')

activate_hotel.from_source(
    source='.',
    entrypoint='device.py:activate_hotel'
).deploy(name='activate-hotel', work_pool_name='plate-resort-pool')

go_home.from_source(
    source='.',
    entrypoint='device.py:go_home'
).deploy(name='go-home', work_pool_name='plate-resort-pool')

move_to_angle.from_source(
    source='.',
    entrypoint='device.py:move_to_angle'
).deploy(name='move-to-angle', work_pool_name='plate-resort-pool')

get_position.from_source(
    source='.',
    entrypoint='device.py:get_position'
).deploy(name='get-position', work_pool_name='plate-resort-pool')

set_speed.from_source(
    source='.',
    entrypoint='device.py:set_speed'
).deploy(name='set-speed', work_pool_name='plate-resort-pool')

emergency_stop.from_source(
    source='.',
    entrypoint='device.py:emergency_stop'
).deploy(name='emergency-stop', work_pool_name='plate-resort-pool')

get_hotels.from_source(
    source='.',
    entrypoint='device.py:get_hotels'
).deploy(name='get-hotels', work_pool_name='plate-resort-pool')
"
```

### 5. Start Worker

In a separate terminal, start the worker:

```bash
prefect worker start --pool plate-resort-pool --type process
```

The worker should be left running to execute flow runs.

## Usage

### Running Flows Directly (Local)

You can run flows directly without deployments:

```python
from device import connect, status, activate_hotel, get_position, go_home

# Connect to motor
connect(device="/dev/ttyUSB0", baudrate=57600, motor_id=1)

# Get status
current_status = status()
print(current_status)

# Move to hotel A
activate_hotel("A")

# Get position
position = get_position()
print(position)

# Go home
go_home()
```

### Running Flows via Deployments (Remote/Scheduled)

After deploying flows and starting a worker:

```python
from prefect.deployments import run_deployment

# Connect to motor
run_deployment(
    name="connect/connect",
    parameters={"device": "/dev/ttyUSB0", "baudrate": 57600, "motor_id": 1}
)

# Get status
run_deployment(name="status/status")

# Move to hotel B
run_deployment(name="activate-hotel/activate-hotel", parameters={"hotel": "B"})

# Get position
run_deployment(name="get-position/get-position")
```

### Via Orchestrator Script

Use the provided orchestrator script:

```bash
python orchestrator.py
```

## Available Flows

- `connect` - Connect to Dynamixel motor
- `disconnect` - Disconnect from motor
- `status` - Get system status
- `health` - Get motor health diagnostics
- `activate_hotel` - Move to specified hotel (A, B, C, D)
- `go_home` - Return to home position
- `move_to_angle` - Move to specific angle in degrees
- `get_position` - Get current motor position
- `set_speed` - Set motor movement speed
- `emergency_stop` - Emergency stop motor
- `get_hotels` - Get available hotels and their angles

## Architecture

- **device.py**: Contains all Prefect flows for motor operations
- **orchestrator.py**: Example script for running multiple deployments in sequence
- **plate_resort/core.py**: Core motor control logic (unchanged)

## Benefits of Prefect

- **Workflow orchestration**: Chain multiple operations together
- **Scheduling**: Schedule flows to run at specific times
- **Monitoring**: Track flow execution in the Prefect UI
- **Retry logic**: Automatic retries on failures
- **Distributed execution**: Run flows on different machines via workers
- **State management**: Track the state of each flow run

## Monitoring

View flow runs in the Prefect UI at http://127.0.0.1:4200
