from discord.commands import slash_command as slash, Option
from bot.utils.ui.confirm import Confirm
from bot.utils.checks.user import manager
from datetime import datetime
from discord.ext import commands
from db import main_db
import bot.variables as v
import discord

users = main_db["users"]


class ManageLeveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(guild_ids=v.guilds)
    @manager()
    async def wipe(self, ctx,
                   member: Option(discord.Member, description="The member you want to wipe leveling data for."),
                   blacklist: Option(str, description="Should this user be prevented from gaining XP?",
                                     choices=["Yes", "No"])
                   ):
        if not member:
            await ctx.respond("You must specify a valid member.", ephemeral=True)
            return

        embed = discord.Embed(title=f"{str(member)} - Wipe Leveling Data",
                              description="This will completely wipe all leveling data pertaining to this user.",
                              color=discord.Color.red())
        view = Confirm()
        view.interaction = ctx.interaction
        message = await ctx.respond(embed=embed, view=view)
        view.interaction = ctx.interaction
        await view.wait()

        if view.value:
            users.update_one(
                {"id": member.id}, {"$rename": {"Leveling": f"WipedLeveling{datetime.now().timestamp()}"}})

            if blacklist == "Yes":
                users.update_one({"id": member.id}, {"$set": {"levelingBlacklist": True}})

            await message.edit_original_message(content="Successfully wiped leveling data.", embed=None, view=None)


def setup(bot):
    bot.add_cog(ManageLeveling(bot))
