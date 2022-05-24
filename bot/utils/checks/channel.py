from discord.commands import core

whitelisted_channel_ids = [893934059804319775,  # verification
                           893936274291974164,  # bots
                           889697149279956993,  # moderator-commands
                           892116017977905242]  # staff-chat
blacklisted_channels = []


class ChannelChecks(core.ApplicationCommandError):
    pass


def ephemeral(ctx):
    if ctx.channel.id in whitelisted_channel_ids:
        return False
    elif ctx.channel.id in blacklisted_channels:
        raise ChannelChecks("This channel cannot be used for commands.")
    else:
        return True
