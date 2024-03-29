from discord.commands import core
import asyncio
import aiohttp
import os


class ApiException(core.ApplicationCommandError):
    pass


class RequestParamsUnfulfilled(core.ApplicationCommandError):
    pass


async def mojang(uuid: str = None, name: str = None, counter: int = 0):
    async with aiohttp.ClientSession() as session:
        link = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}" if uuid else \
            f"https://api.mojang.com/users/profiles/minecraft/{name}"
        async with session.get(link) as r:
            # status 429 means the Mojang API ratelimit (600 per 10 min) has been reached
            if r.status == 429:

                if counter > 5:
                    raise ApiException(f"The Mojang API ratelimit has been reached and exceeded multiple times. "
                                       f"Please check to make sure the ratelimit has not been changed.")
                await asyncio.sleep(120)
                await mojang(uuid, name, counter+1)

            return await r.json() if r.status == 200 else None


async def player(uuid=None, name=None, counter=0):
    if not name and not uuid:
        raise RequestParamsUnfulfilled("You must provide either a UUID or a username.")

    if not uuid and name:
        m = await mojang(name=name)
    else:
        m = {"id": uuid}
    counter = counter

    if m is None:
        return None

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.hypixel.net/player?key={os.environ['HYPIXEL_API_KEY']}&uuid={m['id']}") as r:
            # Hypixel API ratelimit reached (120 per minute)
            if r.status == 429:
                if counter > 2:
                    raise ApiException(f"The Hypixel API ratelimit has been reached and exceeded multiple times. "
                                       f"Please check to make sure the ratelimit has not been changed.")
                await asyncio.sleep(61)
                await player(uuid=uuid, counter=counter+1)

            return await r.json() if r.status == 200 else None
