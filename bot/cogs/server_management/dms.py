from discord.ext import commands


class DMs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild and not message.author.bot:
            channel = self.bot.get_channel(942152380600950824)
            if not message.attachments:
                await channel.send(f"Message From {str(message.author)} ({message.author.id}):\n{message.content}")
            else:
                string = ""
                images = [img.url for img in message.attachments]
                for url in images:
                    string += f"{url}\n"

                await channel.send(f"Message From {str(message.author)} ({message.author.id}):\n{message.content}")
                await channel.send(string)


def setup(bot):
    bot.add_cog(DMs(bot))
