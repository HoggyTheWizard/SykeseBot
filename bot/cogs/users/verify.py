from discord.ext import commands
from discord.commands import slash_command as slash, Option
from bot.variables import guilds
from db import main_db
from bot.utils.misc.requests import player
from bot.utils.checks.user import mod
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
    async def verify(self, ctx, username: Option(str, "Your Minecraft username")):
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

            if users.find_one({"uuid": p["player"]["uuid"]}):
                await ctx.respond("This Minecraft account is already linked to another Discord account.")
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
                await ctx.author.edit(nick=username)

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
                                      "to his channel, starts streaming, or starts a giveaway. "
                                      "These are optional, however we recommend that you enable them.",
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

    @slash(description="Verifies a user by bypassing Hypixel checks. Only use this if you know they own the account.",
           guild_ids=guilds)
    @mod()
    async def forceverify(self, ctx,
                          member: Option(discord.Member, "The member to forceverify"),
                          username: Option(str, "The Minecraft username you want to link the account to"),
                          bypass: Option(str, "Bypasses ALL checks; only use this if you're sure the account is valid.",
                                         choices=["true", "false"], default="false", required=False)
                          ):
        bypass = True if bypass == "true" else False

        if not member:
            await ctx.respond("Invalid member provided")
            return

        doc = users.find_one({"id": member.id})
        if doc and not bypass:
            name = member.nick if member.nick else member.name
            await ctx.respond(f"This member is already verified to `{name}` ({doc.get('uuid', 'ERROR')}). "
                              f"If you wish to switch their account to something new, run the command using the "
                              f"`bypass` argument.")
        else:
            p = await player(name=username)
            obj = Player(player=p)

            if not p and not bypass:
                await ctx.respond("This account couldn't be found... Are you sure you entered the correct username?"
                                  "If it is, try running the command again with the `bypass` argument.")
                return

            if users.find_one({"uuid": p["player"]["uuid"]}) and not bypass:
                await ctx.respond("This Minecraft account is already linked to another Discord account. If you wish to "
                                  "still link it, run the command using the `bypass` argument.")
                return

            await member.add_roles(
                ctx.guild.get_role(verified_role_id),
                ctx.guild.get_role(obj.level()[1]),
                ctx.guild.get_role(obj.rank()["role"])
            )
            await member.edit(nick=username)

            users.insert_one({"id": member.id, "uuid": p["player"]["uuid"],
                              "verifiedAt": datetime.timestamp(datetime.now())})

            embed = discord.Embed(title="Verification Successful!",
                                  description=f"Your account was force verified by a moderator in the {ctx.guild.name} "
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
                await member.send(embed=embed)
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
