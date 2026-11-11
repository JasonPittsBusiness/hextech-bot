import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import database

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=commands.DefaultHelpCommand(
        sort_commands=False, no_category="General", show_parameter_descriptions=False
    ),
)


async def main():
    discord.utils.setup_logging()
    await database.init_db()
    await bot.load_extension("cogs.rank")
    await bot.start(bot_token)


if __name__ == "__main__":
    asyncio.run(main())
