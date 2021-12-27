import json
import pathlib
import discord

# TODO
# - Inheritance. Add an option for a role to inherit permissions from another role.


def permission_file_names():
    path = pathlib.Path(f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/").glob("**/*")
    files = [file.name.replace(".json", "") for file in path if file.is_file()]
    return files


def highest_perm_role(author: discord.Member):
    if len(author.roles) is False:
        return None
    else:
        files = permission_file_names()
        for role in author.roles:
            if str(role.id) not in files:
                continue
            else:
                return int(role.id)


def generate_permission_list(perm_id: str):
    perm_list = []
    with open(f"{pathlib.Path().resolve()}/bot/utils/Misc/Permissions/{perm_id}.json", "r+") as file:
        data = json.load(file)
        for permission in data.values():
            perm_list.append(permission["id"])
        return perm_list
