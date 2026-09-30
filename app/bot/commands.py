import discord
from discord import app_commands

from app.models.search import Search, Condition
from app.services.database import (
    create_user,
    get_user,
    get_saved_searches,
    save_search,
    search_exists,
)
from app.hunter import run_hunter


class ConditionSelect(discord.ui.Select):

    def __init__(self, search: Search):
        self.search = search

        options = [
            discord.SelectOption(
                label="Any",
                value="any",
                description="New or used",
            ),
            discord.SelectOption(
                label="New",
                value="new",
                description="New items only",
            ),
            discord.SelectOption(
                label="Used",
                value="used",
                description="Used items only",
            ),
        ]

        super().__init__(
            placeholder="Choose a condition",
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):

        self.search.condition = Condition(self.values[0])

        if search_exists(self.search):
            await interaction.response.send_message(
                "♡ You already have this search saved.",
                ephemeral=True,
            )
            return

        save_search(self.search)

        await interaction.response.send_message(
            "♡ Search added!",
            ephemeral=True,
        )

class ConditionView(discord.ui.View):

    def __init__(self, search: Search):
        super().__init__(timeout=60)

        self.add_item(
            ConditionSelect(search)
        )

class AddSearchModal(discord.ui.Modal, title="Add Vintage Hunter Search"):

    query = discord.ui.TextInput(
        label="Search query",
        placeholder="e.g. balenciaga city small",
        required=True,
        max_length=100,
    )

    min_price = discord.ui.TextInput(
        label="Minimum price",
        placeholder="e.g. 500",
        required=False,
        max_length=20,
    )

    max_price = discord.ui.TextInput(
        label="Maximum price",
        placeholder="e.g. 1500",
        required=False,
        max_length=20,
    )

    color = discord.ui.TextInput(
        label="Color",
        placeholder="e.g. Black",
        required=False,
        max_length=50,
    )

    async def on_submit(self, interaction: discord.Interaction):

        discord_user_id = str(interaction.user.id)

        user = get_user(discord_user_id)

        if user is None:
            user_id = create_user(discord_user_id)
        else:
            user_id = user["id"]

        try:
            min_price = (
                float(self.min_price.value)
                if self.min_price.value
                else None
            )

            max_price = (
                float(self.max_price.value)
                if self.max_price.value
                else None
            )

        except ValueError:
            await interaction.response.send_message(
                "✕ Prices must be numbers.",
                ephemeral=True,
            )
            return

        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            await interaction.response.send_message(
                "✕ Minimum price cannot be greater than maximum price.",
                ephemeral=True,
            )
            return

        search = Search(
            id=None,
            user_id=user_id,
            query=self.query.value,
            condition=Condition.ANY,
            min_price=min_price,
            max_price=max_price,
            color=self.color.value or None,
        )

        await interaction.response.send_message(
            "♡ One more thing — choose a condition:",
            view=ConditionView(search),
            ephemeral=True,
        )


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

        @self.discord_service.tree.command(
            name="add",
            description="Add a Vintage Hunter search.",
        )
        async def add(interaction: discord.Interaction):

            await interaction.response.send_modal(
                AddSearchModal()
            )

        @self.discord_service.tree.command(
            name="searches",
            description="View your saved Vintage Hunter searches.",
        )
        async def searches(interaction: discord.Interaction):

            discord_user_id = str(interaction.user.id)

            user = get_user(discord_user_id)

            if user is None:
                await interaction.response.send_message(
                    "♡ You don't have any saved searches yet.",
                    ephemeral=True,
                )
                return

            saved_searches = get_saved_searches(user["id"])

            if not saved_searches:
                await interaction.response.send_message(
                    "♡ You don't have any saved searches yet.",
                    ephemeral=True,
                )
                return

            lines = []

            for search in saved_searches:
                price_range = ""

                if search.min_price is not None:
                    price_range += f"${search.min_price:,.0f}"

                if search.max_price is not None:
                    if price_range:
                        price_range += "–"
                    price_range += f"${search.max_price:,.0f}"

                if not price_range:
                    price_range = "Any price"

                color = search.color or "Any color"

                lines.append(
                    f"**#{search.id} • {search.query}**\n"
                    f"♡ {price_range} • "
                    f"{search.condition.value.title()} • "
                    f"{color}"
                )

            await interaction.response.send_message(
                "♡ **Your saved searches**\n\n"
                + "\n\n".join(lines),
                ephemeral=True,
            )