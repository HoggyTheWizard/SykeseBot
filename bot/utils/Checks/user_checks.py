from discord.ext import commands


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
