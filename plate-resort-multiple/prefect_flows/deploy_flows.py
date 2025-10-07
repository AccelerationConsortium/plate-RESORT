#!/usr/bin/env python3
"""
Helper script to deploy all Plate Resort flows to a work pool.
Run this script after creating the work pool to deploy all flows.
"""
import sys
from device import (
    connect_flow,
    disconnect_flow,
    status_flow,
    health_flow,
    activate_hotel_flow,
    go_home_flow,
    move_to_angle_flow,
    set_speed_flow,
    emergency_stop_flow,
    get_hotels_flow,
    get_position_flow,
)


def deploy_all(work_pool_name: str = "plate-resort-pool"):
    """Deploy all flows to the specified work pool"""
    flows = [
        (connect_flow, "plate-resort-connect"),
        (disconnect_flow, "plate-resort-disconnect"),
        (status_flow, "plate-resort-status"),
        (health_flow, "plate-resort-health"),
        (activate_hotel_flow, "plate-resort-activate-hotel"),
        (go_home_flow, "plate-resort-go-home"),
        (move_to_angle_flow, "plate-resort-move-to-angle"),
        (set_speed_flow, "plate-resort-set-speed"),
        (emergency_stop_flow, "plate-resort-emergency-stop"),
        (get_hotels_flow, "plate-resort-get-hotels"),
        (get_position_flow, "plate-resort-get-position"),
    ]

    print(f"Deploying {len(flows)} flows to work pool: {work_pool_name}")
    print("-" * 60)

    for flow, deployment_name in flows:
        try:
            flow.deploy(
                name=deployment_name,
                work_pool_name=work_pool_name,
            )
            print(f"✓ Deployed: {deployment_name}")
        except Exception as e:
            print(f"✗ Failed to deploy {deployment_name}: {e}")
            return False

    print("-" * 60)
    print(f"Successfully deployed all flows to '{work_pool_name}'")
    print("\nNext steps:")
    print(f"1. Start worker: prefect worker start --pool {work_pool_name}")
    print("2. Submit jobs using orchestrator.py or Prefect CLI")
    return True


if __name__ == "__main__":
    work_pool = sys.argv[1] if len(sys.argv) > 1 else "plate-resort-pool"
    
    print("Plate Resort Flow Deployment")
    print("=" * 60)
    
    success = deploy_all(work_pool)
    sys.exit(0 if success else 1)
