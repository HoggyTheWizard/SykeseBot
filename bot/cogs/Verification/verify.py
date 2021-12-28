from discord.ext import commands
from discord.commands import slash_command as slash
from variables import guilds
from main import main_db
from bot.utils.Misc.general import aiohttp_json, get_mojang_from_username
from bot.utils.Checks.channel_checks import channel_restricted
from bot.utils.Checks.user_checks import perms
from variables import verified_role_id, unverified_role_id
from datetime import datetime
import discord
import config


users = main_db["users"]


class verify_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(description="Links a Minecraft account to your Discord account.", guild_ids=guilds)
    @commands.guild_only()
    @channel_restricted()
    async def verify(self, ctx, username):
        if users.find_one({"id": ctx.author.id}):
            await ctx.respond("You're already verified to the account "
                           f"`{users.find_one({'id' : ctx.author.id}).get('uuid', 'ERROR')}`")
        else:
            mojang = await get_mojang_from_username(username=username)
            player = await aiohttp_json(endpoint="player", attribute=mojang["id"])

            try:
                discord_account = player["player"]["socialMedia"]["links"]["DISCORD"]
            except:
                await ctx.respond("You need to link your Discord account to Hypixel! If you're unsure of how to do "
                                  "this, please view the gif below.\nhttps://imgur.com/2ZRQzEC.gif")
                return

            if str(ctx.author) != discord_account:
                if "discord.gg/" in discord_account:
                    account = "Blocked linked account due to it being an invite link."
                else:
                    account = discord_account
                await ctx.respond(f"Your accounts don't match!\n\nYour Account: {str(ctx.author)}\n"
                               f"Linked Account: {account}\n\nYou either need to change your current account to match "
                               "your linked account or update your linked account.")

            elif str(ctx.author) == player["player"]["socialMedia"]["links"]["DISCORD"]:
                await ctx.author.add_roles(ctx.guild.get_role(verified_role_id))
                users.insert_one({"id": ctx.author.id, "uuid": mojang["id"],
                                  "verifiedAt": datetime.timestamp(datetime.now())})
                await ctx.respond("Successfully verified!")

                try:
                    await ctx.author.remove_roles(ctx.guild.get_role(unverified_role_id))
                except:
                    pass
            else:
                await ctx.respond("An unexpected error has occurred.")

    @commands.command(hidden=True)
    @commands.guild_only()
    @channel_restricted()
    @perms(["staff.forceVerify"])
    async def forceverify(self, ctx, discord_user: discord.Member, username):
        if users.find_one({"id": discord_user.id}):
            await ctx.send("This user is already verified to the account "
                           f"`{users.find_one({'uuid': discord_user.id}).get('uuid', 'ERROR')}`")
        else:
            mojang = await get_mojang_from_username(username=username)
            await discord_user.add_roles(ctx.guild.get_role(verified_role_id))
            users.insert_one({"id": discord_user.id, "uuid": mojang["id"],
                              "verifiedAt": datetime.timestamp(datetime.now()), "verifiedBy": ctx.author.id})
            await ctx.send(f"Successfully verified `{str(discord_user)}` as `{mojang['name']}`")
            try:
                await discord_user.remove_roles(ctx.guild.get_role(unverified_role_id))
            except:
                pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id in [889697074491293736] and config.host == "master":
            if users.find_one({"id": member.id}) is not None:
                await member.add_roles(member.guild.get_role(verified_role_id))
                try:
                    await member.send("Welcome back! Because you previously verified, you have automatically received "
                                      "your roles.")
                except:
                    return
            else:
                embed = discord.Embed(title="Welcome to Sykese's Discord Server!",
                                      description="Make sure to read the below information to continue into the "
                                                  "server.",
                                      color=discord.Color.blue())

                embed.add_field(name="Verification",
                                value="We use a Hypixel based verification system. To verify, please "
                                      "use the command `/verify <minecraft username>`. If you're unsure of how to link "
                                      "your account, please view the gif pinned in <#893934059804319775>.",
                                inline=False)

                embed.add_field(name="Rules & Information",
                                value="Our server rules can be found in <#892118771257458738>. "
                                      "By joining our server, you agree to follow these rules. You can also find "
                                      "important information regarding the server and roles in this channel.",
                                inline=False)

                embed.add_field(name="Notification Roles", value="Once you verify, you'll get access to "
                                "<#892208575273922581>. In this channel, you can choose selfroles that allow you to "
                                "be notified for certain events, such as when Sykese uploads a video to his channel. "
                                "These are completely optional, however we recommend that you enable them.",
                                inline=False)

                embed.set_footer(icon_url=member.guild.icon.url, text="Hope to see you around!")
                try:
                    await member.send(embed=embed)
                except:
                    return

def setup(bot):
    bot.add_cog(verify_commands(bot))
