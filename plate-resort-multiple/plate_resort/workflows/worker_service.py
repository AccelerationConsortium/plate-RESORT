#!/usr/bin/env python3
"""
Custom Prefect worker that maintains a persistent PlateResort instance.
This provides deploy-like permissions (work pools) with serve-like persistence.

Documentation:
- ProcessWorker: https://docs.prefect.io/latest/api-ref/prefect/workers/process/
- Custom Workers: https://docs.prefect.io/latest/concepts/workers/
"""
import asyncio
from prefect.workers.process import ProcessWorker
from plate_resort.core import PlateResort


class PlateResortWorker(ProcessWorker):
    """Custom worker that maintains a persistent hardware connection."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resort_instance = None
    
    async def setup(self):
        """Initialize persistent hardware connection"""
        await super().setup()
        self.logger.info("Initializing persistent PlateResort instance")
        self._resort_instance = PlateResort()
        # Note: connect() will be called by flows when needed
        # Not calling it here to avoid hardware initialization issues
        self.logger.info("PlateResort instance ready")
        
    async def teardown(self):
        """Clean up hardware connection"""
        if self._resort_instance:
            self.logger.info("Cleaning up PlateResort instance")
            if self._resort_instance.port:
                self._resort_instance.disconnect()
            self._resort_instance = None
        await super().teardown()
    
    def get_resort(self):
        """Get the persistent resort instance"""
        return self._resort_instance


if __name__ == "__main__":
    asyncio.run(PlateResortWorker(work_pool_name="plate-resort-pool").start())