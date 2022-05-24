from bot.utils.checks.user import staff_check
from discord.ext import commands
from bot.variables import test_guilds, moderator_ids

whitelisted_channel_ids = [893934059804319775, 893936274291974164, 889697149279956993, 892116017977905242]


class channel_checks(commands.CommandError):
    pass


def channel_restricted():
    async def predicate(ctx):
        if ctx.guild.id in test_guilds:
            return True
        if ctx.channel.id not in whitelisted_channel_ids:
            if staff_check(ctx.author, moderator_ids) is False:
                error = "You cannot use this command in this channel!"
                try:
                    await ctx.respond(error, ephemeral=True)
                except:
                    await ctx.message.delete()
                return False
        else:
            return True
    return commands.check(predicate)
