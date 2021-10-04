from discord.ext import commands
from bot.utils.Misc.help_references import cog_name_formatted
from main import main_db
from config import prefixes
import discord
import math
import re
users = main_db["users"]

# Credit to F1scherman on the Mystic Fyre Bot project and MenuDocs

class help_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', aliases=['h', 'commands'], description="Displays this help menu.")
    async def help(self, ctx, page: str = None):
        if page is None:
            cog = "1"
        else:
            cog = page
        embed = discord.Embed(title="Help Menu",
                              description="All public commands that SykeseBot offers and their respective descriptions.",
                              color=discord.Color.blue())

        cogs = [c for c in self.bot.cogs.keys()]
        # This list is a list of those cogs to be removed
        ignoredCogs = ["eval_command", "staff_management"]
        for removed_cog in ignoredCogs:
            if removed_cog not in cogs:
                print(f"Cog in help list {removed_cog} cannot be found.")
                continue
            cogs.remove(removed_cog)

        totalPages = math.ceil(len(cogs) / 4)

        if re.search(r"\d", str(cog)):
            cog = int(cog)
            if cog > totalPages or cog < 1:
                await ctx.send(f"Invalid page number, please pick from 1-{totalPages} pages.")
                return

            embed.set_footer(text=f"<> - Required & [] - Optional | Page {cog} of {totalPages}",
                             icon_url=ctx.author.avatar_url)

            neededCogs = []
            for i in range(4):
                x = i + (int(cog) - 1) * 4
                try:
                    neededCogs.append(cogs[x])
                except IndexError:
                    pass
            for cog in neededCogs:
                print(cog)
                if cog_name_formatted().get(cog) is None:
                    cog_name = cog
                else:
                    cog_name = cog_name_formatted().get(cog)

                # creates just a plain text list of the commands and their arguments to put into an embed
                commandList = ""
                for command in self.bot.get_cog(cog).walk_commands():
                    if command.hidden:
                        continue
                    if command.parent is not None:
                        continue
                    if command.signature is None:
                        usage = "yes"
                    else:
                        usage = command.signature
                    commandList += f"{prefixes[0]}{command.name} {usage} - *{command.description}*\n"
                commandList += "\n"
                if commandList is None:
                    print(f"Skipping {cog_name} due to no viable commands being found.")
                    continue
                embed.add_field(name=f"**{cog_name}**", value=commandList, inline=False)

        # the if and elif statements here are probably different sorting systems based on something
        elif re.search(r"[a-zA-Z]", str(cog)):
            lowerCogs = [c.lower() for c in cogs]
            if cog.lower() not in lowerCogs:
                await ctx.send(f"Invalid Argument, please pick from 1-{totalPages} pages.")
                return
            embed.set_footer(
                text=f"<> = Required & [] = Optional | Page {(lowerCogs.index(cog.lower()) + 1)} of {len(lowerCogs)}",
                icon_url=ctx.author.avatar_url)

            helpText = ""

            for command in self.bot.get_cog(cogs[lowerCogs.index(cog.lower())]).walk.commands():
                if command.hidden:
                    continue

                # elif command.parent != None:
                #   continue

                helpText += f"```{command.name}```\n**{command.description}**\n\n"

                if len(command.aliases) > 0:
                    helpText += f'**Aliases: ** `{", ".join(command.aliases)}`'
                helpText += '\n'

                data = await self.bot.config._Document__get_raw(ctx.guild.id)
                if not data or "prefix" not in data:
                    prefix = self.bot.DEFAULTPREFIX
                else:
                    prefix = data['prefix']

                helpText += f'**Format:** `{prefix}{command.name} {command.usage if command.usage is not None else ""}' \
                            f'`\n\n'
            embed.description = helpText

        else:
            await ctx.send(f"Invalid argument, please pick from 1-{totalPages} pages.")
            return
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(help_command(bot))
