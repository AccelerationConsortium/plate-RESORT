# Plate Resort - Prefect Workflow Orchestration

This system uses **Prefect v3** for workflow orchestration. The `PlateResort` class methods are decorated with `@flow`, making them Prefect workflows.

## Setup

### 1. Install Dependencies

```bash
cd /home/runner/work/plate-RESORT/plate-RESORT/plate-resort-multiple
pip install prefect dynamixel-sdk pyyaml
```

### 2. Start Prefect Server (Optional - for UI/monitoring)

In a terminal, start the Prefect server:

```bash
prefect server start
```

The server will be available at http://127.0.0.1:4200

## Usage

### Direct Method Calls (Simplest)

The PlateResort class methods are Prefect flows, so you can use them directly:

```python
from plate_resort.core import PlateResort

# Create instance
resort = PlateResort()

# All methods are Prefect flows - use them normally
resort.connect()
resort.activate_hotel("A")
position = resort.get_current_position()
resort.go_home()
resort.disconnect()
```

### With Prefect UI Monitoring

If you want to monitor flows in the Prefect UI, just make sure the Prefect server is running and call methods normally. Prefect will automatically track them.

### Creating Deployments (Advanced)

For scheduled or remote execution, you can create deployments:

```python
from plate_resort.core import PlateResort

resort = PlateResort()

# Deploy a specific method as a flow
resort.activate_hotel.deploy(
    name="activate-hotel-a",
    work_pool_name="plate-resort-pool",
    parameters={"hotel": "A"}
)
```

Then run the deployment:

```python
from prefect.deployments import run_deployment

run_deployment(name="activate-hotel/activate-hotel-a")
```

## Available Flow Methods

All public methods in the `PlateResort` class are Prefect flows:

- `connect()` - Connect to Dynamixel motor
- `disconnect()` - Disconnect from motor
- `activate_hotel(hotel)` - Move to specified hotel (A, B, C, D)
- `go_home()` - Return to home position
- `move_to_angle(angle)` - Move to specific angle in degrees
- `get_current_position()` - Get current motor position
- `get_motor_health()` - Get motor health diagnostics
- `set_speed(speed)` - Set motor movement speed
- `emergency_stop()` - Emergency stop motor

## Architecture

- **plate_resort/core.py**: Core PlateResort class with `@flow` decorated methods
- **orchestrator.py**: Example script showing how to chain multiple operations
- **example_usage.py**: Simple usage example

## Benefits of Prefect

- **Automatic tracking**: All method calls are tracked in Prefect UI (if server is running)
- **Workflow orchestration**: Chain multiple operations together
- **Retry logic**: Built-in retry capabilities on failures
- **Monitoring**: Track execution history in the Prefect UI
- **Deployments**: Schedule or trigger flows remotely
- **State management**: Track the state of each flow run

## Monitoring

If you started the Prefect server, view flow runs at http://127.0.0.1:4200

Every time you call a decorated method (like `resort.activate_hotel("A")`), Prefect logs it and you can see the execution in the UI.
