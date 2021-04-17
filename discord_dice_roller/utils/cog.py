"""Utilities for command cogs"""

# Built-in
import logging

# Third-party
from discord import Color
from discord.ext import commands

# Local
from .embed import create_embed


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class ImprovedCog(commands.Cog):
    """Provides commands to roll dice with various options"""

    default_error_message = "Oops, something went wrong! :("

    def __init__(self, bot):
        """
        Initializes the instance
        :param discord.ext.commands.Bot bot:
        """
        self.bot = bot

    async def log_error_and_apologize(self, ctx, error):
        """
        Logs the error and sends the default error message as embed
        :param ctx:
        :param error:
        """
        message = f"!{ctx.command} {error} "
        logging.error(message)
        embed = create_embed(
            title=self.default_error_message,
            description="Check the logs or contact your administrator for more info",
            color=Color.red(),
        )
        await ctx.send(embed=embed)
