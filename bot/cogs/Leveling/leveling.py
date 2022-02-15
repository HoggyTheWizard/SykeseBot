from discord.commands import slash_command as slash
from bot.utils.Leveling.leveling import LevelingMain as leveling
from bot.utils.Checks.user import is_verified
from bot.variables import guilds
from discord.ext import commands, tasks
from db import main_db
from datetime import datetime
import random
import time
import discord
import config
import pytz

users = main_db["users"]
blacklisted_channels = [
                893934059804319775,  # verification
                893936274291974164  # bots
            ]


class leveling_main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.vc_exp.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if config.host != "master":
            return
        elif not message.guild or message.guild.id not in [889697074491293736]:
            return
        elif message.author.bot:
            return
        elif message.type == discord.MessageType.application_command:
            return
        else:
            collection = users.find_one({"id": message.author.id})

            if collection is not None and message.channel.id not in blacklisted_channels:
                leveling_object = leveling.get_leveling(collection, users)
                current_exp = leveling_object.get("exp", 0)
                last_triggered_message = leveling_object.get("lastTriggeredMessage", None)

                # 90 represents the cooldown
                if last_triggered_message is None or last_triggered_message + 90 < int(time.time()) or \
                        leveling_object.get("expBlacklist", False) is False:
                    added_exp = random.randint(15, 20)
                    users.update_one({"id": message.author.id}, {"$set":
                                     {"Leveling.exp": current_exp + added_exp,
                                      "Leveling.lastTriggeredMessage": int(time.time())}})
                    await leveling.levelup(message.guild, users, collection, leveling_object, message.author, message)

    @tasks.loop(seconds=90)
    async def vc_exp(self):
        if config.host != "master":
            return

        if datetime.now(pytz.timezone("US/Eastern")).strftime('%H:%M') == "01:00":
            for user in users.find({"Leveling.dailyVCExp": {"$exists": True}}):
                users.update_one({"id": user["id"]}, {"$set": {"Leveling.dailyVCExp": 0}})

        guild = self.bot.get_guild(guilds[0])
        for vc in guild.voice_channels:
            if vc.id in blacklisted_channels:
                continue
            else:
                states = vc.voice_states
                for member in vc.members:

                    if states[member.id].self_mute or states[member.id].self_deaf:
                        continue

                    collection = users.find_one({"id": member.id})
                    if collection is not None:
                        leveling_object = leveling.get_leveling(collection, users)
                        if leveling_object.get("dailyVCExp", 0) >= 150 or \
                                leveling_object.get("expBlacklist", False) is True:
                            continue
                        current_exp = leveling_object.get("exp", 0)
                        added_exp = random.randint(2, 6)
                        users.update_one({"id": member.id}, {"$set":
                                         {"Leveling.exp": current_exp + added_exp, "Leveling.dailyVCExp":
                                             leveling_object.get("dailyVCExp", 0) + added_exp}})
                        await leveling.levelup(guild, users, collection, leveling_object, member)

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

        if collection is None or "Leveling" not in collection:
            if user_type == "other":
                await ctx.respond(f"Could not find any leveling data for {str(user)}")
            elif user_type == "self":
                await ctx.respond(f"You don't have any leveling data tied to this account.")

        else:
            lvl = collection["Leveling"].get("level", 0)
            exp = collection["Leveling"].get("exp", 0)
            calculated_needed_xp = (5 * (lvl ** 2) + (50 * lvl) + 100 - exp)
            if calculated_needed_xp < 0:
                xp_needed = 1
            else:
                xp_needed = "{:,}".format(calculated_needed_xp)

            embed = discord.Embed(title=f"{str(user)}'s Level",
                                  description="Levels can be increased by chatting in the server or talking in a voice "
                                              "channel.",
                                  color=ctx.author.color)
            embed.add_field(name="Level:", value="{:,}".format(lvl), inline=False)
            embed.add_field(name="Total Experience:", value="{:,}".format(exp), inline=False)
            embed.add_field(name="XP To Next Level:",
                            value=xp_needed, inline=False)
            embed.set_footer(text="The way levels are calculated has been changed - you did not lose exp.",
                             icon_url=ctx.guild.icon.url)
            await ctx.respond(embed=embed)

    @slash(guild_ids=guilds, description="A leaderboard displaying the top exp earners in our server.")
    async def level_leaderboard(self, ctx):
        embed = discord.Embed(title="Level Leaderboard",
                              description="A leaderboard displaying the top exp earners in our server. "
                                          "The way levels are calculated has been changed - you did not lose exp.",
                              color=ctx.author.color)
        id_list = []
        for member in ctx.guild.members:
            id_list.append(member.id)

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

    @vc_exp.before_loop
    async def before_printer(self):
        print("Prepping vc leveling task...")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(leveling_main(bot))
