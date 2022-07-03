from bot.utils.hypixel.player import Player, levels, ranks
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


async def set_hypixel(guild: discord.Guild, member: discord.Member, request: dict, rank_roles: list = None,
                      level_roles: list = None):

    member_roles = [role.id for role in member.roles]
    p = Player(request)
    statuses = []

    if not rank_roles or not level_roles:
        rank_roles, level_roles = get_hypixel_roles(guild)

    # level returns the user's actual Hypixel level and the role associated with it, in that order
    level, corresponding_level_role = p.level()
    corresponding_rank_role = p.rank()["role"]

    # handling level role
    if corresponding_level_role not in member_roles:
        try:
            await member.remove_roles(*level_roles)
            await member.add_roles(guild.get_role(corresponding_level_role))
            statuses[0] = True
        except discord.Forbidden:
            statuses[0] = False

    # handling rank role
    if corresponding_rank_role not in member_roles:
        try:
            await member.remove_roles(*rank_roles)
            await member.add_roles(guild.get_role(corresponding_rank_role))
            statuses[1] = True
        except discord.Forbidden:
            statuses[1] = False

    return statuses[0], statuses[1]


def get_hypixel_roles(guild: discord.Guild):
    # rank information is stored in a dict. In the list comp, x is the key
    rank_roles = [guild.get_role(ranks[x]["role"]) for x in ranks]

    # level roles are stored in a list of tuples, where [0] is the required level and [1] is the role
    level_roles = [guild.get_role(x[1]) for x in levels]

    return rank_roles, level_roles
