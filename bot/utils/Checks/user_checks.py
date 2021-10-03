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


def is_staff(users):
    async def predicate(ctx):
        if users.find_one({"id": ctx.author.id}) is None:
            raise user_checks("You do not have permission to use this command!")
        else:
            try:
                permissions = users.find_one({"id": ctx.author.id})["Permissions"]
                if permissions["isStaff"] is True:
                    return True
                else:
                    raise user_checks("You do not have permission to use this command!")
            except:
                raise user_checks("You do not have permission to use this command!")
    return commands.check(predicate)
