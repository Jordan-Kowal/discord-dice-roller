"""Cog for utility commands like !help or !info"""


# Built-in
import os
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
    """TBD"""

    # ----------------------------------------
    # Help
    # ----------------------------------------
    @commands.command()
    async def help(self, ctx, *args):
        """TBD"""
        pass

    @help.error
    async def help_error(self, ctx, error):
        """Base error handler for the !help command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # info
    # ----------------------------------------
    @commands.command()
    async def info(self, ctx, *args):
        """TBD"""
        pass

    @info.error
    async def info_error(self, ctx, error):
        """Base error handler for the !info command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # ping
    # ----------------------------------------
    @commands.command()
    async def ping(self, ctx, *args):
        """Checks if the bot is up"""
        embed_output = create_embed(title="pong")
        await ctx.send(embed=embed_output)

    @ping.error
    async def ping_error(self, ctx, error):
        """Base error handler for the !ping command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # clear
    # ----------------------------------------
    @commands.command()
    async def clear(self, ctx, *args):
        """Checks the last N messages in the channel and remove both commands and bot messages"""
        is_valid, limit, error_message = self._validate_clear_args(*args)
        if not is_valid:
            error_embed = create_error_embed(description=error_message)
            await ctx.send(embed=error_embed)
        else:
            limit += 1  # To account for THIS command call
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
        """Base error handler for the !clear command"""
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

    def _validate_clear_args(*args):
        """
        Checks we only got 1 arg and it's a int between MIN_LIMIT and MAX_LIMIT
        :param [str] args: The user's instructions
        :return: Whether the args were valid, their value, and the error message
        :rtype: bool, int or None, str
        """
        min_limit = 1
        max_limit = 20
        default_error = f"[Limit] The `limit` argument must be a number between {min_limit} and {max_limit}"
        if len(args) != 1:
            error = f"[Limit] This command expects only 1 argument, a number between {min_limit} and {max_limit}"
            return False, None, error
        try:
            limit = int(args[0])
        except ValueError:
            return False, None, default_error
        if not (min_limit <= limit <= max_limit):
            return False, None, default_error
        return True, limit, ""
