from discord.commands import slash_command as slash, Option
from bot.utils.misc.sync import *
from bot.utils.misc.requests import mojang, player
from bot.utils.checks.user import manager
from bot.utils.checks.channel import ephemeral
from db import main_db
from discord.ext import commands
import bot.variables as v
import discord

settings = main_db["settings"]
users = main_db["users"]


class ManageTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(description="Manage tasks", guilds=v.guilds)
    @manager()
    async def taskreset(self, ctx, task: Option(str, "The name of the task you want to reset.",
                                                choices=["hypixel_sync", "name_sync", "all"])):
        payload = {"hypixel_sync.lastRun": 0, "name_sync.lastRun": 0}
        if task != "all":
            message = f"the {task} task"
            payload = {f"{task}.lastRun": 0}
        else:
            message = f"all tasks"
        settings.update_one({"id": "TASKS"}, {"$set": payload})
        await ctx.respond(f"Successfully reset {message}. The selected task(s) will run within 30 minutes.",
                          ephemeral=ephemeral(ctx))

    @slash(description="Force sync a user", guilds=v.guilds)
    @manager()
    async def forcesync(self, ctx, member: discord.Member):

        if not member:
            await ctx.respond("The member you selected isn't valid.", ephemeral=ephemeral(ctx))
            return

        doc = users.find_one({"id": member.id})

        if not doc:
            await ctx.respond("This member hasn't verified yet, and as such cannot be synced.",
                              ephemeral=ephemeral(ctx))
            return

        raw_hypixel = await player(uuid=doc.get("uuid", None))
        raw_mojang = await mojang(uuid=doc.get("uuid", None))

        if not raw_mojang or not raw_hypixel:
            await ctx.respond("Failed to get data from Mojang or Hypixel.", ephemeral=ephemeral(ctx))
            return

        await set_nick(member=member, request=raw_mojang)
        await set_hypixel(guild=ctx.guild, member=member, request=raw_hypixel)

        await ctx.respond(f"Synced {str(member)}")


def setup(bot):
    bot.add_cog(ManageTasks(bot))
