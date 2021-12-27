from discord.ext import commands
from bot.utils.Misc.permissions import generate_permission_list, highest_perm_role
from variables import test_guilds
import discord


class user_checks(commands.CommandError):
    pass


def is_verified():
    async def predicate(ctx):
        if ctx.guild.id != 889697074491293736:
            return True
        else:
            role_list = []
            for role in ctx.author.roles:
                role_list.append(role.id)
            if 893933214656233563 not in role_list:
                return False
    return commands.check(predicate)


def check_perms(author: discord.Member, required_permissions: list, override=None):
    if override is True:
        return True
    else:
        role = highest_perm_role(author)
        if role is None:
            return False
        else:
            perm_list = generate_permission_list(role)
            if not len(perm_list):
                return False
            for permission in required_permissions:
                if permission not in perm_list:
                    return False
            return True


def perms(required_permissions: list):
    async def predicate(ctx):
        highest_role = highest_perm_role(ctx.author)
        if highest_role is None:
            return False
        elif ctx.guild.id in test_guilds:
            return True
        else:
            return check_perms(ctx.author, required_permissions)
    return commands.check(predicate)
