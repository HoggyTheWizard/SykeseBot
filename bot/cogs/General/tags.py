from discord.ext import commands
from bot.utils.Misc.tag_list import tag_list
from bot.utils.Checks.channel_checks import *
from main import main_db
import discord
users = main_db["users"]


class tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @channel_restricted()
    async def tag(self, ctx, *, tag_name):
        tag_object = tag_list.get(tag_name)
        if tag_object is None:
            await ctx.send("Invalid tag! Please use the command `/tags` to view a list of tags.")
        else:
            embed = discord.Embed(title=tag_object["embedTitle"], description=tag_object["embedDescription"],
                                  color=tag_object["embedColor"])
            for item in tag_object["fields"]:
                embed.add_field(name=tag_object["fields"][item]["name"],
                                value=tag_object["fields"][item]["value"],
                                inline=tag_object["fields"][item]["inline"])
            await ctx.send(embed=embed)

    @commands.command()
    async def tags(self, ctx):
        string = "**Callable Tags**\n\n"
        total_tags = len(tag_list)
        count = 1

        for tag in tag_list:

            if count != total_tags:
                string += f"{tag}, "

            else:
                string += f"{tag}"
            count += 1

        await ctx.send(string)

def setup(bot):
    bot.add_cog(tags(bot))
