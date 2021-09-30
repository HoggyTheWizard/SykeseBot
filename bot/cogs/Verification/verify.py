from discord.ext import commands
from main import main_db
from bot.utils.Misc.general import aiohttp_json, get_mojang_from_username
from variables import verified_role_id
from datetime import datetime
import discord
users = main_db["users"]


class verify_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Links a Minecraft account to your Discord account.")
    async def verify(self, ctx, username):
        if users.find_one({"id": ctx.author.id}):
            await ctx.send("You're already verified to the account "
                           f"`{users.find_one({'id': ctx.author.id}).get('uuid', 'ERROR')}`")
        else:
            mojang = await get_mojang_from_username(username=username)
            player = await aiohttp_json(endpoint="player", attribute=mojang["id"])

            try:
                discord_account = player["player"]["socialMedia"]["links"]["DISCORD"]
            except:
                await ctx.send("You need to link your Discord account to Hypixel! If you're unsure of how to do this, "
                               "please view the gif below.\nhttps://imgur.com/2ZRQzEC.gif")
                return

            if str(ctx.author) != discord_account:
                if "discord.gg/" in discord_account:
                    account = "Blocked linked account due to it being an invite link."
                else:
                    account = discord
                await ctx.send(f"Your accounts don't match!\n\nYour Account: {str(ctx.message.author)}\n"
                               f"Linked Account: {account}")

            elif str(ctx.message.author) == player["player"]["socialMedia"]["links"]["DISCORD"]:
                await ctx.author.add_roles(ctx.guild.get_role(verified_role_id))
                users.insert_one({"id": ctx.author.id, "uuid": mojang["id"],
                                  "verifiedAt": datetime.timestamp(datetime.now())})
                await ctx.send("Successfully verified!")
            else:
                await ctx.send("An unexpected error has occurred.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if users.find_one({"id": member.id}) is not None:
            await member.add_roles(member.guild.get_role(verified_role_id))
            try:
                await member.send("Welcome back! Because you previously verified, you have automatically received your "
                                  "roles.")
            except:
                return

def setup(bot):
    bot.add_cog(verify_commands(bot))