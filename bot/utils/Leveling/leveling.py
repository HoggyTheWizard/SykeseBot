from discord.ext import commands
# Settings
exp_for_next_level = 100
exp_for_next_prestige = exp_for_next_level * 25
emoji_id = 678312701205807105

# add role ids
levelup_actions = {
    "10": 0, "25": 0, "50": 0,
    "75": 0, "100": 0, "125": 0,
    "150": 0, "175": 0, "200": 0,
}

class LevelingMain(commands.CommandError):
    pass

    @staticmethod
    def get_leveling(collection, users):
        if collection is None:
            return None
        else:
            leveling_object = collection.get("Leveling", None)
            if leveling_object is not None:
                return leveling_object
            elif leveling_object is None:
                users.update_one({"id": collection["id"]}, {"$set": {"Leveling": {"exp": 0}}})
                return users.find_one({"id": collection["id"]})["Leveling"]

    @staticmethod
    async def levelup(self, message, collection, leveling, users):
        exp = leveling.get("exp", 0)
        lvl = leveling.get("level", 0)
        # Taken from mee6 (the only good thing they've ever done)
        levelup_xp_needed = 5 * (lvl ** 2) + (50 * lvl) + 100
        if exp >= levelup_xp_needed:
            users.update_one({"id": collection["id"]}, {"$set": {"Leveling.level": lvl + 1}})
            if str(lvl) in levelup_actions:
                role = await message.guild.get_role(levelup_actions[str(lvl)])
                await message.author.add_roles(role)
                await message.channel.send(f"Congrats <@{message.author.id}>, you're now level **{lvl}** and "
                                           f"have received the {role.name} role!")
