#!/usr/bin/env python3
"""
Helper script to deploy all Plate Resort flows to a work pool.
Run this script after creating the work pool to deploy all flows.
"""
from prefect import flow

work_pool_name = "plate-resort-pool"

# Define flows using from_source to avoid hardware initialization during deployment
# Deployment names should be concise since they're combined with flow name
flow_specs = [
    ("connect", "connect"),
    ("disconnect", "disconnect"),
    ("get_motor_health", "health"),
    ("activate_hotel", "activate-hotel"),
    ("go_home", "go-home"),
    ("move_to_angle", "move-to-angle"),
    ("set_speed", "set-speed"),
    ("emergency_stop", "emergency-stop"),
    ("get_current_position", "get-position"),
]

print(f"Deploying {len(flow_specs)} flows to work pool: {work_pool_name}")
print("-" * 60)

for flow_method, deployment_name in flow_specs:
    flow.from_source(
        source=".",
        entrypoint=f"plate_resort/core.py:PlateResort.{flow_method}",
    ).deploy(
        name=deployment_name,
        work_pool_name=work_pool_name,
    )
    print(f"✓ Deployed: {deployment_name}")

print("-" * 60)
print(f"Successfully deployed all flows to '{work_pool_name}'")
print("\nNext steps:")
print(f"1. Start worker: prefect worker start --pool {work_pool_name}")
print("2. Submit jobs using orchestrator.py or Prefect CLI")