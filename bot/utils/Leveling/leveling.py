levelup_actions = {
    "15": 933130048192544838, "25": 933130059731066930, "50": 933130064927784970,
    "75": 933130067284992050, "100": 933130061949849691, "125": 933130057063481384,
    "150": 933130054437859428, "175": 933130051522809936, "200": 933130038356877373,
}


def get_leveling(collection):
    obj = collection.get("Leveling", None)
    payload = obj if obj else {"exp": 100, "level": 1}
    xp_needed = 5 * obj["level"] ** 2 + 50 * obj["level"] + 100 - obj["exp"]
    payload["xp_needed"] = xp_needed
    payload["lastTriggeredMessage"] = payload["lastTriggeredMessage"] if "lastTriggeredMessage" in payload else None
    return payload


async def levelup(guild, users, collection, leveling, member, message=None):
    exp = leveling["exp"]
    lvl = leveling["level"]
    # Taken from mee6 (the only good thing they've ever done)
    levelup_xp_needed = 5 * lvl ** 2 + 50 * lvl + 100 - exp
    if exp >= levelup_xp_needed:
        users.update_one({"id": collection["id"]}, {"$inc": {"Leveling.level": 1}})
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
