from discord.ext import commands
# Settings
exp_for_next_level = 100
exp_for_next_prestige = exp_for_next_level * 25
emoji_id = 678312701205807105

# add role ids
levelup_actions = {
    "10": 933130048192544838, "25": 933130059731066930, "50": 933130064927784970,
    "75": 933130067284992050, "100": 933130061949849691, "125": 933130057063481384,
    "150": 933130054437859428, "175": 933130051522809936, "200": 933130038356877373,
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
            print("triggered levelup")
            users.update_one({"id": collection["id"]}, {"$set": {"Leveling.level": lvl + 1}})
            print(str(lvl+1))
            if str(lvl+1) in levelup_actions:
                print("triggered levelup action")
                role = guild.get_role(levelup_actions[str(lvl+1)])
                print(role)

                if message is None:
                    channel = guild.get_channel(774054508329566209)
                else:
                    channel = message.channel

                # removing all roles that a user has that don't correspond with their level
                same_roles = [x for x in [role.id for role in member.roles]
                              if x in [levelup_actions[x] for x in levelup_actions]]
                for role in same_roles:
                    await member.remove_roles(guild.get_role(role))

                await member.add_roles(role)
                await channel.send(f"Congrats <@{member.id}>, you're now level **{lvl}** and "
                                   f"have received the **{role.name}** role!")
