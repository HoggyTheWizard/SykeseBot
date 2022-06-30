from discord.ext import commands
from discord.commands import slash_command as slash
from bot.variables import guilds
from db import main_db
from bot.utils.misc.requests import player
from bot.utils.hypixel.player import Player
from bot.variables import verified_role_id
from datetime import datetime
import discord
import config

users = main_db["users"]


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(description="Links a Minecraft account to your Discord account.", guild_ids=guilds)
    async def verify(self, ctx, username):
        doc = users.find_one({"id": ctx.author.id})
        if doc:
            name = ctx.author.nick if ctx.author.nick else ctx.author.name
            await ctx.respond(f"You're already verified to `{name}` "
                              f"({doc.get('uuid', 'There was an error getting your UUID')})")
        else:
            p = await player(name=username)
            obj = Player(player=p)

            if not p:
                await ctx.respond("Couldn't find any data regarding that account. There are two reasons why this error "
                                  "may have been triggered:\n1. The Minecraft username you entered may be invalid. Are "
                                  f"you sure `{username}` is your current __Minecraft__ username?\n2."
                                  f" The account you have chosen has never logged on to Hypixel.")
                return

            try:
                discord_account = p["player"]["socialMedia"]["links"]["DISCORD"]
            except KeyError:
                await ctx.respond("You need to link your Discord account to Hypixel! If you're unsure of how to do "
                                  "this, please view the gif below.\nhttps://imgur.com/2ZRQzEC.gif")
                return

            if str(ctx.author) != discord_account:
                account = discord_account if "discord.gg" not in discord_account else \
                    "Blocked linked account due to it being an invite link."
                await ctx.respond(f"Your accounts don't match!\n\nYour Account: {str(ctx.author)}\n"
                                  f"Linked Account: {account}\n\nYou either need to change your current account to "
                                  f"match your linked account or update your linked account.")

            elif str(ctx.author) == p["player"]["socialMedia"]["links"]["DISCORD"]:
                await ctx.author.add_roles(
                    ctx.guild.get_role(verified_role_id),
                    ctx.guild.get_role(obj.level()[1]),
                    ctx.guild.get_role(obj.rank()["role"])
                )

                users.insert_one({"id": ctx.author.id, "uuid": p["player"]["uuid"],
                                  "verifiedAt": datetime.timestamp(datetime.now())})

                embed = discord.Embed(title="Verification Successful!",
                                      description=f"Thank you for verifying your account in the {ctx.guild.name} "
                                                  f"server! Below is some helpful information to help you get started "
                                                  f"in our server.",
                                      color=discord.Color.blue())
                embed.add_field(name="Rules & Information",
                                value="Our server rules can be found in <#892118771257458738>. "
                                      "By joining our server, you agree to follow these rules. If you see"
                                      "a member breaking our rules, please use the `/report` command so that it can"
                                      "be handled by our moderation team.",
                                inline=False)

                embed.add_field(name="Notification Roles",
                                value="To assign roles to yourself, head over to <#892208575273922581>. This will "
                                      "allow you be notified of certain events, such as when Sykese uploads a video "
                                      "to his channel or starts streaming. These are optional, however we recommend "
                                      "that you enable them.",
                                inline=False)

                embed.add_field(name="Suggestions and Feedback",
                                value="Have any suggestions regarding our server or Sykese's channel? Head over to our "
                                      "Suggestions and Feedback category to voice your opinions. Make sure to keep "
                                      "your opinions constructive; all feedback is welcome if voiced in a respectful "
                                      "and constructive manner.",
                                inline=False)

                embed.set_footer(icon_url=ctx.guild.icon.url, text="Have a good day!")
                try:
                    await ctx.author.send(embed=embed)
                except:
                    return

                await ctx.respond("Successfully verified!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id in guilds and config.host == "master":
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
                                      "use the command `/verify <minecraft username>` in the <#893934059804319775> "
                                      "channel. If you're unsure of how to link your account, please view the pinned "
                                      "gif",
                                inline=False)

                embed.set_footer(icon_url=member.guild.icon.url, text="Hope to see you around!")
                try:
                    await member.send(embed=embed)
                except:
                    return


def setup(bot):
    bot.add_cog(Verify(bot))
