from discord.ext import commands
from discord.commands import slash_command as slash
from bot.variables import guilds
from bot.utils.checks.user import verified, manager
from bot.utils.checks.channel import ephemeral
from db import main_db
import discord

users = main_db["users"]


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(description="Displays the ping of the bot.", guild_ids=guilds)
    @verified()
    async def ping(self, ctx):
        await ctx.respond(f"🏓 Pong ({round(self.bot.latency * 1000)}ms)", ephemeral=ephemeral(ctx))

    @commands.command(description="Sends Verification Info Embed")
    @manager()
    async def rules_embed(self, ctx):
        embed = discord.Embed(
            title="Community Rules and Guidelines",
            description="In order to keep our community healthy and safe, we have certain guidelines that all users "
                        "must follow. Please note that while examples may be listed, they do not reflect every "
                        "circumstance in which we will take moderation actions. A certain level of common sense is "
                        "required to determine whether or not you are breaking our rules. If you have any questions or "
                        "concerns, please contact a chat moderator.",
            color=discord.Color.blue())

        embed.add_field(
            name="Respect All Members",
            value="Regardless of your personal feelings about another user/group, you must treat them with respect "
            "within the scope of our services. \nExamples:\n- Usage of slurs (regardless of personal background and a "
            "supposed lack of ill intentions)\n- Displaying aggression, or otherwise toxic behavior\n- Discriminatory "
            "behavior\n- Hate speech\n- Doxxing\n- Threats", inline=False)

        embed.add_field(
            name="Spam",
            value="Spam is unwanted in most communities, and it is here too. It should be common sense as to what is "
                  "considered spam, but for those who have differing opinions on what constitutes it, it will be "
                  "defined here as well. Spam is sending content that is unrelated to the channel topic and/or current "
                  "conversation, or posting “meme” content in channels that disallow it.\nExamples:\n"
                  "- Mass pinging/mentioning, or otherwise doing so for no good reason\n"
                  "- Sending the same (or similar) message(s) over and over again\n"
                  "- Obnoxiously adding reactions to messages\n"
                  "- Posting random unwanted gifs in a discussion based channel\n- Begging for free items/perks/etc\n"
                  "- Intentionally sending low quality messages in order to gain leveling experience\n- Posting "
                  "something in an incorrect channel", inline=False)

        embed.add_field(
            name="Language",
            value="Our guild and server are English speaking only, and as such, all conversations should be had in "
                  "English. While we know this may be disappointing to some, there are a few reasons for this:\n"
                  "- It prevents users from not feeling included in the conversation\n"
                  "- server_management members who cannot speak said language cannot properly moderate it\n"
                  "- When multiple languages are being used at the same time, it disrupts the flow of conversation.",
                  inline=False)

        embed.add_field(
            name="Listen to Server server_management",
            value="server_management members are here for a reason and have been guided on how to handle certain "
                  "situations. Because of this, we ask that you follow the advice/instructions given by a staff "
                  "member. If for any reason you don’t believe a staff member is acting in a proper way, "
                  "you may contact another chat moderator.",
                  inline=False)

        embed_2 = discord.Embed(color=discord.Color.blue())
        embed_2.add_field(name="Inappropriate & Sensitive Content",
                          value="When interacting with the community, keep in mind that there are users as young as 13 "
                                "in this server. As such, inappropriate content will not be tolerated. Essentially, "
                                "community interaction should be kept PG-13 or under. Note that while "
                                "political/religious/etc. topics of that nature aren’t strictly disallowed, it should "
                                "be noted that those types of conversations tend to become heated easily, especially "
                                "around younger audiences. In short, be careful and respectful.\nExamples:\n"
                                "- In-depth discussions about controlled substances (alcoholic beverages, "
                                "illicit substances, etc.)\n- Sharing religious or political views that can be "
                                "reasonably considered detrimental to society (e.g. making it known that you don’t like"
                                " gay people)\n- Discussing and/or sharing "
                                "pornography\n- Sending links to inappropriate content\n- Talking about sexual "
                                "experiences", inline=False)

        embed_2.add_field(name="Exploits",
                          value="We offer a custom bot for users to enjoy, with features such as leveling and a custom "
                                "report system to help report unruly members. However, our developer(s) are not "
                                "perfect - sometimes bypasses can be found. If you find an exploit, you should contact "
                                "a moderator (or preferably a developer) as soon as possible. You will not be punished "
                                "for unintentional use if it is reported.\n"
                                "Examples:\n- Discovering an exploit and using it to your advantage",
                          inline=False)

        embed_2.add_field(name="Follow The Discord TOS",
                          value="We reserve the right to remove you from any of our services if you break the rules "
                                "set in place by Discord. Whether we do so is completely up to our "
                                "discretion and is handled on a case to case basis.\nExamples:\n " 
                                "- Being under the age of 13 (Discord)\n "
                                "- Distributing harmful material (trojan horses, IP loggers, malware, etc.)\n "
                                "- https://discord.com/terms\n "
                                "- https://discord.com/guidelines \n",
                          inline=False)
        embed_2.set_footer(text=f"If you find a user to be breaking these rules, you may report them using the /report "
                                f"command or by right clicking on a user -> Apps -> Report.", icon_url=
        "https://cdn.discordapp.com/icons/889697074491293736/1ceae83c85cfde4ac1dd1c8b95c7f774.png")
        message_1 = await ctx.guild.get_channel(892118771257458738).fetch_message(943315669548683324)
        message_2 = await ctx.guild.get_channel(892118771257458738).fetch_message(943315670546935839)
        await message_1.edit(embed=embed)
        await message_2.edit(embed=embed_2)

    @commands.command(description="Sends test embed.")
    @manager()
    async def send_dot(self, ctx):
        embed = discord.Embed(title='test')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
