#!/usr/bin/env python3
"""
Helper script to deploy all Plate Resort flows to a work pool.
Run this script after creating the work pool to deploy all flows.
"""
from plate_resort.workflows import flows

FUNCTION_FLOWS = [
    (flows.connect, "connect"),
    (flows.disconnect, "disconnect"),
    (flows.get_motor_health, "health"),
    (flows.activate_hotel, "activate-hotel"),
    (flows.go_home, "go-home"),
    (flows.move_to_angle, "move-to-angle"),
    (flows.set_speed, "set-speed"),
    (flows.emergency_stop, "emergency-stop"),
    (flows.get_current_position, "get-position"),
]


def main():
    """Deploy function-based flows (no class method flows)."""
    work_pool_name = "plate-resort-pool"
    print(
        f"Deploying {len(FUNCTION_FLOWS)} flows to work pool: {work_pool_name}"
    )
    print("-" * 60)
    for flow_obj, deployment_name in FUNCTION_FLOWS:
        # flow_obj is a Prefect Flow; underlying function is flow_obj.fn
        print(
            f"Deploying '{deployment_name}' (flow: {flow_obj.fn.__name__})"
        )
        flow_obj.deploy(
            name=deployment_name,
            work_pool_name=work_pool_name,
        )
        print(f"\u2713 Deployed: {deployment_name}")
    print("-" * 60)
    print(f"Successfully deployed all flows to '{work_pool_name}'")
    print("\nNext steps:")
    print(f"1. Start worker: prefect worker start --pool {work_pool_name}")
    print("2. Submit jobs using orchestrator.py or Prefect CLI")


if __name__ == "__main__":
    main()
