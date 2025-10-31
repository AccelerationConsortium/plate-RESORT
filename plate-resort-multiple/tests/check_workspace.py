"""Quick connectivity probe to Prefect Cloud.

Prints the configured API URL, then lists available work pools.
Run after setting PREFECT_API_URL and PREFECT_API_KEY environment variables.
"""

import asyncio
import os
from prefect.client.orchestration import get_client


def get_api_url():
    url = os.getenv("PREFECT_API_URL")
    if not url:
        print("[WARN] PREFECT_API_URL not set in environment.")
    else:
        print(f"API URL: {url}")
    return url


async def main():
    get_api_url()
    async with get_client() as client:
        try:
            pools = await client.read_work_pools()
        except AttributeError:
            print(
                "[ERROR] Client method read_work_pools() not available in this Prefect version."
            )
            return
        names = [p.name for p in pools]
        print(f"Work pools ({len(names)}): {names}")
        # Show first pool detail for extra confirmation
        if names:
            first = await client.read_work_pool(names[0])
            print(f"First pool '{first.name}' type: {first.type}")


if __name__ == "__main__":
    asyncio.run(main())
