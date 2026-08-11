import discord

from app.config import (
    DISCORD_BOT_TOKEN,
    DISCORD_USER_ID,
)

intents = discord.Intents.default()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")

    user = await client.fetch_user(DISCORD_USER_ID)

    await user.send(
        "₍^. .^₎Ⳋ Vintage Hunter is online!"
    )

    await client.close()


client.run(DISCORD_BOT_TOKEN)