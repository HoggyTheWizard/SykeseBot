from discord.ext import commands
# Settings
exp_for_next_level = 100
exp_for_next_prestige = exp_for_next_level * 25
emoji_id = 678312701205807105


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
            emoji = self.bot.get_emoji(905569355507585035)
            if lvl == 1:
                await message.add_reaction(str(emoji))
            elif lvl % 5 == 0:
                await message.add_reaction(str(emoji))
            elif lvl % 10 == 0:
                await message.channel.send(f"Congrats <@{message.author.id}>, you're now level **{lvl}**!")

    @staticmethod
    def retroactive_leveling_hypixel(current_level, old_exp, added_exp):
        exp_dynamic = old_exp
        exp_left = added_exp
        level = current_level

        while exp_left > 0:
            exp_to_next_level = 5 * (level ** 2) + (50 * level) + 100 - exp_dynamic

            if exp_left >= exp_to_next_level:
                exp_dynamic += exp_to_next_level
                exp_left -= exp_to_next_level
                level += 1

            else:
                exp_dynamic += exp_left
                exp_left -= exp_left

        return {"expAdded": exp_dynamic - old_exp, "levelsAdded": level - current_level, "exp": exp_dynamic, "level": level}
