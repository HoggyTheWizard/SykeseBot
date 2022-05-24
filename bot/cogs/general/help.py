from discord.ext import commands
from discord.commands import slash_command as slash
from bot.utils.checks.user import verified
from bot.utils.checks.channel import ephemeral

from bot.variables import guilds
import discord


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(description="Displays an embed describing different aspects of the server.", guild_ids=guilds)
    @verified()
    async def help(self, ctx):
        embed = discord.Embed(title="Help Menu", description="Welcome to the help menu! Below you can find "
                                                             "information about the different commands and aspects of "
                                                             "our server.", color=discord.Color.blue())
        embed.add_field(name="Commands", value="All public commands are slash commands. To view a list of commands and "
                                               "their respective descriptions, simply type a slash and click on "
                                               "SykeseBot.", inline=False)
        embed.add_field(name="Rules", value="Our server has certain rules and guidelines that all users must abide by "
                        "to maintain a positive, healthy community. To view our rules, go to <#892118771257458738> "
                                            "and view the category titled \"Rules\". If you believe a user is breaking "
                                            "our rules, please contact a Chat Moderator.", inline=False)
        embed.add_field(name="Roles", value="We have different roles that users can obtain. To view a list of all "
                                            "important roles, go to <#892118771257458738> and view the "
                                            "category titled \"Roles\".", inline=False)
        embed.add_field(name="YouTube", value="Sykese has a YouTube channel! You can view it (and hopefully subscribe) "
                                              "by going to https://www.youtube.com/c/sykese", inline=False)
        embed.set_footer(text="Have a good day!", icon_url=ctx.guild.icon.url)
        await ctx.respond(embed=embed, ephemeral=ephemeral(ctx))


def setup(bot):
    bot.add_cog(HelpCommand(bot))
