from discord.ext import commands


class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Displays the ping of the bot.")
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong ({round(self.bot.latency*1000)}ms)")

def setup(bot):
    bot.add_cog(general(bot))
