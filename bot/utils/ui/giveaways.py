from db import main_db
import discord

giveaways = main_db["giveaways"]
users = main_db["users"]


class GiveawayButton(discord.ui.Button):
    def __init__(self, giveaway: dict):
        self.giveaway = giveaway
        super().__init__(
            label="Enter",
            style=discord.ButtonStyle.blurple,
            custom_id=giveaway["id"],
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        giveaway = self.giveaway

        if member.id in giveaway["participants"]:
            await interaction.response.send_message("You're already entered this giveaway.")
        if giveaway["requirements"] == "none":
            await enter_giveaway(interaction, giveaway)

        else:
            user = users.find_one({"id": member.id})
            level = user.get("Leveling", {}).get("level", 0)

            if "level" in giveaway["requirements"]:
                giveaway_level = giveaway["requirements"].replace("level_", "")

                if level >= int(giveaway_level):
                    await enter_giveaway(interaction, giveaway)
                else:
                    await not_eligible(interaction)


async def enter_giveaway(interaction, giveaway):
    users.update_one(
        {"id": interaction.user.id}, {"$inc": {"giveawaysEntered": 1}}
    )
    participants = giveaway["participants"]
    participants.append(interaction.user.id)

    giveaways.update_one(
        {"id": giveaway["id"]}, {"$set": {"participants": participants}}
    )
    await interaction.response.send_message(f"Successfully entered the giveaway! Check back in "
                                            f"<t:{giveaway['timestamp']}:R> to see the results.", ephemeral=True)


async def not_eligible(interaction):
    await interaction.response.send_message("You are not eligible to enter this giveaway. Please review the giveaway "
                                            "requirements listed in the giveaway post.", ephemeral=True)
