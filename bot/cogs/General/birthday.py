from discord.commands import slash_command as slash, Option
from discord.ext import commands
from bot.utils.Checks.user_checks import is_verified
from variables import test_guilds
from main import main_db
import datetime
from main import main_db
from config import host
import discord

users = main_db["users"]


class birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(description="Add your birthday so you get the birthday role on your birthday.", guild_ids=test_guilds)
    @is_verified(users=users)
    async def birthday(self, ctx, month: Option(int, "The day you were born"),
                       day: Option(int, "The month you were born, in the form of a number"),
                       year: Option(int, "The year you were born")):
        try:
            date = datetime.datetime(month=month, day=day, year=year)
            users.update_one({"id": ctx.author.id}, {"$set": {"Birthday.date": date.strftime("%m%d"),
                                                              "Birthday.year": year}})
            await ctx.respond(f"Successfully set your birthday to {month}/{day}/{year}")
        except:
            await ctx.respond("Invalid date provided!")

def setup(bot):
    bot.add_cog(birthday(bot))
