from discord.ext import commands
from bot.utils.Checks.user_checks import group_check

whitelisted_channel_ids = [893934059804319775, 833711606470148206, 889697149279956993, 892116017977905242]


class channel_checks(commands.CommandError):
    pass


def channel_restricted():
    async def predicate(ctx):
        if ctx.channel.id not in whitelisted_channel_ids:
            try:
                if group_check(ctx.author, 90):
                    return True
                else:
                    await ctx.message.delete()
                    return
            except:
                await ctx.message.delete()
                return
        else:
            return True
    return commands.check(predicate)
