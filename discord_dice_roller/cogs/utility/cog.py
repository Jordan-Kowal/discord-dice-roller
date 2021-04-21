"""Cog for utility commands like !help or !info"""


# Built-in
import time

# Third-party
from discord import Color
from discord.ext import commands

# Application
from discord_dice_roller.cogs.utility.clear import should_delete, validate_clear_args
from discord_dice_roller.utils.cog import ImprovedCog
from discord_dice_roller.utils.embed import create_embed


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class UtilityCog(ImprovedCog):
    """Provides utility commands to assist our users"""

    @commands.command()
    async def help(self, ctx, *args):
        """TBD"""
        pass

    @help.error
    async def help_error(self, ctx, error):
        """Base error handler for the !help command"""
        await self.log_error_and_apologize(ctx, error)

    @commands.command()
    async def info(self, ctx, *args):
        """TBD"""
        pass

    @info.error
    async def info_error(self, ctx, error):
        """Base error handler for the !info command"""
        await self.log_error_and_apologize(ctx, error)

    @commands.command()
    async def ping(self, ctx, *args):
        """Checks if the bot is up"""
        embed_output = create_embed(title="pong", color=Color.blue())
        await ctx.send(embed=embed_output)

    @ping.error
    async def ping_error(self, ctx, error):
        """Base error handler for the !ping command"""
        await self.log_error_and_apologize(ctx, error)

    @commands.command()
    async def clear(self, ctx, *args):
        """Checks the last N messages in the channel and remove both commands and bot messages"""
        is_valid, limit, error_message = validate_clear_args(*args)
        if not is_valid:
            error_embed = create_embed(
                title="Invalid arguments for this command",
                description=error_message,
                color=Color.red(),
            )
            await ctx.send(embed=error_embed)
        else:
            limit += 1  # To account for THIS command call
            await ctx.channel.purge(
                limit=limit, check=lambda msg: should_delete(msg, self.bot, ctx)
            )
            # Send some feedback
            auto_destruct_timer = 5
            feedback_embed = create_embed(
                title="Purge recap",
                description=f"Check the last {limit-1} message for deletion",
                color=Color.blue(),
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
