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
    @commands.guild_only()
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
                    account = discord_account
                await ctx.send(f"Your accounts don't match!\n\nYour Account: {str(ctx.message.author)}\n"
                               f"Linked Account: {account}")

            elif str(ctx.author) == player["player"]["socialMedia"]["links"]["DISCORD"]:
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
        else:
            embed = discord.Embed(title="Welcome to Sykese's Discord Server!",
                                  description="Make sure to read the below information to continue into the server.",
                                  color=discord.Color.blue())
            embed.add_field(name="Verification", value="We use a Hypixel based verification system. To verify, please "
                            "use the command `/verify <minecraft username>`. If you're unsure of how to link your "
                            "account, please view the gif pinned in {CHANNEL}.", inline=False)
            embed.add_field(name="Rules & Information", value="Our server rules can be found in <#892118771257458738>. "
                            "By joining our server, you agree to follow these rules. You can also find important "
                            "information regarding the server and roles in this channel.", inline=False)
            embed.add_field(name="Notification Roles", value="Once you verify, you'll get access to "
                            "<#892208575273922581>. In this channel, you can choose selfroles that allow you to "
                            "be notified for certain events, such as when Sykese uploads a video to his channel. "
                            "These are completely optional, however we recommend that you enable them.", inline=False)
            embed.set_footer(icon_url=member.guild.icon_url, text="Hope to see you around!")
            try:
                member.send(embed=embed)
            except:
                return

def setup(bot):
    bot.add_cog(verify_commands(bot))
