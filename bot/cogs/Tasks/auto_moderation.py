from discord.ext import commands
from bot.utils.Checks.user_checks import check_perms
from main import main_db
from config import host
import discord

users = main_db["users"]
blacklisted_domains = ["https://tenor.com/", "tenor.com/", "https://discord.gg/", "discord.gg/"]


class auto_moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Create exception for higher roled people posting tenor links
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.type == discord.MessageType.application_command:
            return
        elif message.guild.id == 707963219536248982 and host != "master":

            if any(x in message.content for x in blacklisted_domains):
                if check_perms(message.author, ["bypass.blacklistedDomains"]) is True:
                    return
                else:
                    await message.delete()

def setup(bot):
    bot.add_cog(auto_moderation(bot))
