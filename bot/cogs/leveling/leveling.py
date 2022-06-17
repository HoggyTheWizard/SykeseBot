from discord.commands import slash_command as slash
from bot.utils.leveling.leveling import get_leveling, levelup
from bot.utils.checks.user import verified
from bot.utils.checks.channel import ephemeral
from bot.variables import guilds
from discord.ext import commands
from db import main_db
import random
import time
import discord
import config

users = main_db["users"]
blacklisted_channels = [
                893934059804319775,  # verification
                893936274291974164  # bots
            ]


class LevelingMain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if config.host != "master":
            return
        elif not message.guild or message.guild.id not in [889697074491293736] or message.author.bot or \
                message.type == discord.MessageType.application_command:
            return

        else:
            doc = users.find_one({"id": message.author.id})

            if not doc and message.channel.id not in blacklisted_channels:
                leveling = get_leveling(doc)
                current_exp = leveling["exp"]
                last_triggered_message = leveling["lastTriggeredMessage"]

                # 90 represents the cooldown
                if not last_triggered_message or last_triggered_message + 90 < int(time.time()) or \
                        not leveling.get("expBlacklist", False):
                    added_exp = random.randint(15, 20)
                    users.update_one({"id": message.author.id}, {"$set":
                                     {"Leveling.exp": current_exp + added_exp,
                                      "Leveling.lastTriggeredMessage": int(time.time())}})
                    await levelup(message.guild, users, doc, leveling, message.author, message)

    @slash(description="DEPRECIATED LEVEL COMMAND - USE /PROFILE INSTEAD", guild_ids=guilds)
    @verified()
    async def level(self, ctx):
        await ctx.respond("This command has been depreciated, please use the `/profile` command to view leveling data "
                          "instead.", ephemeral=True)

    @slash(guild_ids=guilds, description="A leaderboard displaying the top exp earners in our server.")
    @verified()
    async def level_leaderboard(self, ctx):
        embed = discord.Embed(title="Level Leaderboard",
                              description="A leaderboard displaying the top exp earners in our server. "
                                          "The way levels are calculated has been changed - you did not lose exp.",
                              color=ctx.author.color)
        id_list = [member.id for member in ctx.guild.members]
        lb = users.find({}).sort("Leveling.exp", -1)
        i = 0
        for user in lb:
            if "Leveling" not in user:
                continue
            elif user["id"] not in id_list:
                continue
            else:
                i += 1
                embed.add_field(name=f"#{i}",
                                value=f"<@{user['id']}>\nLevel {user['leveling'].get('level', 0)}\n"
                                      f"{'{:,}'.format(user['leveling'].get('exp', 0))} exp", inline=True)
            if i >= 20:
                break

        author = users.find_one({"id": ctx.author.id})

        if author is None:
            footer = "Level 0 (0 exp)"

        elif author.get("Leveling", None) is None:
            footer = "Level 0 (0 exp)"

        else:
            footer = (f"Level {'{:,}'.format(author['leveling'].get('level', 0))} "
                      f"({'{:,}'.format(author['leveling'].get('exp', 0))} exp)")
        embed.set_footer(text=footer, icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed, ephemeral=ephemeral(ctx))


def setup(bot):
    bot.add_cog(LevelingMain(bot))
