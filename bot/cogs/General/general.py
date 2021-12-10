from discord.ext import commands
from discord.commands import slash_command as slash, Option
from variables import test_guilds
from bot.utils.Misc.general import get_mojang_from_uuid
from bot.utils.Checks.channel_checks import channel_restricted
from bot.utils.Checks.user_checks import is_verified, check_perms
from main import main_db
import discord

users = main_db["users"]


class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(description="Displays the ping of the bot.", guild_ids=test_guilds)
    @channel_restricted()
    async def ping(self, ctx):
        await ctx.respond(f"🏓 Pong ({round(self.bot.latency * 1000)}ms)")

    @slash(description="Displays the account a user is linked to.", guild_ids=test_guilds)
    @channel_restricted()
    @is_verified()
    async def profile(self, ctx, member: Option(discord.Member, "The user you want to view the profile of.") = None):
        if member is None:
            user = ctx.author
            account_type = "self"
        else:
            user = member
            account_type = "other"

        collection = users.find_one({"id": user.id})

        if account_type == "other" and collection.get("publicProfile", True) is False and \
                check_perms(ctx.author, ["staff.viewPrivateProfile"]) is False:

            await ctx.respond("This user has indicated that they do not want their linked account to be public. "
                              "As such, this information is only available to server staff.")
        elif collection is not None:
            mojang = await get_mojang_from_uuid(uuid=collection["uuid"])
            if mojang is None:
                username = "Couldn't fetch a username for this user."
            else:
                username = mojang["name"]

            embed = discord.Embed(title=f"{str(user)}'s Profile", color=discord.Color.blue())
            embed.add_field(name="Linked Account:", value=username, inline=False)
            embed.add_field(name="UUID:", value=collection["uuid"], inline=False)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("Couldn't find any data for this user.")

    @slash(description="Toggle whether or not your Minecraft account is publicly shown.", guild_ids=test_guilds)
    @channel_restricted()
    @is_verified()
    async def toggleprofile(self, ctx):
        user = users.find_one({"id": ctx.author.id})
        if user.get("publicProfile", True) is True:
            new_setting = False
        elif user.get("publicProfile") is False:
            new_setting = True
        else:
            new_setting = True
        users.update_one({"id": ctx.author.id}, {"$set": {"publicProfile": new_setting}})
        await ctx.respond(f"Successfully set your public profile status to `{new_setting}`")


def setup(bot):
    bot.add_cog(general(bot))
