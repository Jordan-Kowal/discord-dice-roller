"""Utilities for command cogs"""

# Built-in
import logging

# Third-party
from discord.ext import commands

# Local
from .embed import create_error_embed
from .settings import get_command_prefix


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class ImprovedCog(commands.Cog):
    """Extends Cog to provide various utilities"""

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
        message = f"Command '{ctx.command}': {error} "
        logging.error(message)
        prefix = get_command_prefix(self.bot, ctx.message)
        description = """
            Did you forget a required arguments in your command?
            Use `{{prefix}}help` or check the [official documentation](https://jordan-kowal.github.io/discord-dice-roller/).
            If you believe you found a bug, please open a [bug report here](https://github.com/Jordan-Kowal/discord-dice-roller/issues/new).
        """.replace(
            "{{prefix}}", prefix
        )
        embed = create_error_embed(
            title=self.default_error_message,
            description=description,
        )
        await ctx.send(embed=embed)

    @staticmethod
    def log_command_call(name, message):
        """
        Logs the command call in the console and log file
        Does not crash in case of failure
        :param str name: Name of the command
        :param Message message: The discord message that triggered the call
        :return:
        """
        try:
            logging.info(
                f"User {message.author.id} triggered '{name}' with: {message.content}"
            )
        except Exception:
            pass
