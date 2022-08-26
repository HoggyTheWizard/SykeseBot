from discord.ext import commands
from discord.commands import SlashCommandGroup, Option, OptionChoice
from bot.utils.checks.user import mod
from bot.utils.ui.confirm import Confirm
from bot.utils.ui.giveaways import GiveawayButton, auto_enroll
from bot.cogs.tasks.end_giveaways import end_giveaway
from bot.utils.ui.utils import disable_buttons
from datetime import datetime, timedelta
from db import main_db
import bot.variables as v
import discord

giveaways = main_db["giveaways"]
users = main_db["users"]

# Eventually I want to add a recent message requirement, however the initial version of this will only include user
# level as it's quite easy to implement.
requirement_types = {
    "none": "- No Requirements",
    "level_5": "- Bot Level 5",

}


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    giveaway = SlashCommandGroup("giveaway", "Create a giveaway.", guild_ids=v.guilds)

    @giveaway.command(guild_ids=v.guilds, description="Create a giveaway.")
    @mod()
    async def create(self, ctx,
                     prize: Option(str, "The thing you're giving away."),
                     requirement: Option(str, "The requirements for this giveaway", choices=[
                         OptionChoice("None", "none"),
                         OptionChoice("Level Requirement (5)", "level_5"),
                     ]),
                     days: Option(int, "How many days this giveaway will last.", required=False, default=0,
                                  min_value=1),
                     hours: Option(int, "How many hours this giveaway will last.", required=False, default=0,
                                   min_value=1),
                     winners: Option(int, "How many winners there will be", required=False, default=1),
                     ):
        if sum([days, hours]) == 0:
            await ctx.respond("You must specify how long this giveaway will last.", ephemeral=True)
            return

        end = datetime.now() + timedelta(days=days, hours=hours)

        confirm_embed = discord.Embed(title="Giveaway Confirmation",
                                      description="Please verify that the information below is correct. If it's not, "
                                                  "run the command again.",
                                      color=discord.Color.orange())
        confirm_embed.add_field(name="Prize", value=prize, inline=False)
        confirm_embed.add_field(name="Winners", value=str(winners), inline=False)
        confirm_embed.add_field(name="End Date", value=f"<t:{int(end.timestamp())}> (<t:{int(end.timestamp())}:R>)")

        view = Confirm()
        view.interaction = ctx.interaction
        await ctx.respond(embed=confirm_embed, view=view, ephemeral=True)
        await view.wait()
        await disable_buttons(view)

        if not view.value:
            await ctx.send("Cancelled giveaway")
            view.stop()
            return

        view.stop()
        giveaway_id = f"giveaways:{giveaways.find_one({'id': 'config'})['totalGiveaways'] + 1}"

        embed = discord.Embed(title=f"Giveaway - {prize}",
                              description=f"Requirements to enter:\n "
                                          f"{requirement_types.get(requirement, 'Error Loading Requirements')}",
                              color=discord.Color.green())
        embed.add_field(name="Total Winners", value=str(winners), inline=False)
        embed.add_field(name="End Date", value=f"<t:{int(end.timestamp())}> (<t:{int(end.timestamp())}:R>)")
        embed.set_footer(text=f"Giveaway ID: {giveaway_id}")
        channel = ctx.guild.get_channel(v.giveaways)
        message = await channel.send("Creating giveaway...")
        enter = discord.ui.View(timeout=None)
        payload = {
            "id": giveaway_id, "participants": auto_enroll(ctx), "timestamp": int(end.timestamp()),
            "requirements": requirement, "message": message.id, "totalWinners": winners, "active": True
        }
        enter.add_item(GiveawayButton(giveaway=payload))
        await message.edit(content="", embed=embed, view=enter),
        await channel.send(f"<@&{v.giveaway_role}>")
        giveaways.insert_one(payload)
        giveaways.update_one(
            {"id": "config"}, {"$inc": {"totalGiveaways": 1}}
        )
        await ctx.respond(f"Giveaway created. ID: {giveaway_id}", ephemeral=True)

    @giveaway.command(guild_ids=v.guilds, description="Reroll the winner(s) of a giveaway.")
    @mod()
    async def reroll(self, ctx, giveaway_id: Option(int, "The giveaway ID (just the number)", min_value=1)):
        giveaway = giveaways.find_one({"id": f"giveaways:{giveaway_id}"})
        if not giveaway:
            await ctx.respond("Giveaway not found.", ephemeral=True)

        elif giveaway["active"]:
            await ctx.respond("The giveaway is still active... are you sure this is the one you want to reroll?",
                              ephemeral=True)

        else:
            view = Confirm()
            view.interaction = ctx.interaction
            await ctx.respond(f"Are you sure you want to reroll the winner(s) of giveaway {giveaway_id}?", view=view,
                              ephemeral=True)
            await view.wait()
            view.stop()

            if view.value:
                message = await ctx.respond("Rerolling...", ephemeral=True)
                await end_giveaway(self, giveaway)
                await message.edit(content="Finished!")
            else:
                await ctx.respond("Cancelled reroll.", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        view = discord.ui.View(timeout=None)
        active = giveaways.find({"active": True})

        for doc in active:
            view.add_item(GiveawayButton(giveaway=doc))
            self.bot.add_view(view)


def setup(bot):
    bot.add_cog(Giveaway(bot))
