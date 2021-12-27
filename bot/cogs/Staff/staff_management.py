from discord.ext import commands
from bot.utils.Checks.user_checks import perms
import discord
import pathlib
import json
import os


class staff_management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @perms(["staff.admin"])
    async def set_perm(self, ctx, role: discord.Role, name: str):
        with open(f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/{str(role.id)}.json", "r+") as file:
            new_json = {
                "id": name
            }
            data = json.load(file)
            data[name] = new_json
            file.seek(0)
            json.dump(data, file, indent=4)
            await ctx.send(f"Successfully added `{name}` permission to the `{role.name}` role.")

    @commands.command(hidden=True)
    @perms(["staff.admin"])
    async def remove_perm(self, ctx, role: discord.Role, name: str):
        with open(f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/{str(role.id)}.json", "r") as file:
            data = json.load(file)
            data.pop(name)

        with open(f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/{str(role.id)}.json", "w") as file:
            json.dump(data, file)
            await ctx.send(f"Successfully removed `{name}` permission from the `{role.name}` role.")

    @commands.command(hidden=True)
    @perms(["staff.admin"])
    async def set_global_perm(self, ctx, name: str):
        directory = f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/"
        for file_name in os.listdir(directory):
            with open(f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/{file_name}", "r+") as file:
                new_json = {
                    "id": name,
                }
                data = json.load(file)
                data[name] = new_json
                file.seek(0)
                json.dump(data, file, indent=4)
        await ctx.send(f"Successfully set `{name}` as a global permission.")


def setup(bot):
    bot.add_cog(staff_management(bot))
