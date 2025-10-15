#!/usr/bin/env python3
"""
Custom Prefect worker that maintains a persistent PlateResort instance.
Provides deploy-like permissions (work pools) with serve-like persistence.
"""

from prefect.workers.process import ProcessWorker
from plate_resort.core import PlateResort


class PlateResortWorker(ProcessWorker):
    """Custom worker that maintains a persistent hardware connection."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resort_instance = None

    async def setup(self):
        """Initialize persistent hardware connection."""
        try:
            await super().setup()
        except Exception as exc:
            # Skip work-pool creation or sync errors
            self._logger.warning(f"Skipping work-pool sync: {exc}")

        self._logger.info("Initializing persistent PlateResort instance")
        self._resort_instance = PlateResort()
        self._logger.info("PlateResort instance ready")

    async def teardown(self):
        """Clean up hardware connection."""
        if self._resort_instance:
            self._logger.info("Cleaning up PlateResort instance")
            try:
                if getattr(self._resort_instance, "port", None):
                    self._resort_instance.disconnect()
            except Exception as exc:
                self._logger.warning(f"Error during disconnect: {exc}")
            self._resort_instance = None

        await super().teardown()

    def get_resort(self):
        """Return the persistent PlateResort instance."""
        return self._resort_instance


def main():
    """
    CLI entry point: starts the custom ProcessWorker for 'plate-resort-pool'.
    """
    import asyncio

    worker = PlateResortWorker(work_pool_name="plate-resort-pool")
    asyncio.run(worker.start())


if __name__ == "__main__":
    main()
