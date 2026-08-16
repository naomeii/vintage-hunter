import asyncio

from app.services.discord import DiscordService


async def main():
    discord = DiscordService()
    await discord.start()


asyncio.run(main())
