from discord.ext import commands, tasks
from bot.utils.hypixel.player import Player, levels, ranks
from bot.utils.misc.requests import player
from db import main_db
import bot.variables as v
from datetime import datetime
import config
import discord

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

        # rank information is stored in a dict. In the list comp, x is the key
        rank_roles = [guild.get_role(ranks[x]["role"]) for x in ranks]

        # level roles are stored in a list of tuples, where [0] is the required level and [1] is the role
        level_roles = [guild.get_role(x[1]) for x in levels]

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

            p = Player(request)
            # level returns the user's actual Hypixel level and the role associated with it, in that order
            level, corresponding_level_role = p.level()
            corresponding_rank_role = p.rank()["role"]

            # handling level role
            if corresponding_level_role not in member_roles:
                try:
                    await member.remove_roles(*level_roles)
                    await member.add_roles(guild.get_role(corresponding_level_role))
                    success += 1
                except discord.Forbidden:
                    failed += 1
                    await channel.send(f"I don't have permission to add {str(corresponding_level_role)} to "
                                       f"{str(member)}.")

            # handling rank role
            if corresponding_rank_role not in member_roles:
                try:
                    await member.remove_roles(*rank_roles)
                    await member.add_roles(guild.get_role(corresponding_rank_role))
                    success += 1
                except discord.Forbidden:
                    failed += 1
                    await channel.send(f"I don't have permission to add {str(p.rank()['role'])} to {str(member)}.")

        await channel.send(f"Finished syncing Hypixel levels and ranks:\n{success} successful\n{failed} failed\n"
                           f"{exempt} exempt\n{no_change} no change")

    @hypixel_sync.before_loop
    async def before_hypixel_sync(self):
        print("Prepping Hypixel sync...")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(HypixelSync(bot))
