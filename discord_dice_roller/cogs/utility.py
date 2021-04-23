"""Cog for utility commands like clean up or info"""

# Built-in
import time

# Third-party
from discord.ext import commands

# Local
from ..utils.cog import ImprovedCog
from ..utils.embed import create_embed, create_error_embed


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class UtilityCog(ImprovedCog):
    """
    Provides utility commands such as:
        > info      Provides a recap of the bot information
        > ping      Checks if the bot is up
        > clear     Checks the last N messages in the channel and remove both commands and bot messages
    """

    # ----------------------------------------
    # info
    # ----------------------------------------
    @commands.command()
    async def info(self, ctx):
        """Provides a recap of the bot information"""
        self.log_command_call("info", ctx.message)
        lines = [
            "Author: **Jordan Kowal**",
            "GitHub: **[Link](https://github.com/Jordan-Kowal/discord-dice-roller)**",
            "Version: **`1.0`**",
            "Licence: **MIT - opensource**",
        ]
        embed = create_embed(description="\n".join(lines))
        await ctx.send(embed=embed)

    @info.error
    async def info_error(self, ctx, error):
        """Base error handler for the `info` command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # ping
    # ----------------------------------------
    @commands.command()
    async def ping(self, ctx):
        """Checks if the bot is up"""
        self.log_command_call("ping", ctx.message)
        embed_output = create_embed(title="pong")
        await ctx.send(embed=embed_output)

    @ping.error
    async def ping_error(self, ctx, error):
        """Base error handler for the `ping` command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # clear
    # ----------------------------------------
    @commands.command()
    async def clear(self, ctx, limit):
        """Checks the last N messages in the channel and remove both commands and bot messages"""
        self.log_command_call("clear", ctx.message)
        error = self._validate_clear_args(limit)
        if error is not None:
            error_embed = create_error_embed(description=error)
            await ctx.send(embed=error_embed)
        else:
            limit = int(limit) + 1  # To account for THIS command call
            await ctx.channel.purge(
                limit=limit, check=lambda msg: self._should_delete(msg, ctx)
            )
            # Send some feedback
            auto_destruct_timer = 5
            feedback_embed = create_embed(
                title="Purge recap",
                description=f"Check the last {limit-1} message for deletion",
            )
            feedback_embed.set_footer(
                text=f"This message will auto-destruct in {auto_destruct_timer} seconds"
            )
            message = await ctx.send(embed=feedback_embed)
            # Then we delete the call and our feedback
            time.sleep(auto_destruct_timer)
            await ctx.message.delete()
            await message.delete()

    @clear.error
    async def clear_error(self, ctx, error):
        """Base error handler for the `clear` command"""
        await self.log_error_and_apologize(ctx, error)

    def _should_delete(self, msg, ctx):
        """
        Predicate to choose which message to delete in the `purge` API
        :param Message msg: Any discord message we are reading through
        :param Context ctx: The command call context
        :return: Whether the message should be deleted
        :rtype: bool
        """
        # Do not remove the user's call
        if msg.id == ctx.message.id:
            return False
        # Remove command calls
        if msg.content.startswith(ctx.prefix):
            return True
        # Remove our bot's messages
        if msg.author == self.bot.user:
            return True
        return False

    @staticmethod
    def _validate_clear_args(limit):
        """
        Checks we got a `limit` within the right range
        :param str limit: The provided quantity of messages to check
        :return: The error message, if there's any
        :rtype: str or None
        """
        min_limit = 1
        max_limit = 20
        default_error = f"[Limit] The `limit` argument must be a number between {min_limit} and {max_limit}"
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            return default_error
        if not (min_limit <= limit <= max_limit):
            return default_error
        return None
