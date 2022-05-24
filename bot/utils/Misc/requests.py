import aiohttp
import asyncio


class ApiException(Exception):
    def __init__(self, message):
        self.message = message


async def mojang(uuid, counter=0):
    counter = counter
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{uuid}?") as r:

            # status 429 means the Mojang API ratelimit (600 per 10 min) has been reached
            if r.status == 429:
                if counter > 5:
                    raise ApiException(f"The Mojang API ratelimit has been reached and exceeded multiple times. "
                                       f"Please check to make sure the ratelimit has not been changed.")
                await asyncio.sleep(120)
                await mojang(uuid, counter+1)

            if r.status == 200:
                return r.json()

            else:
                return None
