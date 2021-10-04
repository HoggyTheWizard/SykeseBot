from discord.ext import commands
from variables import mod_role_id
from config import flagged_words, host
import discord

exceptions = ["None for now :sadge:"]

class flags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if host != "master":
            return
        elif message.author.bot:
            return
        elif message.guild.id not in [889697074491293736, 707963219536248982]:
            return
        elif any(flagged in message.content.lower().split() for flagged in flagged_words):
            my_word = ""
            for word in flagged_words:
                if word in message.content.lower().split():
                    my_word += word
                    break
            if my_word in exceptions:
                return
            else:
                await message.delete()
                embed = discord.Embed(title="[FLAGGED] - Detected Abusive Language",
                                      description="Our system detected abusive language in the chat. Please monitor "
                                                  "this situation ASAP. If this was falsely flagged, please let a "
                                                  "developer know so that an an exception can be made in the code.",
                                      color=discord.Colour.red())
                embed.add_field(name="User:", value=message.author, inline=False)
                embed.add_field(name="User ID:", value=message.author.id, inline=False)
                embed.add_field(name="Flagged Word(s):", value=my_word, inline=False)
                embed.add_field(name="Message Content:", value=message.content, inline=False)
                channel = message.guild.get_channel(836990571012030465)
                await channel.send(embed=embed)
                await channel.send(f"{message.author.id}\n<@{mod_role_id}>")

def setup(bot):
    bot.add_cog(flags(bot))
