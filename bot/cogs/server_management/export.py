from discord.commands import slash_command as slash, Option as option
from bot.utils.checks.user import manager
from bson import json_util
from discord.ext import commands
from datetime import datetime
from db import main_db
import bot.variables as v
import discord
import json
import io

users = main_db["users"]
# A list of keys that shouldn't be exported for a normal user.
blacklisted_keys = ["Staff"]


class Export(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(guild_ids=v.guilds, description="Exports data for a user")
    @manager()
    async def export(self, ctx,
                     filtered: option(str, description="Filter out private data (member export requests).",
                                      choices=["Yes", "No"]),
                     member: option(discord.Member, description="A member in the server to export.", required=False),
                     discord_id: option(str, description="The Discord ID of a user to export.", required=False)):
        if not member and not discord_id:
            await ctx.respond("You must specify a member or a Discord ID.", ephemeral=True)
            return

        identifier = member.id if member else int(discord_id) if discord_id else None
        doc = users.find_one({"id": identifier})
        if not identifier or not doc:
            await ctx.respond("Couldn't find any data for the provided user. Are you sure you selected the correct "
                              "user?", ephemeral=True)
            return

        await ctx.respond("Collecting data...")

        if filtered == "Yes":
            for item in blacklisted_keys:
                if item in doc:
                    del doc[item]

        f = json.loads(json_util.dumps(doc))

        with io.BytesIO() as a:
            a.write(json.dumps(f).encode())
            a.seek(0)
            await ctx.send(file=discord.File(a, filename=f"{identifier}_export_{datetime.now().timestamp()}.json"))
        await ctx.interaction.edit_original_message(content="Done!")


def setup(bot):
    bot.add_cog(Export(bot))
