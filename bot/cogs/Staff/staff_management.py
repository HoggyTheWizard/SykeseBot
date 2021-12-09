from discord.ext import commands
from main import main_db
from bot.utils.Checks.channel_checks import channel_restricted
from bot.utils.Misc.permissions import get_all_files
from bot.utils.Checks.user_checks import is_staff
from variables import mod_role_id
import pathlib
import discord
import pathlib
import json
import os

users = main_db["users"]


class staff_management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(hidden=True)
    @channel_restricted()
    @is_staff(users=users)
    async def staff(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please use a subcommand:\n"
                           "+staff add <user> - Adds staff permissions to a user\n"
                           "+staff remove <user> - Removes staff permissions from a user.")

    @staff.command(hidden=True)
    @channel_restricted()
    @is_staff(users=users)
    async def add(self, ctx, member: discord.Member, permission_level):
        user = users.find_one({"id": member.id})
        if user is None:
            await ctx.send("This user has not verified yet, and as such cannot be set to staff.")
        else:
            users.update_one({"id": user["id"]}, {"$set": {"Staff.permissionLevel": int(permission_level)}})
            await member.add_roles(ctx.guild.get_role(mod_role_id))
            await ctx.send(f"Successfully set `{str(member)}` to staff with a permission level of "
                           f"`{permission_level}`")

    @staff.command(hidden=True)
    @channel_restricted()
    @is_staff(users=users)
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

    @commands.command(hidden=True)
    @is_staff(users)
    async def set_perm(self, ctx, role: discord.Role, name: str):
        with open(f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/{str(role.id)}.json", "r+") as file:
            new_json = {
                "id": name,
            }
            data = json.load(file)
            data[name].append(new_json)
            file.seek(0)
            json.dump(data, file, indent=4)
            await ctx.send(f"Successfully added `{name}` permission to the `{role.name}` role.")

    @commands.command()
    async def boop(self, ctx):
        await ctx.send(get_all_files())

    @commands.command(hidden=True)
    @is_staff(users)
    async def remove_perm(self, ctx, role: discord.Role, name: str):
        with open(f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/{str(role.id)}.json", "r+") as file:
            new_json = {
                "id": name,
            }
            data = json.load(file)
            data["emp_details"].append(new_json)
            file.seek(0)
            json.dump(data, file, indent=4)
            await ctx.send(f"Successfully added `{name}` permission to the `{role.name}` role.")

    @commands.command(hidden=True)
    async def set_global_perm(self, ctx, name: str):
        directory = f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/"
        for file_name in os.listdir(directory):
            with open(f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/{file_name}", "r+") as file:
                new_json = {
                    "id": name,
                }
                data = json.load(file)
                data["emp_details"].append(new_json)
                file.seek(0)
                json.dump(data, file, indent=4)
        await ctx.send(f"Successfully set `{name}` as a global permission.")

def setup(bot):
    bot.add_cog(staff_management(bot))
