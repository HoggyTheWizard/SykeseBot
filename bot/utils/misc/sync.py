import discord


async def set_nick(member: discord.Member, request: dict):
    if not member.nick and request["name"] != member.name:
        try:
            await member.edit(nick=request["name"])
            return True
        except discord.Forbidden:
            return False

    elif member.nick != request["name"]:
        try:
            await member.edit(nick=request["name"])
            return True
        except discord.Forbidden:
            return False


