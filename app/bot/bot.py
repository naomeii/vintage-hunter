import asyncio

from app.services.database import initialize_database
from app.services.scheduler import run_scheduler


async def main():
    print("♡ Starting Vintage Hunter...")

    initialize_database()

    await run_scheduler()


asyncio.run(main())