from discord.ext import commands
from discord.commands import core
from db import main_db
import bot.variables as v
import discord

users = main_db["users"]
alts = main_db["alts"]
# These functions are a fallback for if Discord's permission systems fail (they have before, and they will again)


class UserChecks(core.ApplicationCommandError):
    pass


def throw(x):
    raise x


def verified():
    async def predicate(ctx):
        roles = [role for role in v.moderator_ids]
        roles.append(v.verified_role_id)

        return (len([role.id for role in ctx.author.roles if role.id in roles])) \
               or throw(UserChecks("You must be verified to use this command."))

    return commands.check(predicate)


def embed_perm(author: discord.Member):
    if not len(author.roles):
        return False
    else:
        for role in author.roles:
            if role.permissions.embed_links:
                return True
        return False


def staff_check(author, id_list: list):
    return (author.id in v.owner_ids) or (len([role.id for role in author.roles if role.id in id_list]) >= 1)


def mod():
    async def predicate(ctx):
        return staff_check(ctx.author, v.moderator_ids) or throw(UserChecks(
            "You must be a moderator or above to use this command."))

    return commands.check(predicate)


def manager():
    async def predicate(ctx):
        return staff_check(ctx.author, v.manager_ids) or throw(UserChecks(
            "You must be a manager or above to use this command."))

    return commands.check(predicate)


