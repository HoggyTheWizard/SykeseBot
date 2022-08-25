from discord.ext import commands, tasks
from bot.utils.misc.requests import mojang
from bot.utils.misc.sync import set_nick
from asyncio import sleep
from db import main_db
import bot.variables as v
from datetime import datetime
import config

users = main_db["users"]
settings = main_db["settings"]


class NameSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.name_sync.start()

    @tasks.loop(minutes=30)
    async def name_sync(self):
        if config.host != "master" or settings.find_one({"id": "TASKS"})["name_sync"]["lastRun"] + 3600 > \
                int(datetime.now().timestamp()):
            return

        print("Running Name Sync task...")
        settings.update_one({"id": "TASKS"}, {"$set": {"name_sync.lastRun": int(datetime.now().timestamp())}})

        guild = self.bot.get_guild(v.guilds[0])

        for member in guild.members:
            if member.bot or len([role.id for role in member.roles if role.id == v.sync_lock_id]):
                continue

            doc = users.find_one({"id": member.id})

            if not doc:
                continue

            request = await mojang(uuid=doc.get("uuid", None))
            if not request:
                continue

            await set_nick(member, request)

    @name_sync.before_loop
    async def before_name_sync(self):
        await self.bot.wait_until_ready()

    @name_sync.error
    async def name_sync_error(self, error):
        await self.bot.get_channel(v.bot_logs).send(f"Error in NameSync task:\n{error}")
        await sleep(60)
        self.name_sync.start()


def setup(bot):
    bot.add_cog(NameSync(bot))
