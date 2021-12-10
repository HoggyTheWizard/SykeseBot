from discord.commands import slash_command as slash, Option
from discord.ext import commands, tasks
from bot.utils.Checks.user_checks import is_verified
from variables import test_guilds
import datetime
from main import main_db
from config import host
import discord
import asyncio
import pytz

users = main_db["users"]


class birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_loop.start()

    @slash(description="Add your birthday so you get the birthday role on your birthday.", guild_ids=test_guilds)
    @is_verified()
    async def birthday(self, ctx, month: Option(int, "The month you were born (e.g. 04)"),
                       day: Option(int, "The day you were born (e.g. 24)"),
                       year: Option(int, "The year you were born (e.g. 2003)")):
        try:
            b_date = users.find_one({"id": ctx.author.id})["Birthday"]["date"]
            b_date_formatted = f"{b_date[0]}{b_date[1]}/{b_date[2]}{b_date[3]}"
            await ctx.respond(f"You've already set your birthday to {b_date_formatted}")
            return
        except:
            pass

        try:
            date = datetime.datetime(month=month, day=day, year=year)
            current_year = int(datetime.date.today().year)
            if int(year) > current_year:
                users.update_one({"id": ctx.author.id}, {"$set": {"Birthday.date": date.strftime("%m%d"),
                                                                "Birthday.year": year}})
            await ctx.respond(f"Successfully set your birthday to {month}/{day}/{year}")
        except:
            await ctx.respond("Invalid date provided!")

    @tasks.loop(seconds=60)
    async def birthday_loop(self):
        date = datetime.datetime.now(pytz.timezone("US/Eastern"))
        current_time = date.strftime("%H:%M")
        current_date = date.strftime("%m%d")
        if current_time != "0:00" and host != "main":  # for testing
            #guild = self.bot.get_guild(889697074491293736)
            #channel = guild.get_channel(890085670696124436)
            guild = self.bot.get_guild(707963219536248982)
            channel = guild.get_channel(708020912397484163)
            for user in users.find({}):
                if "Birthday" not in user or user["Birthday"].get("date", None) is None:
                    continue
                elif current_date == user["Birthday"]["date"]:
                    if guild.get_member(user.get("id", None)) is None:
                        continue
                    else:
                        member = guild.get_member(user["id"])
                        await channel.send(f"Happy Birthday to <@{member.id}>! Enjoy the birthday role "
                                           "for the next 24 hours.")
                        #await guild.get_member(user["id"]).add_roles(guild.get_role(911038229862563911))
            await asyncio.sleep(60)

    @birthday_loop.before_loop
    async def before_printer(self):
        print("Prepping birthday loop task...")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(birthday(bot))
