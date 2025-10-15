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

    worker = PlateResortWorker(work_pool_name="plate-resort-pool")
    asyncio.run(worker.start())


if __name__ == "__main__":
    main()
