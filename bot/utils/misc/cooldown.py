from bot.variables import mod_id
from discord.ext import commands
import time
import discord

command_cache = {}


def get_author_role_ids(author: discord.Member):
    role_ids = []
    if not len(author.roles):
        return role_ids
    else:
        for role in author.roles:
            role_ids.append(role.id)
        return role_ids


def cooldown(seconds: int, mod_bypass: bool = False):
    async def predicate(ctx):
        if mod_bypass is True and mod_id in get_author_role_ids(ctx.author):
            return True
        else:
            try:
                last_used = command_cache[ctx.author.id][ctx.command.name]["timestamp"]
                if time.time() - last_used >= seconds:
                    command_cache[ctx.author.id][ctx.command.name]["timestamp"] = time.time()
                    return True
                else:
                    await ctx.respond(f"You can only use this command every {seconds} seconds. "
                              f"({round(seconds - (time.time() - last_used))} seconds remaining)")
                    return False
            except:
                command_cache[ctx.author.id] = {
                        ctx.command.name: {
                            "timestamp": time.time()}
                    }
                return True
    return commands.check(predicate)
