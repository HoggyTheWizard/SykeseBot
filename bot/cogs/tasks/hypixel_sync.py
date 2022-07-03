from discord.ext import commands, tasks
from bot.utils.misc.sync import *
from bot.utils.misc.requests import player
from db import main_db
import bot.variables as v
from datetime import datetime
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

        rank_roles, level_roles = await get_hypixel_roles(guild)

        channel = guild.get_channel(v.bot_logs)
        success = 0
        exempt = 0
        no_change = 0
        failed = 0

        for member in guild.members:
            doc = users.find_one({"id": member.id})

            if not doc:
                no_change += 1
                continue

            request = await player(uuid=doc.get("uuid", None))

            if not request:
                no_change += 1
                continue

            # a list of role ids the member has
            member_roles = [role.id for role in member.roles]

            if v.sync_lock_id in member_roles or member.bot:
                exempt += 1
                continue

            statuses = await set_hypixel(guild=guild, member=member, request=request, rank_roles=rank_roles,
                                         level_roles=level_roles)

            if statuses[0]:
                success += 1
            elif statuses[0] is False:
                failed += 1
            else:
                no_change += 1

            if statuses[1]:
                success += 1
            elif statuses[1] is False:
                failed += 1
            else:
                no_change += 1

        await channel.send(f"Finished syncing Hypixel levels and ranks:\n{success} successful\n{failed} failed\n"
                           f"{exempt} exempt\n{no_change} no change")

    @hypixel_sync.before_loop
    async def before_hypixel_sync(self):
        print("Prepping Hypixel sync...")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(HypixelSync(bot))
