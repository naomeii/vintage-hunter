import asyncio

from app.services.database import initialize_database
from app.services.discord import DiscordService
from app.services.scheduler import run_scheduler
from app.bot.commands import CommandService


async def main():
    print("♡ Starting Vintage Hunter...")

    initialize_database()

    discord_service = DiscordService()

    command_service = CommandService(discord_service)
    command_service.register_commands()

    await asyncio.gather(
        discord_service.start(),
        run_scheduler(discord_service),
    )


asyncio.run(main())