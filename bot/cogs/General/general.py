from discord.ext import commands
from bot.utils.Misc.general import get_mojang_from_uuid
from bot.utils.Checks.channel_checks import channel_restricted
from bot.utils.Checks.user_checks import is_verified
from main import main_db
import discord
users = main_db["users"]


class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Displays the ping of the bot.")
    @channel_restricted(users=users)
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong ({round(self.bot.latency*1000)}ms)")

    @commands.command(description="Displays the account a user is linked to.")
    @channel_restricted(users=users)
    @is_verified(users=users)
    async def profile(self, ctx, member: discord.Member = None):
        if member is None:
            user = ctx.author
            account_type = "self"
        else:
            user = member
            account_type = "other"

        collection = users.find_one({"id": user.id})

        if account_type == "other" and collection.get("publicProfile", True) is False \
                and collection.get("isStaff", False) is False:

            await ctx.send("This user has indicated that they do not want their linked account to be public. "
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
            await ctx.send(embed=embed)
        else:
            await ctx.send("Couldn't find any data for this user.")

    @commands.command(description="Toggle whether or not your Minecraft account is publicly shown.")
    @channel_restricted(users=users)
    @is_verified(users=users)
    async def toggleprofile(self, ctx):
        user = users.find_one({"id": ctx.author.id})
        if user.get("publicProfile", True) is True:
            new_setting = False
        elif user.get("publicProfile") is False:
            new_setting = True
        else:
            new_setting = True
        users.update_one({"id": ctx.author.id}, {"$set": {"publicProfile": new_setting}})
        await ctx.send(f"Successfully set your public profile status to `{new_setting}`")


def setup(bot):
    bot.add_cog(general(bot))
