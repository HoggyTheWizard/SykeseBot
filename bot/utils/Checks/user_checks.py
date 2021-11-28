from discord.ext import commands
from variables import group_tiers
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

