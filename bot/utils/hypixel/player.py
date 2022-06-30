from math import sqrt

levels = [(0, 979567551677890620), (50, 979567554794225725), (100, 979801136905220106), (200, 979801189610835969),
          (300, 979801391319113788), (100_000, 979801391319113788)]
ranks = {
    None: {"name": "Non-Ranked", "role": 979566999128666122},
    "VIP": {"name": "VIP", "role": 979567052849315880},
    "VIP_PLUS": {"name": "VIP+", "role": 979567059388223508},
    "MVP": {"name": "MVP", "role": 979567061061750834},
    "MVP_PLUS": {"name": "MVP+", "role": 979567062387159181},
    "SUPERSTAR": {"name": "MVP++", "role": 979567061086900255},
    "YOUTUBER": {"name": "YouTube", "role": 979567061082730527},
    "GAME_MASTER": {"name": "Game Master", "role": 979567327408435230},
    "ADMIN": {"name": "Admin", "role": 979567331556610058},

}


class Player:
    def __init__(self, player: dict):
        self.player = player

    def level(self):
        try:
            network_experience = self.player["player"]["networkExp"]
        except KeyError:
            network_experience = 0

        network_level = (sqrt((2 * network_experience) + 30625) / 50) - 2.5 if network_experience != 0 else 1
        level = int(network_level)

        # Gets a tuple found in levels that corresponds with the user's Hypixel level
        matched = [v[1] for i, v in enumerate(levels) if
                   levels[i][0] <= level < levels[i + 1 if i < len(levels) - 1 else len(levels) - 1][0]]
        # Returns the user's level and the role that corresponds with it (if none found the level is above the highest
        # level listed in the levels dict, so it defaults the highest)
        return level, matched[0] if len(matched) else levels[len(levels) - 1][0]

    def rank(self):
        if "rank" in self.player["player"] and not self.player["player"]["rank"] == "NORMAL":
            rank = self.player["player"]["rank"]

        elif "monthlyPackageRank" in self.player["player"] and not \
                self.player["player"]["monthlyPackageRank"] == "NONE":
            rank = self.player["player"]["monthlyPackageRank"]

        elif "newPackageRank" in self.player["player"]:
            rank = self.player["player"]["newPackageRank"]

        elif "packageRank" in self.player["player"]:
            rank = self.player["player"]["packageRank"]
        else:
            rank = None

        return ranks[rank]
