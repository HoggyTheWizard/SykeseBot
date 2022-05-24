from discord.ext import commands, tasks
from bot.utils.Misc.requests import mojang
from db import main_db
import bot.variables as v
import discord
import aiohttp
import config

users = main_db["users"]


class NameSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.name_sync.start()

    @tasks.loop(hours=1)
    async def name_sync(self):
        if config.host != "master":
            return

        guild = self.bot.get_guild(v.guilds[0])
        channel = guild.get_channel(v.bot_logs)
        session = aiohttp.ClientSession()
        success = 0
        exempt = 0
        no_change = 0
        failed = 0

        for member in guild.members:
            if member.bot or len([role.id for role in member.roles if role.id == v.sync_lock_id]):
                exempt += 1
                continue

            doc = users.find_one({"id": member.id})
            request = await mojang(session=session, uuid_or_name=doc.get("uuid", None))

            if not doc or not request:
                no_change += 1
                continue

            elif not member.nick and request["name"] != member.name or member.nick != request["name"]:
                try:
                    await member.edit(nick=request["name"])
                    success += 1
                except discord.Forbidden:
                    failed += 1
                    await channel.send(f"I don't have permission to change {str(member)}'s nickname. ({member.id})")

        await channel.send(f"Finished syncing names:\n{success} successful\n{failed} failed\n{exempt} "
                           f"exempt\n{no_change} no change")

    @name_sync.before_loop
    async def before_name_sync(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(NameSync(bot))
