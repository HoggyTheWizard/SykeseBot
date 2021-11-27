from discord.ext import commands
from variables import permission_tiers
import discord


class user_checks(commands.CommandError):
    pass


def is_verified(users):
    async def predicate(ctx):
        if users.find_one({"id": ctx.author.id}) is None:
            raise user_checks("You need to be verified to use this command!")
        else:
            return True
    return commands.check(predicate)


def is_staff(users, permission_level=None):
    async def predicate(ctx):
        if users.find_one({"id": ctx.author.id}) is None:
            raise user_checks("You do not have permission to use this command!")
        else:
            if permission_level is None:
                permission = 0
            else:
                permission = permission_level
            try:
                staff = users.find_one({"id": ctx.author.id})["Staff"]
                if staff["permissionLevel"] >= permission:
                    return True
                else:
                    raise user_checks("You do not have permission to use this command!")
            except:
                raise user_checks("You do not have permission to use this command!")
    return commands.check(predicate)


def group_check(author: discord.Member, minimum_permission_level: int):
    role_list = []
    if not len(author.roles):
        return False

    for role in author.roles:
        role_list.append(role.id)

    highest_role_permission = 0

    for role_id in role_list:
        if permission_tiers.get(role_id, None) is not None:
            if permission_tiers[role_id] > highest_role_permission:
                highest_role_permission = permission_tiers[role_id]

    if highest_role_permission >= minimum_permission_level:
        return True
    else:
        return False
