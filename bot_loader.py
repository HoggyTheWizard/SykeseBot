from discord.ext import commands
from discord.commands import core
from pathlib import Path
import logging

log = logging.getLogger(__name__)


class BotLoader(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for ext in Path().glob("bot/cogs/*/*.py"):
            try:
                self.load_extension(".".join(part for part in ext.parts)[:-len(ext.suffix)])
            except Exception:
                log.exception(f"Could not load extension {ext}")

    async def on_ready(self):
        log.info(f"Ready: {self.user} (ID: {self.user.id})")

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, commands.CommandNotFound):
            return
        elif isinstance(exc, commands.MissingRequiredArgument):
            await ctx.send(f"Invalid Command Format: {ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}")
            return
        elif isinstance(exc, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
            return
        else:
            await ctx.send(exc)

    async def on_application_command_error(self, ctx, exc):
        if isinstance(exc, core.CheckFailure):
            pass
        else:
            try:
                await ctx.respond(exc)
            except:
                await ctx.send(exc)
            log.error("", exc_info=exc)
