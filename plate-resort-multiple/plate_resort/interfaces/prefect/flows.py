#!/usr/bin/env python3
"""
Prefect flows for Plate Resort operations.
Each flow instantiates a PlateResort instance and performs the operation.
"""
from prefect import flow, get_run_logger
from plate_resort.core import PlateResort


@flow
def connect(
    device: str = "/dev/ttyUSB0",
    baudrate: int = 57600,
    motor_id: int = 1,
):
    """Connect to the motor"""
    resort = PlateResort()
    resort.connect(device, baudrate, motor_id)


@flow
def disconnect():
    """Disconnect from the motor"""
    resort = PlateResort()
    resort.disconnect()


@flow
def get_motor_health():
    """Get motor health.

    Connection is established if needed and left active (torque enabled)
    after completion. Use disconnect() flow explicitly to release torque.
    """
    logger = get_run_logger()
    resort = PlateResort()
    resort.connect()
    health = resort.get_motor_health()
    logger.info(
        ("motor_health temp=%s current=%s volt=%s pos=%s hwErr=%s " "warnings=%s"),
        health.get("temperature"),
        health.get("current"),
        health.get("voltage"),
        health.get("position"),
        health.get("hardware_error"),
        ",".join(health.get("warnings", [])) or "none",
    )
    return health


@flow
def activate_hotel(
    hotel: str,
    precise: bool = True,
    overrides: dict | None = None,
):
    """Activate a hotel (precise two-stage by default).

    Args:
        hotel: Hotel identifier (e.g. "A").
        precise: When True (default), uses two-stage coarse+PWM refinement
            via `activate_hotel_precise`; when False, uses legacy blind
            `activate_hotel` (immediate goal position write, no verification).
        overrides: Optional dict of precise movement parameter overrides
            passed to `activate_hotel_precise` (e.g.,
            {"switch_error": 5.0, "pulse_pwm_start": 150}). If omitted or
            null, defaults are used.

    Returns:
        dict | None: Precise result dict when precise=True, else None.

    Notes:
        - Replaces earlier variadic ``**overrides`` parameter which caused a
          Prefect parameter schema validation error ("'overrides' is a
          required property"). Using an explicit optional dict keeps the
          parameter optional and avoids schema enforcement issues.
        - To override parameters remotely now call the deployment with, e.g.:
            overrides={"pulse_pwm_start": 140, "pwm_step": 20}

    Leaves connection/torque enabled for motor locking after move so that
    subsequent flow invocations operate on an already-engaged motor.
    """
    logger = get_run_logger()
    resort = PlateResort()
    resort.connect()
    if precise:
        result = resort.activate_hotel_precise(hotel, **(overrides or {}))
        logger.info(
            (
                "activate_hotel precise hotel=%s success=%s reason=%s "
                "pulses=%s final_angle=%s final_error=%s overrides=%s"
            ),
            hotel,
            result.get("success"),
            result.get("reason"),
            result.get("pulses"),
            result.get("final_angle"),
            result.get("final_error"),
            (overrides or {}),
        )
        return result
    resort.activate_hotel(hotel)
    logger.info("activate_hotel blind hotel=%s", hotel)
    return None


@flow
def go_home():
    """Go to home position and keep connection active."""
    resort = PlateResort()
    resort.connect()
    resort.go_home()


@flow
def move_to_angle(angle: float):
    """Move to specific angle; connection left active."""
    logger = get_run_logger()
    resort = PlateResort()
    resort.connect()
    ok = resort.move_to_angle(angle)
    logger.info("move_to_angle angle=%s success=%s", angle, ok)


@flow
def set_speed(speed: int):
    """Set movement speed; keep connection active."""
    logger = get_run_logger()
    resort = PlateResort()
    resort.connect()
    resort.set_speed(speed)
    logger.info("set_speed speed=%s", speed)


@flow
def emergency_stop():
    """Emergency stop.

    Leaves torque disabled (stop) but keeps port connection active.
    """
    logger = get_run_logger()
    resort = PlateResort()
    resort.connect()
    resort.emergency_stop()
    logger.warning("emergency_stop executed")


@flow
def get_current_position():
    """Get current position; keep connection active."""
    logger = get_run_logger()
    resort = PlateResort()
    resort.connect()
    position = resort.get_current_position()
    logger.info("get_current_position position=%s", position)
    return position


@flow
def reboot(wait: float = 0.8, reapply: bool = True):
    """Soft reboot the Dynamixel and reapply settings.

    Args:
        wait: Seconds to wait after reboot before reapplying settings.
        reapply: When True, reapply operating mode, limits, speed, accel.

    Returns:
        dict: Result from `PlateResort.reboot` plus a post-health snapshot.
    """
    logger = get_run_logger()
    resort = PlateResort()
    resort.connect()
    result = resort.reboot(wait=wait, reapply=reapply)
    try:
        health = resort.get_motor_health()
    except Exception as e:  # noqa: BLE001
        health = {"error": str(e)}
    result["health"] = health
    logger.info(
        "reboot wait=%s reapply=%s healthTemp=%s hwErr=%s warnings=%s",
        wait,
        reapply,
        health.get("temperature"),
        health.get("hardware_error"),
        ",".join(health.get("warnings", [])) or "none",
    )
    return result


@flow
def get_motor_info():
    """Get motor model and capabilities information."""
    logger = get_run_logger()
    resort = PlateResort()
    resort.connect()
    try:
        motor_info = resort.get_motor_info()
        logger.info(
            "Motor info: model=%s current_control=%s max_current=%s",
            motor_info.get("model"),
            motor_info.get("supports_current_control"),
            motor_info.get("max_current_ma"),
        )
        return motor_info
    finally:
        # Keep connection active for consistency with other flows
        pass
