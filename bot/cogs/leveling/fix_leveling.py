from bot.cogs.leveling.leveling import *
from bot.utils.checks.user import manager
from db import main_db
import discord
from pprint import pprint

users = main_db["users"]


class FixLeveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @manager()
    async def fix_leveling(self, ctx):
        await ctx.send("Leveling task started (this may take a while)")
        channels = []
        for channel in ctx.guild.channels:
            if channel.type == discord.ChannelType.text and channel.id not in blacklisted_channels:
                channels.append(channel)

        await ctx.send("Successfully gathered all channels. Starting iteration...")

        data = {}
        for channel in channels:
            await ctx.send(f"Iterating through {channel.name} ({channel.id})")
            messages = await channel.history(limit=None).flatten()
            for message in messages:
                if message.author.bot:
                    continue
                else:
                    if message.author.id in data:
                        data[message.author.id]["messages"] += 1
                    else:
                        data[message.author.id] = {
                            "messages": 1,
                            "level": 1,
                            "exp": 0
                        }

        await ctx.send("Finished all iteration. An array of message counts has been printed to the console. "
                       "Now converting to leveling...")

        for user in data:
            count = data[user]["messages"]
            exp = 0
            lvl = 1

            while count > 0:
                exp += random.randint(15, 20)
                count -= 1

            exp_left = exp
            while exp_left >= 5 * lvl ** 2 + 50 * lvl + 100 - exp_left:
                exp_left -= 5 * lvl ** 2 + 50 * lvl + 100
                lvl += 1

            data[user]["level"] = lvl
            data[user]["exp"] = exp
        pprint(data)
        # save legacyLevel key
        # update_many
        # add/remove necessary roles


def setup(bot):
    bot.add_cog(FixLeveling(bot))
