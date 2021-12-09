from discord.ext import commands

whitelisted_channel_ids = [893934059804319775, 833711606470148206, 889697149279956993, 892116017977905242]


class channel_checks(commands.CommandError):
    pass


def channel_restricted():
    async def predicate(ctx):
        if ctx.guild.id is not 889697074491293736:
            return True
        if ctx.channel.id not in whitelisted_channel_ids:
            try:
                # Commenting out while this is reworked
                #if group_check(ctx.author, 90):
                #    return True
                if 5 < 4:
                    return True
                else:
                    await ctx.respond("You cannot use this command in this channel!", ephemeral=True)
                    return
            except:
                await ctx.respond("You cannot use this command in this channel!", ephemeral=True)
                return
        else:
            return True
    return commands.check(predicate)
