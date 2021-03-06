from discord.ui import InputText, Modal
from db import main_db
from discord.ext import commands
import discord

users = main_db["users"]
reports = main_db["reports"]


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
        print("triggered callback")
        await interaction.response.defer()
        user = users.find_one({"id": self.ctx.author.id})
        if self.ctx.author.id == self.member.id:
            await interaction.response.send_message("You can't report yourself.", delete_after=3)
            return

        elif 891123241765179472 in [role.id for role in self.member.roles]:
            await interaction.response.send_message("You can't report a staff member.", delete_after=3)
            return

        elif user is None or user.get("Reports", None) is None or user["Reports"].get("activeReports", 0) >= 3:
            await interaction.response.send_message("You can't have more than 3 active reports open at once. "
            "Please be patient as your pending reports are reviewed by a moderator.", delete_after=5)
            return

        else:

            embed = discord.Embed(title=f"New Report | #{reports.count_documents({}) + 1}", color=discord.Color.red())
            embed.add_field(name="Submitted By:", value=f"{interaction.user.mention}")
            embed.add_field(name="Reported User:", value=self.member.mention)
            embed.add_field(name="Report Tile:", value=self.children[0].value, inline=False)
            embed.add_field(name="Report Details", value=self.children[1].value or "No Details Provided.", inline=False)
            log = await self.ctx.guild.get_channel(942853283662397440).send(embed=embed)

            report_data = user.get("Reports", {})
            report_data["activeReports"] = report_data.get("activeReports", 0)
            report_data["reports"] = report_data.get("reports", 0)
            users.update_one({"id": self.ctx.author.id}, {"$set": {
                "Reports.activeReports": report_data["activeReports"] + 1,
                "Reports.reports": report_data["reports"] + 1}})

            member_collection = users.find_one({"id": self.member.id})
            if member_collection is not None:
                member_report_data = member_collection.get("Reports", {"totalTimesReported": 0})
                users.update_one({"id": self.member.id}, {"$set": {
                    "Reports.totalTimesReported": member_report_data.get("totalTimesReported", 0) + 1}})

            reports.insert_one({"id": reports.count_documents({}) + 1, "messageID": log.id,
                                "reporter": self.ctx.author.id, "offender": self.member.id,
                                "title": self.children[0].value, "details": self.children[1].value or None,
                                "status": "ACTIVE"})

            await interaction.response.send_message("Report submitted!", delete_after=5)
