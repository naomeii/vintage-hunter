import discord
from discord import app_commands

from app.services.database import (
    create_user,
    get_user,
)
from app.hunter import run_hunter


class CommandService:

    def __init__(self, discord_service):
        self.discord_service = discord_service

    def register_commands(self):

        @self.discord_service.tree.command(
            name="hunt",
            description="Run Vintage Hunter for your saved searches.",
        )
        async def hunt(interaction: discord.Interaction):

            discord_user_id = str(interaction.user.id)

            user = get_user(discord_user_id)

            if user is None:
                create_user(discord_user_id)
                user = get_user(discord_user_id)

            await interaction.response.send_message(
                "♡ Vintage Hunter is hunting...",
                ephemeral=True,
            )

            await run_hunter(
                user["id"],
                self.discord_service,
            )