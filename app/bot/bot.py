import asyncio

from app.services.database import initialize_database
from app.services.discord import DiscordService
from app.services.scheduler import run_scheduler


async def main():
    print("♡ Starting Vintage Hunter...")

    initialize_database()

    discord_service = DiscordService()

    await discord_service.login()

    try:
        await run_scheduler(discord_service)
    finally:
        await discord_service.close()


asyncio.run(main())