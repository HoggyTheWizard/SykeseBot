from discord.ext import commands
from bot.utils.checks.user import staff_check, embed_perm
from db import main_db
from config import host
import bot.variables as v
import discord

users = main_db["users"]
gif_domains = ["https://tenor.com/", "tenor.com"]
blacklisted_domains = ["https://discord.gg/", "discord.gg/"]


class AutoModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.type == discord.MessageType.application_command or message.guild is None:
            return
        elif message.guild.id == 889697074491293736 and host == "master":
            if any(x in message.content for x in gif_domains):
                if embed_perm(message.author) is False:
                    await message.delete()
            if any(x in message.content for x in blacklisted_domains):
                if staff_check(message.author, v.moderator_ids) is True:
                    return
                else:
                    await message.delete()

    @commands.Cog.listener()
    async def on_auto_moderation_action_execution(self, payload):
        """TEMPORARILY DISABLED DUE TO PYCORD HAVING MAJOR ISSUES WITH THIS LISTENER (e.g. event triggering 3 times)"""
        return

        print("triggered")

        if (not payload.member or
                payload.guild.id != v.guilds[0] or
                host != "master"):
            return

        if payload.rule_id == v.mention_spam_rule:
            try:
                await payload.member.send("You have been temporarily blocked from chatting due to being flagged for "
                                          "spam. The duration of this timeout is not static and may change. If you "
                                          "believe this is a mistake, please contact a staff member.")
            except discord.Forbidden:
                await payload.guild.get_channel(v.moderator_commands).send(f"{payload.member.mention} could not be "
                                                                           f"sent a DM due to their Discord "
                                                                           f"permissions.")


def setup(bot):
    bot.add_cog(AutoModeration(bot))
