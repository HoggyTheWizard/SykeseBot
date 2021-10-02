from config import hypixel_api_key
from discord.ext import commands
import aiohttp


class general(commands.CommandError):
    pass


async def aiohttp_json(endpoint, attribute):
    if endpoint == "player":
        url = f"https://api.hypixel.net/player?key={hypixel_api_key}&uuid={attribute}"
    else:
        raise general("Invalid endpoint provided")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()
    except Exception as e:
        print(e)
        raise general("An error occurred whilst fetching data for this user. (details printed to console)")


async def get_mojang_from_username(username):
        try:
            url = f"https://api.mojang.com/users/profiles/minecraft/{username}?"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    return await resp.json()
        except:
            raise general(f"Invalid username provided - are you sure `{username}` is correct?")


async def get_mojang_from_uuid(uuid):
    try:
        url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()
    except:
        return None