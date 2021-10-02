from discord.ext import commands

whitelisted_channel_ids = [833711606470148206, 889697149279956993, 892116017977905242]


class channel_checks(commands.CommandError):
    pass


def channel_restricted(users):
    async def predicate(ctx):
        if ctx.channel.id not in whitelisted_channel_ids:
            try:
                permissions = users.find_one({"id": ctx.author.id})["Permissions"]
                if permissions["bypassPermissions"] is True:
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
