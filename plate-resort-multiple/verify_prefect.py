#!/usr/bin/env python3
"""Quick verification of Prefect Cloud setup for Plate Resort.

Checks:
  - API URL & key presence
  - Work pool exists
  - Deployments present for expected flow names
  - Reports most recent flow run statuses (optional)
"""
from __future__ import annotations
import os
import asyncio
from prefect import get_client

EXPECTED_DEPLOYMENTS = {
    "connect",
    "disconnect",
    "health",
    "activate-hotel",
    "go-home",
    "move-to-angle",
    "set-speed",
    "emergency-stop",
    "get-position",
}
WORK_POOL = "plate-resort-pool"


async def main() -> int:
    api_url = os.getenv("PREFECT_API_URL")
    api_key = os.getenv("PREFECT_API_KEY")
    print("Prefect verification starting...")
    if not api_url or not api_key:
        print("ERROR: PREFECT_API_URL or PREFECT_API_KEY not set")
        return 1
    print(f"API URL: {api_url}")

    async with get_client() as client:
        # Work pool check
        try:
            wp = await client.read_work_pool(WORK_POOL)
            print(f"Work pool OK: {wp.name}")
        except Exception as e:  # noqa: BLE001
            print(f"ERROR: Cannot read work pool '{WORK_POOL}': {e}")
            return 2

        # Read deployments
        deployments = await client.read_deployments()
        names = {d.name for d in deployments}
        missing = EXPECTED_DEPLOYMENTS - names
        extra = names - EXPECTED_DEPLOYMENTS
        print(f"Found {len(names)} deployments")
        if missing:
            print("Missing deployments:")
            for m in sorted(missing):
                print(f"  - {m}")
        else:
            print("All expected deployments present")
        if extra:
            print("Extra deployments (legacy or test):")
            for e in sorted(extra):
                print(f"  - {e}")

        # Recent flow runs (best effort)
        try:
            flow_runs = await client.read_flow_runs(limit=5)
            print("Recent flow runs (latest 5):")
            for fr in flow_runs:
                state_summary = f"{fr.state.type}:{fr.state.name}"
                print(f"  - {fr.name} | {fr.id} | {state_summary}")
        except Exception as e:  # noqa: BLE001
            print(f"(Skipping flow runs listing: {e})")

    print("Verification complete.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(asyncio.run(main()))
