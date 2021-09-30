from discord.ext import commands
from pathlib import Path
import logging
import config

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

    async def on_command_error(self, ctx: commands.Context, exc):
        if isinstance(exc, commands.CommandNotFound):
            return

        if isinstance(exc, commands.MissingRequiredArgument):
            await ctx.send(f"Invalid Command Format: {ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}")
            return

        log.error("", exc_info=exc)

        await ctx.send(exc)
