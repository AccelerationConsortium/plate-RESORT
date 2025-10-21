#!/usr/bin/env python3
"""Deploy all Plate Resort flows to Prefect Cloud.

Prefect Cloud requires image or remote source storage for deployments.
We avoid building a container by pointing flows to the public Git repository.

Environment overrides:
    PLATE_RESORT_GIT_REF   Optional branch, tag, or commit SHA (default: main)

Pin a specific commit: export PLATE_RESORT_GIT_REF=<ref>
"""
import os
from plate_resort.workflows import flows
from prefect.runner.storage import GitRepository

REPO_URL = "https://github.com/AccelerationConsortium/plate-RESORT.git"
GIT_REF = os.getenv("PLATE_RESORT_GIT_REF", "main")  # branch/tag info
GIT_COMMIT = os.getenv("PLATE_RESORT_GIT_COMMIT")  # 40-char commit SHA

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
    """Deploy function-based flows using remote Git source (no image build)."""
    work_pool_name = "plate-resort-pool"
    print(
        f"Deploying {len(FUNCTION_FLOWS)} flows to work pool: {work_pool_name}"
        f" (ref: {GIT_REF}{' commit: ' + GIT_COMMIT if GIT_COMMIT else ''})"
    )
    if not GIT_COMMIT:
        print("WARNING: no commit SHA; cloning default 'main'.")
    print("If path missing: set PLATE_RESORT_GIT_COMMIT and redeploy.")
    print("-" * 60)
    for flow_obj, deployment_name in FUNCTION_FLOWS:
        # Repo layout nests package in 'plate-resort-multiple/plate_resort/'.
        # Entrypoint must include that base folder for Prefect Cloud cloning.
        entrypoint = (
            "plate-resort-multiple/plate_resort/workflows/flows.py:" +
            f"{flow_obj.fn.__name__}"
        )
        print(
            f"Deploying '{deployment_name}' (flow: {flow_obj.fn.__name__},"
            f" entrypoint: {entrypoint})"
        )
    # Attach remote source; from_source returns new Flow with storage metadata
        if GIT_COMMIT:
            storage = GitRepository(repo_url=REPO_URL, commit_sha=GIT_COMMIT)
            source_flow = flow_obj.from_source(
                source=storage,
                entrypoint=entrypoint,
            )
        else:
            # Fallback: no commit provided; attempt clone of default branch.
            source_flow = flow_obj.from_source(
                source=REPO_URL,
                entrypoint=entrypoint,
            )
        source_flow.deploy(
            name=deployment_name,
            work_pool_name=work_pool_name,
        )
        print(f"\u2713 Deployed: {deployment_name}")
    print("-" * 60)
    print(f"Successfully deployed all flows to '{work_pool_name}'")
    print("\nNext steps:")
    print(f"1. Start worker: prefect worker start --pool {work_pool_name}")
    print("2. Run a deployment: prefect deployment run 'connect/connect'")
    print("3. (Optional) Pin git ref: set PLATE_RESORT_GIT_REF then redeploy")


if __name__ == "__main__":  # pragma: no cover
    main()
