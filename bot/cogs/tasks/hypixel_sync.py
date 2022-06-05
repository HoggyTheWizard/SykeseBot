from discord.ext import commands, tasks
from bot.utils.hypixel.player import Player, levels, ranks
from bot.utils.misc.requests import player
from db import main_db
import bot.variables as v
import discord
import aiohttp
import config

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
        session = aiohttp.ClientSession()
        success = 0
        exempt = 0
        no_change = 0
        failed = 0

        for member in guild.members:
            roles = [role.id for role in member.roles if role.id in [x["role"] for x in ranks] or
                     role.id in [x[1] for x in levels]]
            if member.bot or len([role for role in roles if role.id == v.sync_lock_id]) or \
                    v.verified_role_id not in roles:
                exempt += 1
                continue

            doc = users.find_one({"id": member.id})
            request = await player(session=session, uuid=doc.get("uuid", None))

            if not doc or not request:
                no_change += 1
                continue

            p = Player(player=request)

            # rank
            rank = [x for x in ranks if any(x in roles for x in rank_roles)]
            if p.rank()["role"] != rank:
                await member.add_roles(guild.get_role(p.rank()["role"]))

            # leveling
            level = [x for x in levels if any(x in roles for x in level_roles)]
            if p.level()[1] != level:
                await member.add_roles(guild.get_role(p.level()[1]))

        await channel.send(f"Finished syncing names:\n{success} successful\n{failed} failed\n{exempt} "
                           f"exempt\n{no_change} no change")

    @hypixel_sync.before_loop
    async def before_name_sync(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(HypixelSync(bot))
