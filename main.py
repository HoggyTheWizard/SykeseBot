from bot_loader import BotLoader
from discord.ext import commands
from dotenv import load_dotenv
import logging
import discord
import config
import os

load_dotenv("config.env")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s - %(name)s] %(message)s")
logging.getLogger("discord").setLevel(logging.WARNING)

bot = BotLoader(commands.when_mentioned_or(*config.prefixes), case_insensitive=True,
                max_messages=None, intents=discord.Intents.all(), help_command=None)

bot.run(os.environ["TOKEN"])
