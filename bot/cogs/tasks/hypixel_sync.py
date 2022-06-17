from discord.ext import commands, tasks
from bot.utils.hypixel.player import Player, levels, ranks
from bot.utils.misc.requests import player
from db import main_db
import bot.variables as v
import config
import discord

users = main_db["users"]


class HypixelSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hypixel_sync.start()

    @tasks.loop(hours=24)
    async def hypixel_sync(self):
        if config.host != "master":
            return

        rank_roles = [x["role"] for x in ranks]
        level_roles = [x[1] for x in levels]
        guild = self.bot.get_guild(v.guilds[0])
        channel = guild.get_channel(v.bot_logs)
        success = 0
        exempt = 0
        no_change = 0
        failed = 0

        for member in guild.members:
            # creates a list of all roles the user has pertaining to Hypixel level and rank
            roles = [role.id for role in member.roles if role.id in [x["role"] for x in ranks] or
                     role.id in [x[1] for x in levels]]

            # exempts members if they have the sync lock role or aren't verified
            if member.bot or len([role for role in roles if role.id == v.sync_lock_id]) or \
                    v.verified_role_id not in roles:
                exempt += 1
                continue

            doc = users.find_one({"id": member.id})
            request = await player(uuid=doc.get("uuid", None))

            if not doc or not request:
                no_change += 1
                continue

            # The Player class includes handlers for annoying tasks in the Hypixel API, such as getting Network level
            p = Player(player=request)

            # rank
            rank = [x for x in ranks if any(x in roles for x in rank_roles)]
            if p.rank()["role"] != rank:
                try:
                    await member.remove_roles(guild.get_role(rank[0]))
                    await member.add_roles(guild.get_role(p.rank()["role"]))
                except discord.Forbidden:
                    failed += 1
                    await channel.send(f"I don't have permission to edit roles for {str(member)} ({member.id})")

            # leveling
            level = [x for x in levels if any(x in roles for x in level_roles)]
            if p.level()[1] != level:
                try:
                    await member.remove_roles(guild.get_role(level[0]))
                    await member.add_roles(guild.get_role(p.level()[1]))
                except discord.Forbidden:
                    failed += 1
                    await channel.send(f"I don't have permission to edit roles for {str(member)} ({member.id})")

        await channel.send(f"Finished syncing names:\n{success} successful\n{failed} failed\n{exempt} "
                           f"exempt\n{no_change} no change")

    @hypixel_sync.before_loop
    async def before_hypixel_sync(self):
        print("Prepping Hypixel sync...")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(HypixelSync(bot))
