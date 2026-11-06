import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def main():
    discord.utils.setup_logging()
    await bot.load_extension("cogs.rank")
    await bot.start(bot_token)


if __name__ == "__main__":
    asyncio.run(main())
