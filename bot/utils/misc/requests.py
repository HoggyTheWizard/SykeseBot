from discord.commands import core
from config import hypixel_api_key as key
import asyncio
import aiohttp


class ApiException(core.ApplicationCommandError):
    pass


class RequestParamsUnfulfilled(core.ApplicationCommandError):
    pass


async def mojang(uuid_or_name: str, counter: int = 0):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{uuid_or_name}") as r:
            print("m session fetched", r.status)
            # status 429 means the Mojang API ratelimit (600 per 10 min) has been reached
            if r.status == 429:

                if counter > 5:
                    raise ApiException(f"The Mojang API ratelimit has been reached and exceeded multiple times. "
                                       f"Please check to make sure the ratelimit has not been changed.")
                await asyncio.sleep(120)
                await mojang(uuid_or_name, counter+1)

            return await r.json() if r.status == 200 else None


async def player(uuid=None, name=None, counter=0):
    if not name and not uuid:
        raise RequestParamsUnfulfilled("You must provide either a UUID or a username.")

    if not uuid and name:
        m = await mojang(uuid_or_name=name)
    else:
        m = {"id": uuid}
    counter = counter
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.hypixel.net/player?key={key}&uuid={m['id']}") as r:
            # Hypixel API ratelimit reached (120 per minute)
            if r.status == 429:
                if counter > 2:
                    raise ApiException(f"The Hypixel API ratelimit has been reached and exceeded multiple times. "
                                       f"Please check to make sure the ratelimit has not been changed.")
                await asyncio.sleep(61)
                await player(uuid=uuid, counter=counter+1)

            return await r.json() if r.status == 200 else None
