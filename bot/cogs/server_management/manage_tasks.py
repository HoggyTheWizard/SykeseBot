from discord.commands import slash_command as slash, Option
from bot.utils.checks.user import manager
from bot.utils.checks.channel import ephemeral
from db import main_db
from discord.ext import commands
import bot.variables as v
import discord

settings = main_db["settings"]


class ManageTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(description="Manage tasks", guilds=v.guilds)
    @manager()
    async def taskreset(self, ctx, task: Option(str, "The name of the task you want to reset.",
                                                options=["hypixel_sync", "name_sync", "all"])):
        payload = {"hypixel_sync": 0, "name_sync": 0}
        if task != "all":
            payload = {task: 0}

        settings.update_one({"id": "TASKS"}, {"$set": payload})
        await ctx.respond(f"Task {task} has been reset.", ephemeral=ephemeral(ctx))


def setup(bot):
    bot.add_cog(ManageTasks(bot))
