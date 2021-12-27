from discord.commands import slash_command as slash
from bot.utils.Leveling.leveling import LevelingMain as leveling
from bot.utils.Checks.user_checks import is_verified
from variables import guilds
from discord.ext import commands
from main import main_db
import random
import time
import discord
import config


users = main_db["users"]


class leveling_main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if config.host == "master":
            return
        elif not message.guild or message.guild.id not in [889697074491293736]:
            return
        elif message.author.bot:
            return
        elif message.type == discord.MessageType.application_command:
            return
        else:
            blacklisted_channels = [
                893934059804319775,  # verification
                893936274291974164,  # bots

            ]
            collection = users.find_one({"id": message.author.id})

            if collection is not None and message.channel.id not in blacklisted_channels:
                leveling_object = leveling.get_leveling(collection, users)
                current_exp = leveling_object.get("exp", 0)
                last_triggered_message = leveling_object.get("lastTriggeredMessage", None)

                # 90 represents the cooldown
                if last_triggered_message is None or last_triggered_message + 90 < int(time.time()):
                    added_exp = random.randint(15, 20)
                    users.update_one({"id": message.author.id}, {"$set":
                                     {"Leveling.exp": current_exp + added_exp,
                                      "Leveling.lastTriggeredMessage": int(time.time())}})
                    await leveling.levelup(self, message, collection, leveling_object, users)

    @slash(guild_ids=guilds)
    @is_verified()
    async def level(self, ctx, other_user: discord.User = None):

        if other_user is None:
            user = ctx.author
            user_type = "self"
        else:
            user = other_user
            user_type = "other"

        collection = users.find_one({"id": user.id})

        if "Leveling" not in collection:
            if user_type == "other":
                await ctx.respond(f"Could not find any leveling data for {str(user)}")
            elif user_type == "self":
                await ctx.respond(f"You don't have any leveling data tied to this account.")

        else:
            lvl = collection["Leveling"].get("level", 0)
            exp = collection["Leveling"].get("exp", 0)

            embed = discord.Embed(title=f"{str(user)}'s Level",
                                  description="Levels can be increased by chatting in the server.",
                                  color=ctx.author.color)
            embed.add_field(name="Level:", value="{:,}".format(lvl), inline=False)
            embed.add_field(name="Total Experience:", value="{:,}".format(exp), inline=False)
            embed.add_field(name="XP To Next Level:",
                            value="{:,}".format(5 * (lvl ** 2) + (50 * lvl) + 100 - exp), inline=False)
            embed.set_footer(text="Have a nice day!", icon_url=ctx.guild.icon.url)
            await ctx.respond(embed=embed)

    @slash(guild_ids=guilds, description="A leaderboard displaying the top exp earners in our server.")
    async def level_leaderboard(self, ctx):
        embed = discord.Embed(title="Level Leaderboard",
                              description="A leaderboard displaying the top exp earners in our server.",
                              color=ctx.author.color)

        lb = users.find({}).sort("Leveling.exp", -1)
        i = 0
        for user in lb:
            if "Leveling" not in user:
                continue
            else:
                i += 1
                embed.add_field(name=f"#{i}",
                                value=f"<@{user['id']}> | Level {user['Leveling'].get('level', 0)} "
                                      f"({'{:,}'.format(user['Leveling'].get('exp', 0))} exp)", inline=False)
            if i == 15:
                break

        author = users.find_one({"id": ctx.author.id})

        if author is None:
            footer = "Level 0 (0 exp)"

        elif author.get("Leveling", None) is None:
            footer = "Level 0 (0 exp)"

        else:
            footer = (f"Level {'{:,}'.format(author['Leveling'].get('level', 0))} "
                      f"({'{:,}'.format(author['Leveling'].get('exp', 0))} exp)")
        embed.set_footer(text=footer, icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(leveling_main(bot))
