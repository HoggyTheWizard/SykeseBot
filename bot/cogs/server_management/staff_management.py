from discord.ext import commands
from bot.utils.checks.user import manager
import discord


class staff_management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @manager()
    async def dm(self, ctx, member: discord.Member, *, message: str):
        try:
            await member.send(message)
            await ctx.send("Successfully sent message.")
        except discord.Forbidden:
            await ctx.send("Could not send message to member.")

    @commands.command()
    @manager()
    async def send(self, ctx, channel: discord.TextChannel, *, message: str):
        await channel.send(message)

        await ctx.send("Successfully sent message.")


def setup(bot):
    bot.add_cog(staff_management(bot))
