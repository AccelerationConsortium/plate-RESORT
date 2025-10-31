"""
Orchestrator for executing Plate Resort flows remotely.
This runs on a remote machine (e.g., laptop) and submits jobs to the
Prefect work pool.

Deployment names follow the format: flow-name/deployment-name
where flow-name is the Prefect flow name (from @flow decorator) and
deployment-name is specified in deploy.py
"""

from prefect.deployments import run_deployment
import asyncio
import time
from prefect.client.orchestration import get_client


def wait(flow_run, poll: float = 2.0, timeout: float = 600.0):
    """Block until the given flow run reaches a final state.

    Parameters
    ----------
    flow_run: FlowRun or object with `id` attribute
        The run returned by `run_deployment`.
    poll: float
        Seconds between state checks.
    timeout: float
        Maximum seconds to wait before raising TimeoutError.

    Returns
    -------
    prefect.states.State
        Final state object.
    """
    run_id = getattr(flow_run, "id", flow_run)
    start = time.time()
    
    async def _fetch(rid: str):
        async with get_client() as client:
            fr = await client.read_flow_run(rid)
            return fr.state
    while True:
        state = asyncio.run(_fetch(run_id))
        if state.is_final():
            return state
        if time.time() - start > timeout:
            raise TimeoutError(f"Flow run {run_id} timed out after {timeout}s")
        time.sleep(poll)


def connect(
    device: str = "/dev/ttyUSB0",
    baudrate: int = 57600,
    motor_id: int = 1,
):
    """Connect to the motor using function-based flow deployment."""
    return run_deployment(
        name="connect/connect",
        parameters={
            "device": device,
            "baudrate": baudrate,
            "motor_id": motor_id,
        },
    )


def disconnect():
    """Disconnect from the motor"""
    return run_deployment(name="disconnect/disconnect")


def get_health():
    """Get motor health"""
    return run_deployment(name="get-motor-health/health")


def activate_hotel(hotel: str, precise: bool = True, **overrides):
    """Activate a hotel using precise two-stage move by default.

    Parameters
    ----------
    hotel : str
        Hotel identifier.
    precise : bool, default True
        When True, remote flow performs coarse+PWM refinement and returns
        a result dict. When False, legacy blind activation is used.
    **overrides : dict
        Optional precise parameter overrides forwarded to the flow
        (e.g., switch_error=5.0, pulse_pwm_start=150).
    """
    params = {"hotel": hotel, "precise": precise}
    params.update(overrides)
    return run_deployment(
        name="activate-hotel/activate-hotel",
        parameters=params,
    )


def go_home():
    """Go to home position"""
    return run_deployment(name="go-home/go-home")


def move_to_angle(angle: float):
    """Move to specific angle"""
    return run_deployment(
        name="move-to-angle/move-to-angle",
        parameters={"angle": angle},
    )


def set_speed(speed: int):
    """Set motor speed"""
    return run_deployment(
        name="set-speed/set-speed",
        parameters={"speed": speed},
    )


def emergency_stop():
    """Emergency stop"""
    return run_deployment(name="emergency-stop/emergency-stop")


def get_position():
    """Get current position"""
    return run_deployment(name="get-position/get-position")


def reboot(wait: float = 0.8, reapply: bool = True):
    """Soft reboot the motor via deployed flow."""
    return run_deployment(
        name="reboot/reboot",
        parameters={"wait": wait, "reapply": reapply},
    )
