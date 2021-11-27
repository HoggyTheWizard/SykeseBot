from discord.ext import commands
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
                try:
                    permission_level = users.find_one({"id": message.author.id})["permissionLevel"]
                except:
                    permission_level = 0

                if permission_level < 1 and message.channel.id != 836990571012030465:
                    await message.delete()


def setup(bot):
    bot.add_cog(auto_moderation(bot))
