from discord.ext import commands
from variables import group_tiers
from bot.utils.Misc.permissions import generate_permission_list, highest_perm_role
import discord
import pathlib
import json

class user_checks(commands.CommandError):
    pass


def is_verified(users):
    async def predicate(ctx):
        if users.find_one({"id": ctx.author.id}) is None:
            raise user_checks("You need to be verified to use this command!")
        else:
            return True
    return commands.check(predicate)


def is_staff(users):
    async def predicate(ctx):
        collection = users.find_one({"id": ctx.author.id})

        if collection is None:
            raise user_checks("You do not have permission to use this command!")

        try:
            staff_check = collection["Staff"]["isStaff"]
            if staff_check is False:
                raise user_checks("You do not have permission to use this command!")
            elif staff_check is True:
                return True
        except:
            raise user_checks("You do not have permission to use this command!")

        else:
            return True
    return commands.check(predicate)

def check_perms(author: discord.Member, required_permissions: list, db_override=None):
    role = highest_perm_role(author)
    if role is None:
        return False
    else:
        perm_list = generate_permission_list(role)
        if not len(perm_list):
            return False
        # continue here

def perms(required_permissions: list):
    async def predicate(ctx):
        highest_role = highest_perm_role(ctx.author)
        if highest_role is None:
            return False
        else:
            check_perms(highest_role, required_permissions)
    return commands.check(predicate)
