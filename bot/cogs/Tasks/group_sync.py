from discord.ext import commands, tasks
from bot.utils.Misc.general import get_highest_group
from main import main_db
from config import host

users = main_db["users"]

role_cache = {}


class group_sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sync_user_groups.start()

    @tasks.loop(seconds=60)
    async def sync_user_groups(self):
        print("Starting sync task...")
        if host != "master":
            guild = self.bot.get_guild(889697074491293736)
            for member in guild.members:
                if not len(member.roles):
                    continue
                else:
                    group = get_highest_group(member)

                    if role_cache.get(member.id, None) is not None:
                        if role_cache[member.id] not in member.roles:
                            print("cache is None db add")
                            #users.update_one({"id": member.id}, {"$set": {"group": [group[0], group[1]]
                            #                                             }})
                    else:
                        collection = users.find_one({"id": member.id})
                        if collection is None:
                            continue
                        elif collection.get("group", None) is None:
                            if group[0] is None:
                                print("group[0] is None db add")
                                #users.update_one({"id": member.id}, {"$set": {"group": [group[0], group[1]]
                                #                                              }})
                        elif collection["group"] not in member.roles:
                            print("collection group not in member roles db add")
                            #users.update_one({"id": member.id}, {"$set": {"group": [group[0], group[1]]
                            #                                              }})
            print("Finished!")
    @sync_user_groups.before_loop
    async def before_printer(self):
        print("Queueing Sync Task...")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(group_sync(bot))
