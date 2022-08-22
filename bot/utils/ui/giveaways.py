from db import main_db
import discord

giveaways = main_db["giveaways"]
users = main_db["users"]


class GiveawayViews(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    active = giveaways.find({"active": True})
