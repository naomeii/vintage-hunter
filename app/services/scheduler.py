import asyncio

from app.hunter import run_hunter
from app.services.discord import DiscordService
from app.config import HUNTER_INTERVAL_SECONDS


async def run_scheduler(discord_service: DiscordService):
    while True:
        try:
            print("\n♡ Vintage Hunter is hunting...")

            await run_hunter(discord_service)

            print(
                f"♡ Hunt complete. "
                f"Next hunt in {HUNTER_INTERVAL_SECONDS // 60} minutes."
            )

        except Exception as error:
            print(f"Hunter error: {error}")
            print("♡ Vintage Hunter will try again on the next cycle.")

        await asyncio.sleep(HUNTER_INTERVAL_SECONDS)