from discord.commands import slash_command as slash, Option
from bot.utils.leveling.leveling import get_leveling
from bot.utils.checks.channel import ephemeral
from bot.utils.misc.requests import mojang
from bot.utils.checks.user import verified
from discord.ext import commands
from datetime import datetime
from db import main_db
import bot.variables as v
import discord

users = main_db["users"]
# To prevent unnecessary API calls, the bot will only update a skin every hour
cached_profile = {}


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(description="View the server profile of you or another member.", guild_ids=v.guilds)
    @verified()
    async def profile(self, ctx, member: Option(discord.Member, "The member you want to view the profile of.",
                                                required=False)):

        member = ctx.author if not member else member
        doc = users.find_one({"id": member.id if member.id else 0})

        if not member or not doc:
            await ctx.respond("Couldn't find any data for this member.", ephemeral=True)
            return

        lock = [x.id for x in member.roles if x.id == v.sync_lock_id]
        if len(lock):
            m = await mojang(doc["uuid"])
            name = m["name"]
        else:
            name = member.nick if member.nick else member.name

        leveling = get_leveling(doc)
        cached_member = cached_profile.get(member.id)

        if cached_member:
            if int(datetime.now().timestamp()) - cached_member.get("timestamp") >= 3600:
                skin = f"https://crafatar.com/renders/head/{doc['uuid']}?overlay=true"
                cached_profile[member.id]["skin"] = skin
                cached_profile[member.id]["timestamp"] = int(datetime.now().timestamp())
            else:
                skin = cached_profile[member.id]["skin"]
        else:
            skin = f"https://crafatar.com/renders/head/{doc['uuid']}?overlay=true"

        embed = discord.Embed(title=f"{str(name)}'s Profile", color=member.color)
        embed.set_thumbnail(url=skin)
        embed.add_field(name="Linked Account:", value=f"{name}", inline=False)
        embed.add_field(name="Level:", value=leveling["level"], inline=True)
        embed.add_field(name="Total EXP:", value=leveling["exp"], inline=True)
        embed.add_field(name="Needed EXP:",
                        value=(5 * (leveling["level"] ** 2) + 50 * leveling["level"] + 100) -
                        leveling["expGainedSinceLevelup"], inline=True)

        await ctx.respond(embed=embed, ephemeral=ephemeral(ctx))
        if "Notifications" not in doc or doc["Notifications"].get("levelFixUpdate", False) is False:
            await ctx.respond("The way levels are calculated has been changed due to a bug found within the original "
                              "code. You can read about this change in <#890085670696124436>. This message will not "
                              "appear again.", ephemeral=True)
            users.update_one({"id": member.id}, {"$set": {"Notifications.levelFixUpdate": True}})


def setup(bot):
    bot.add_cog(Profile(bot))
