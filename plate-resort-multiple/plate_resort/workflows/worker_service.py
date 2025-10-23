#!/usr/bin/env python3
"""
Custom Prefect worker that maintains a persistent PlateResort instance.
Provides deploy-like permissions (work pools) with serve-like persistence.
"""

from prefect.workers.process import ProcessWorker


class PlateResortWorker(ProcessWorker):
    """Custom worker for Plate Resort flows."""

    pass


def main():
    """
    CLI entry point: starts the custom ProcessWorker for 'plate-resort-pool'.
    """
    import asyncio
    import os

    # Allow overriding the work pool via environment variable for flexibility.
    pool = os.getenv("PLATE_RESORT_POOL", "plate-resort-pool")

    worker = PlateResortWorker(work_pool_name=pool)
    asyncio.run(worker.start())


if __name__ == "__main__":
    main()
