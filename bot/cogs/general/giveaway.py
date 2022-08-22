from discord.ext import commands
from discord.commands import SlashCommandGroup, Option, OptionChoice
from bot.utils.checks.user import mod
from bot.utils.ui.confirm import Confirm
from bot.utils.ui.utils import disable_buttons
from datetime import datetime, timedelta
from db import main_db
import bot.variables as v
import discord

giveaways = main_db["giveaways"]
users = main_db["users"]
requirement_types = {
    "none": "- No Requirements",
    "level": "-Bot Level 5",
    "recent": "-Recent Activity (100 messages in the last week)",
    "level_and_recent": "- Bot Level 5\n- Recent Activity (100 messages in the last week)",

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
                         OptionChoice("Level Requirement (5)", "level"),
                         OptionChoice("Recent Activity (100 messages in the last week)", "recent"),
                         OptionChoice("Level Requirement  & Recent Activity", "level_and_recent")
                     ]),
                     days: Option(int, "How many days this giveaway will last.", required=False),
                     hours: Option(int, "How many hours this giveaway will last.", required=False),
                     winners: Option(int, "How many winners there will be", required=False, default=1),
                     ):
        if not days and not hours:
            await ctx.respond("You must specify how long this giveaway will last.", ephemeral=True)
            return

        end = datetime.now() + timedelta(days=days, hours=hours)

        confirm_embed = discord.Embed(title="Giveaway Confirmation",
                                      description="Please verify that the information below is correct. If it's not, "
                                                  "run the command again.")
        confirm_embed.add_field(name="Prize", value=prize, inline=False)
        confirm_embed.add_field(name="Winners", value=str(winners), inline=False)
        confirm_embed.add_field(name="End Date", value=f"<t:{int(end.timestamp())}> (<t:{int(end.timestamp())}:R>)")

        view = Confirm()
        view.interaction = ctx.interaction
        await ctx.respond(embed=confirm_embed, view=view)
        await view.wait()
        await disable_buttons(view)

        if not view.value:
            await ctx.send("Cancelled giveaway")
            return

        giveaway_id = f"giveaways:{giveaways.find_one({'id': 'config'})['totalGiveaways'] + 1}"

        embed = discord.Embed(title=prize,
                              description=f"Requirements to enter:\n {requirement}")
        embed.add_field(name="Total Winners", value=str(winners), inline=False)
        embed.add_field(name="End Date", value=f"<t:{int(end.timestamp())}> (<t:{int(end.timestamp())}:R>)")
        embed.set_footer(text=f"Giveaway ID: {giveaway_id}")

        message = await ctx.get_channel(v.giveaways).send(embed=embed)
        giveaways.insert_one({
            "id": giveaway_id, "timestamp": int(end.timestamp()), "requirements": requirement,
            "message": message.id, "active": True
        })
        giveaways.update_one(
            {"id": "config"}, {"$inc": {"totalGiveaways": 1}}
        )
        await ctx.send(f"Giveaway created. ID: {giveaway_id}")


def setup(bot):
    bot.add_cog(Giveaway(bot))
