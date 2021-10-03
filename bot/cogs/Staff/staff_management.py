from discord.ext import commands
from main import main_db
from bot.utils.Checks.channel_checks import channel_restricted
from bot.utils.Checks.user_checks import is_staff
from variables import mod_role_id
import discord

users = main_db["users"]


class staff_management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(hidden=True)
    @channel_restricted(users=users)
    @is_staff(users=users, permission_level=2)
    async def staff(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please use a subcommand:\n"
                           "+staff add <user> - Adds staff permissions to a user\n"
                           "+staff remove <user> - Removes staff permissions from a user.")

    @staff.command(hidden=True)
    @channel_restricted(users=users)
    @is_staff(users=users, permission_level=2)
    async def add(self, ctx, member: discord.Member, permission_level):
        user = users.find_one({"id": member.id})
        if user is None:
            await ctx.send("This user has not verified yet, and as such cannot be set to staff.")
        else:
            users.update_one({"id": user["id"]}, {"$set": {"Staff.permissionLevel": permission_level}})
            await member.add_roles(ctx.guild.get_role(mod_role_id))
            await ctx.send(f"Successfully set `{str(member)}` to staff with a permission level of "
                           f"`{permission_level}`")

    @staff.command(hidden=True)
    @channel_restricted(users=users)
    @is_staff(users=users, permission_level=2)
    async def remove(self, ctx, member: discord.Member):
        user = users.find_one({"id": member.id})
        if user is None:
            await ctx.send("This user has not verified yet, and as such they do not have staff permissions to remove.")
        else:
            try:
                for item in user["Staff"]:
                    if type(user["Staff"][item]) is int:
                        users.update_one({"id": user["id"]}, {"$set": {f"Staff.{item}": 0}})
                    elif type(user["Staff"][item]) is bool:
                        users.update_one({"id": user["id"]}, {"$set": {f"Staff.{item}": False}})
                    else:
                        users.update_one({"id": user["id"]}, {"$set": {f"Staff.{item}": None}})
                        await ctx.send(f"Value {item} (Type = {type(item)} is neither a boolean nor an integer. Please "
                        "tell a developer to make an exception for this type. For now, it has been set to None.")
                    await member.remove_roles(ctx.guild.get_role(mod_role_id))
            except Exception as e:
                print(e)
                await ctx.send("An unexpected error occurred.. please tell a developer to check the console.")
            await ctx.send(f"Successfully removed staff from `{str(member)}`")


def setup(bot):
    bot.add_cog(staff_management(bot))
