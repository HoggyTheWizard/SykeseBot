from discord.ext import commands, tasks
from datetime import datetime
from asyncio import sleep
from db import main_db
import bot.variables as v
from random import choice
import logging
import discord

giveaways = main_db["giveaways"]
users = main_db["users"]


class EndGiveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.end_giveaways.start()

    @tasks.loop(seconds=60)
    async def end_giveaways(self):
        guild = self.bot.get_guild(v.guilds[0])
        for giveaway in giveaways.find({"active": True}):
            if giveaway["timestamp"] <= int(datetime.now().timestamp()):
                winners = pick_winner(guild, giveaway["participants"], winners=giveaway["totalWinners"])
                if not len(winners):
                    await guild.get_channel(giveaway).send(f"No one entered the giveaway. Very sad. :(")
                    return
                await end_giveaway(self, giveaway)

    @end_giveaways.before_loop
    async def before_end_giveaways(self):
        print("Prepping giveaways...")
        await self.bot.wait_until_ready()

    @end_giveaways.error
    async def end_giveaways_error(self, error):
        logging.getLogger(__name__).error("", exc_info=error)
        await sleep(60)
        self.end_giveaways.start()


def pick_winner(guild: discord.Guild, participants: list, winners: int = 1):
    winner_list = []
    if winners > len(participants):
        return []

    while winners > 0:
        winner = choice(participants)
        member = guild.get_member(winner)

        if not member:
            participants.remove(winner)
            winners -= 1
            pick_winner(guild, participants)

        else:
            winner_list.append(member)
            participants.remove(winner)
            winners -= 1

    return winner_list


async def end_giveaway(self, giveaway: dict):
    guild = self.bot.get_guild(v.guilds[0])
    participants = giveaway["participants"]
    participants = [x for x in participants if x not in giveaway["winners"]]
    winners = pick_winner(guild, participants, winners=giveaway["totalWinners"])
    giveaways.update_one(
        {"id": giveaway["id"]}, {"$set": {"active": False, "winners": [winner.id for winner in winners]}}
    )

    try:
        message = await guild.get_channel(v.giveaways).fetch_message(giveaway["message"])
    except:
        await guild.get_channel(v.bot_logs).send(f"Couldn't find a giveaway message for giveaway "
                                                 f"`{giveaway['id']}`. If this is intentional, "
                                                 f"ignore this message.")
        return

    embed = message.embeds[0]
    embed.color = discord.Color.red()
    embed.set_footer(text=f"{winners[0].display_name if len(winners) == 1 else f'{len(winners)} people'} "
                          f"won the giveaway!")
    view = discord.ui.View.from_message(message)
    view.disable_all_items()
    await message.edit(embed=embed, view=view)
    pings = ""
    for winner in winners:
        pings += f"{winner.mention} "

    await message.reply(f"Congratulations to {pings}for winning the giveaway! Please contact the host for "
                        f"more info.")


def setup(bot):
    bot.add_cog(EndGiveaways(bot))
