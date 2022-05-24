from discord.commands import slash_command as slash, Option
from discord.ext import commands
import bot.variables as v
import discord


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(description="View the server profile of you or another member.", guild_ids=v.guilds)
    async def profile(self, ctx, member: Option(discord.Member, "The member you want to view the profile of",
                                                required=False)):
        pass


def setup(bot):
    bot.add_cog(Profile(bot))
