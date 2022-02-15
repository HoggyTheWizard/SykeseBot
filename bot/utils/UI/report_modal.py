from discord.ui import InputText, Modal
from db import main_db
from discord.ext import commands
import discord

users = main_db["users"]


class ReportHandler(commands.CommandError):
    pass


class ReportModal(Modal):
    def __init__(self, ctx, member, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ctx = ctx
        self.member = member

        self.add_item(
            InputText(
                label="Report Reason",
                placeholder="What rule has this user broken?"
            ))

        self.add_item(
            InputText(
                label=f"Detailed Information (Optional)",
                placeholder="Go into detail about what this user has done that goes against our rules.",
                style=discord.InputTextStyle.long,
                max_length=1024,
                required=False
            )
        )

    async def callback(self, interaction: discord.Interaction):
        user = users.find_one({"id": self.ctx.author.id})
        if self.ctx.author.id == self.member.id:
            raise ReportHandler("You can't report yourself.")

        elif 891123241765179472 in [role.id for role in self.ctx.author.roles]:
            raise ReportHandler("You can't report a staff member.")

        elif user is None or user.get("activeReports", 0) >= 3:
            raise ReportHandler("You can't have more than 3 active reports open at once. Please be patient.")

        else:

            embed = discord.Embed(title="New Report", color=discord.Color.red())
            embed.add_field(name="Submitted By:", value=f"{interaction.user.mention}")
            embed.add_field(name="Reported User:", value=self.member.mention)
            embed.add_field(name="Report Tile:", value=self.children[0].value, inline=False)
            embed.add_field(name="Report Details", value=self.children[1].value or "No Details Provided.", inline=False)
            await self.ctx.guild.get_channel(942152380600950824).send(embed=embed)
            await self.ctx.respond("Report submitted!", delete_after=3)

