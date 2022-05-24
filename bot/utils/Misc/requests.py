from discord.commands import core
from config import hypixel_api_key as key
import aiohttp
import asyncio


class ApiException(core.ApplicationCommandError):
    pass


class RequestParamsUnfilled(core.ApplicationCommandError):
    pass


async def mojang(uuid=None, name=None, counter=0):
    if not name and not uuid:
        raise RequestParamsUnfilled("You must provide either a UUID or a username.")
    counter = counter
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{uuid if uuid else name}?") as r:
            # status 429 means the Mojang API ratelimit (600 per 10 min) has been reached
            if r.status == 429:
                if counter > 5:
                    raise ApiException(f"The Mojang API ratelimit has been reached and exceeded multiple times. "
                                       f"Please check to make sure the ratelimit has not been changed.")
                await asyncio.sleep(120)
                await mojang(uuid if uuid else name, counter+1)

            if r.status == 200:
                return r.json()

            else:
                return None


async def player(uuid=None, name=None, counter=0):
    if not name and not uuid:
        raise RequestParamsUnfilled("You must provide either a UUID or a username.")
    if not uuid:
        m = await mojang(name)
        uuid = m["id"] if m else None

    counter = counter
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.hypixel.net/player?key={key}&uuid={uuid}") as r:
            # Hypixel API ratelimit reached (120 per minute)
            if r.status == 429:
                if counter > 2:
                    raise ApiException(f"The Hypixel API ratelimit has been reached and exceeded multiple times. "
                                       f"Please check to make sure the ratelimit has not been changed.")
                await asyncio.sleep(61)
                await player(uuid if uuid else name, counter+1)

            if r.status == 200:
                return r.json()

            else:
                return None
