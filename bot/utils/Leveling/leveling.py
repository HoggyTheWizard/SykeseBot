from discord.ext import commands

exp_for_next_level = 100
exp_for_next_prestige = exp_for_next_level * 25
emoji_id = 678312701205807105

levelup_actions = {
    "5": 933130048192544838, "15": 933130059731066930, "30": 933130064927784970,
    "45": 933130067284992050, "60": 933130061949849691, "75": 933130057063481384,
    "90": 933130054437859428, "105": 933130051522809936, "120": 933130038356877373,
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
    async def levelup(guild, users, collection, leveling, member, message=None):
        exp = leveling.get("exp", 0)
        lvl = leveling.get("level", 0)
        # Taken from mee6 (the only good thing they've ever done)
        levelup_xp_needed = 5 * (lvl ** 2) + (50 * lvl) + 100
        if exp >= levelup_xp_needed:
            users.update_one({"id": collection["id"]}, {"$set": {"Leveling.level": lvl + 1}})
            if str(lvl+1) in levelup_actions:
                added_role = guild.get_role(levelup_actions[str(lvl+1)])
                if message is None:
                    channel = guild.get_channel(889697074491293740)
                else:
                    channel = message.channel

                # removing all roles that a user has that don't correspond with their level
                same_roles = [x for x in [role.id for role in member.roles]
                              if x in [levelup_actions[x] for x in levelup_actions]]
                for role in same_roles:
                    await member.remove_roles(guild.get_role(role))
                await member.add_roles(added_role)
                await channel.send(f"Congrats <@{member.id}>, you're now level **{lvl+1}** and "
                                   f"have received the **{added_role.name}** role!")
