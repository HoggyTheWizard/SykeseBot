from discord.ext import commands
from bot.utils.Checks.user_checks import check_perms, embed_perm
from main import main_db
from config import host
import discord

users = main_db["users"]
gif_domains = ["https://tenor.com/", "tenor.com"]
blacklisted_domains = ["https://discord.gg/", "discord.gg/"]


class auto_moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.type == discord.MessageType.application_command:
            return
        elif message.guild.id == 889697074491293736 and host == "master":
            if any(x in message.content for x in gif_domains):
                if embed_perm(message.author) is False:
                    await message.delete()
            if any(x in message.content for x in blacklisted_domains):
                if check_perms(message.author, ["bypass.blacklistedDomains"]) is True:
                    return
                else:
                    await message.delete()

def setup(bot):
    bot.add_cog(auto_moderation(bot))
