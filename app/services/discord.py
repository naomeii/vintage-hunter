# used to expose methods like send_listing_notification()
import discord

from app.config import DISCORD_BOT_TOKEN, DISCORD_USER_ID
from app.models.listing import Listing
from app.models.authenticity_result import AuthenticityResult, Recommendation


class DiscordService:

    def __init__(self):
        intents = discord.Intents.default()

        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            print(f"Logged in as {self.client.user}!")

    async def login(self):
        await self.client.login(DISCORD_BOT_TOKEN)

    async def start(self):
        await self.client.start(DISCORD_BOT_TOKEN)

    async def close(self):
        await self.client.close()

    async def send_message(self, message: str):
        user = await self.client.fetch_user(DISCORD_USER_ID)
        await user.send(message)

    async def send_listing_notification(
        self,
        listing: Listing,
        result: AuthenticityResult,
    ):
        if result.recommendation == Recommendation.BUY:
            color = 0x57F287
            greeting = "₍^. .^₎Ⳋ I found something!"
            verdict = "♡ BUY ♡"

        elif result.recommendation == Recommendation.INVESTIGATE:
            color = 0xFEE75C
            greeting = "( •̀ᴗ•́ )و Worth a closer look!"
            verdict = "❀ INVESTIGATE ❀"

        else:
            color = 0xED4245
            greeting = "૮ • ﻌ • ა I'd pass on this one."
            verdict = "✕ AVOID ✕"

        embed = discord.Embed(
            title=listing.title,
            url=listing.listing_url,
            description=greeting,
            color=color,
        )

        embed.add_field(
            name="୨୧ Verdict",
            value=f"{verdict} • {result.confidence:.0%}",
            inline=False,
        )

        embed.add_field(
            name="୨୧ Price",
            value=f"${listing.price:,.2f} {listing.currency}",
            inline=False,
        )

        embed.add_field(
            name="୨୧ Seller",
            value=(
                f"{listing.seller_username} • "
                f"{listing.seller_feedback_percent:.1f}% "
                f"({listing.seller_feedback_score:,})"
            ),
            inline=False,
        )

        embed.add_field(
            name="୨୧ Condition",
            value=listing.condition,
            inline=False,
        )

        embed.add_field(
            name="୨୧ Thoughts",
            value=result.explanation,
            inline=False,
        )

        embed.set_image(url=listing.thumbnail_image_url)

        embed.set_footer(
            text="Vintage Hunter • eBay"
        )

        view = discord.ui.View()

        view.add_item(
            discord.ui.Button(
                label="View Listing",
                url=listing.listing_url,
            )
        )

        user = await self.client.fetch_user(DISCORD_USER_ID)

        await user.send(
            embed=embed,
            view=view,
        )