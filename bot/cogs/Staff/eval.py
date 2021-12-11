from config import hypixel_api_key
from discord.ext import commands
from main import main_db
from config import irl_name
from bot.utils.Misc.eval_utils import *
from traceback import format_exception
import io
import contextlib
import textwrap
import discord
import requests

users = main_db["users"]


class eval_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="eval", aliases=["exec"], description="Evaluates an input script.", hidden=True)
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
        code = clean_code(code)

        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "hypixel_api_key": hypixel_api_key,
            "requests": requests,
            "users": users,
            "db": main_db
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )
                color = discord.Color.green()
                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}"
        except Exception as e:
            color = discord.Color.red()
            result = "".join(format_exception(e, e, e.__traceback__)).replace(irl_name, "Hoggy")
        embed = discord.Embed(title="Code Executed", description=f"```py\n{result}\n```", color=color)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(eval_command(bot))
