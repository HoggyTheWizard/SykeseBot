from googleapiclient.discovery import build
from discord.ext import commands, tasks
from bot.utils.misc.status import get_status
import discord
import os

youtube = build(serviceName="youtube", version="v3", developerKey=os.environ["YOUTUBE_API_KEY"], cache_discovery=False)


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_switcher.start()

    @tasks.loop(seconds=180)
    async def status_switcher(self):
        await self.bot.change_presence(activity=discord.Game(name=get_status(
            guild=self.bot.get_guild(889697074491293736),
            yt=youtube))
        )

    @status_switcher.before_loop
    async def before_printer(self):
        print("Prepping status switcher...")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Status(bot))
