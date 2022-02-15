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
                     status: Option(str, "The status of the report", choices=["Accepted", "Denied"]),
                     reason: Option(str, "The reason for the response")
                     ):
        report = reports.find_one({"id": report_id})
        if report_id is None or report is None:
            await ctx.respond("That report doesn't exist.")

        elif report.get("status", "ACTIVE") != "ACTIVE":
            await ctx.respond("This report has already been handled.")

        else:
            reporter = users.find_one({"id": report["reporter"]})

            data = reporter.get("Reports", {
                "activeReports": reporter.get("Reports", {"activeReports": 1}).get("activeReports") - 1,
            })

            if status == "Accepted":
                data["totalDeniedReports"] = None
                data["totalAcceptedReports"] = data.get("Reports",
                                                        {"totalAcceptedReports", 0}).get("totalAcceptedReports") + 1

                user_message = (f"[REPORT] After reviewing your report (ID: {report_id}), it has been determined that "
                                f"the user you reported did act in a manner that breaks our community guidelines. "
                                "Thank you for your report!")

            elif status == "Denied":
                data["totalAcceptedReports"] = None
                data["totalDeniedReports"] = data.get("Reports", {"totalDeniedReports": 0}).get("totalDeniedReports") + 1
                user_message = (f"[REPORT] After reviewing your report (ID: {report_id}), it has been determined that "
                                "your report either doesn't feature content breaking our rules or doesn't include "
                                "enough evidence to justify issuing a punishment. If you believe this is false or have " 
                                "additional context/evidence not in the original report, feel free to create a new " 
                                "report.")

            else:
                return

            users.update_one({"id": report["reporter"]}, {"$set": {
                "Reports.activeReports": data["activeReports"],
                "Reports.totalAcceptedReports": data["totalAcceptedReports"],

            }})
            reports.update_one({"id": int(report_id)}, {"$set": {"status": status, "reason": reason,
                                                                 "handledBy": ctx.author.id}})
            try:
                await ctx.guild.get_member(report["reporter"]).send(user_message)
            except:
                pass

            await ctx.respond(f"Handled report #{report_id}")

def setup(bot):
    bot.add_cog(Report(bot))
