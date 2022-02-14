from discord.commands import slash_command as slash, user_command
from bot.utils.UI.report_modal import ReportModal
from discord.ext import commands
import variables as v
import discord

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #@slash(guild_ids=v.guilds)
    @user_command(guild_ids=v.guilds)
    async def rep(self, ctx, member):
        modal = ReportModal(title=f"Report Against {str(member)}", ctx=ctx)
        await ctx.interaction.response.send_modal(modal)

def setup(bot):
    bot.add_cog(Report(bot))
