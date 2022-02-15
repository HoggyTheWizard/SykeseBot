from discord.commands import user_command, Option, SlashCommandGroup
from bot.utils.UI.report_modal import ReportModal
from bot.utils.Checks.user import mod
from db import main_db
from discord.ext import commands
from bot import variables as v
import discord

users = main_db["users"]
reports = main_db["reports"]
archived_reports = main_db["archived_reports"]


class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    report = SlashCommandGroup("report", "Report a user to the moderators.", guild_ids=v.guilds)

    @user_command(name="Report", guild_ids=v.guilds)
    async def report_user(self, ctx, member):
        modal = ReportModal(title=f"Report Against {str(member)}", ctx=ctx, member=member)
        await ctx.interaction.response.send_modal(modal)

    @report.command(guild_ids=v.guilds, description="Report a user to the moderators.")
    async def create(self, ctx, member: Option(discord.Member, "The member you want to report")):
        modal = ReportModal(title=f"Report Against {str(member)}", ctx=ctx, member=member)
        await ctx.interaction.response.send_modal(modal)

    @report.command(description="Staff Only - Handle a Report")
    @mod()
    async def handle(self, ctx, report_id: int,
                     status: Option(str, "The status of the report", choices=["Accepted", "Not Enough Evidence",
                                                                              "Denied"]),
                     reason: Option(str, "The reason for the response")
                     ):
        report = reports.find_one({"id": report_id})
        if report_id is None:
            await ctx.respond("That report doesn't exist.")
        else:
            reporter = users.find_one({"id": report["reporter"]})
            data = {
                "status": status,
                "activeReports": reporter.get("activeReports", 1) - 1
            }
            if status == "Accepted":
                data["totalAcceptedReports"] = reporter.get("totalAcceptedReports", 0) + 1
            elif status == "Not Enough Evidence":
                data["totalNotEnoughEvidenceReports"] = reporter.get("totalNotEnoughEvidenceReports", 0) + 1
            elif status == "Denied":
                data["totalDeniedReports"] = reporter.get("totalDeniedReports", 0) + 1

            users.update_one({"id": report["reporter"]}, {"$set": {data}})


def setup(bot):
    bot.add_cog(Report(bot))
