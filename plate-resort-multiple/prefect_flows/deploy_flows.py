#!/usr/bin/env python3
"""
Helper script to deploy all Plate Resort flows to a work pool.
Run this script after creating the work pool to deploy all flows.
"""
from plate_resort.core import PlateResort

work_pool_name = "plate-resort-pool"

# Get a resort instance to access flow methods
resort = PlateResort()

flows = [
    (resort.connect, "plate-resort-connect"),
    (resort.disconnect, "plate-resort-disconnect"),
    (resort.get_motor_health, "plate-resort-health"),
    (resort.activate_hotel, "plate-resort-activate-hotel"),
    (resort.go_home, "plate-resort-go-home"),
    (resort.move_to_angle, "plate-resort-move-to-angle"),
    (resort.set_speed, "plate-resort-set-speed"),
    (resort.emergency_stop, "plate-resort-emergency-stop"),
    (resort.get_current_position, "plate-resort-get-position"),
]

print(f"Deploying {len(flows)} flows to work pool: {work_pool_name}")
print("-" * 60)

for flow, deployment_name in flows:
    flow.deploy(
        name=deployment_name,
        work_pool_name=work_pool_name,
    )
    print(f"✓ Deployed: {deployment_name}")

print("-" * 60)
print(f"Successfully deployed all flows to '{work_pool_name}'")
print("\nNext steps:")
print(f"1. Start worker: prefect worker start --pool {work_pool_name}")
print("2. Submit jobs using orchestrator.py or Prefect CLI")

