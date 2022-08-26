from discord.ext import commands, tasks
from bot.utils.misc.sync import *
from bot.utils.misc.requests import player
from asyncio import sleep
from db import main_db
import bot.variables as v
from datetime import datetime
import logging
import config

users = main_db["users"]
settings = main_db["settings"]


class HypixelSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hypixel_sync.start()

    @tasks.loop(minutes=30)
    async def hypixel_sync(self):
        if config.host != "master" or settings.find_one({"id": "TASKS"})["hypixel_sync"]["lastRun"] + 86400 > \
                int(datetime.now().timestamp()):
            return

        print("Running Hypixel Sync task...")
        settings.update_one({"id": "TASKS"}, {"$set": {"hypixel_sync.lastRun": int(datetime.now().timestamp())}})
        guild = self.bot.get_guild(v.guilds[0])

        rank_roles, level_roles = get_hypixel_roles(guild)

        for member in guild.members:
            doc = users.find_one({"id": member.id})

            if not doc:
                continue

            request = await player(uuid=doc.get("uuid", None))

            if not request:
                continue

            # a list of role ids the member has
            member_roles = [role.id for role in member.roles]

            if v.sync_lock_id in member_roles or member.bot:
                continue

            await set_hypixel(guild=guild, member=member, request=request, rank_roles=rank_roles, level_roles=level_roles)

    @hypixel_sync.before_loop
    async def before_hypixel_sync(self):
        print("Prepping Hypixel sync...")
        await self.bot.wait_until_ready()

    @hypixel_sync.error
    async def hypixel_sync_error(self, error):
        logging.getLogger(__name__).error("", exc_info=error)
        await sleep(60)
        self.hypixel_sync.start()


def setup(bot):
    bot.add_cog(HypixelSync(bot))
