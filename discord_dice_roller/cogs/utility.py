"""Cog for utility commands like clean up or about"""

# Built-in
import time

# Third-party
from discord.ext import commands

# Application
from utils.cog import ImprovedCog
from utils.embed import create_embed, create_error_embed

# --------------------------------------------------------------------------------
# > Constants
# --------------------------------------------------------------------------------
HELP_TEXT = """```yaml
# Rolling dice
reroll                           Rolls the dice using the same settings as the user's last valid dice roll
roll [instruction]*              Rolls the dice using the provided instructions
use [shortcut] ?[instruction]*   Rolls the dice using a user's shortcut and maybe additional instructions

# Shortcut management
remove [shortcut]                Removes one specific shortcut for the user
removeall                        Removes all of the user's shortcuts
save [shortcut] [instruction]*   Creates a new shortcut mapped to those instructions for the user
show                             Shows the list of existing shortcuts for the user

# Utility
about                            Provides a recap of the bot main information
clear [qty]                      Checks the N last messages and removes those that are command calls or belongs to the bot
help                             Shows THIS message
ping                             Simply checks if the bot is up and running
@DiceRoller                      Mention him to know what command prefix he responds to

# Settings
setprefix [value]                Change the command prefix at the guild/server level. Needs admin privileges
settings ?[name=value]*          Shows the user current settings and allows editing on the fly
```"""

MORE_INFO_TEXT = """
For more details, checkout those links:
- [Commands](https://jordan-kowal.github.io/discord-dice-roller/#command-list)
- [Roll instructions](https://jordan-kowal.github.io/discord-dice-roller/#roll-instructions)
- [Settings](https://jordan-kowal.github.io/discord-dice-roller/#settings)
"""

ABOUT_TEXT = """
Author: **Jordan Kowal**
Version: **`v1.0.0`**
Useful Links: **[Official Page](https://jordan-kowal.github.io/discord-dice-roller/)** || \
**[GitHub repository](https://github.com/Jordan-Kowal/discord-dice-roller)**
"""


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class UtilityCog(ImprovedCog):
    """
    Provides utility commands such as:
        > about     Provides a recap of the bot information
        > ping      Checks if the bot is up
        > clear     Checks the last N messages in the channel and remove both commands and bot messages
    """

    # ----------------------------------------
    # about
    # ----------------------------------------
    @commands.command()
    async def about(self, ctx):
        """Provides a recap of the bot information"""
        self.log_command_call("about", ctx.message)
        embed = create_embed(description=ABOUT_TEXT)
        await ctx.send(embed=embed)

    @about.error
    async def about_error(self, ctx, error):
        """Base error handler for the `about` command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # help
    # ----------------------------------------
    @commands.command()
    async def help(self, ctx):
        """Checks if the bot is up"""
        self.log_command_call("help", ctx.message)
        await ctx.send(HELP_TEXT)
        embed_output = create_embed(description=MORE_INFO_TEXT)
        await ctx.send(embed=embed_output)

    @help.error
    async def help_error(self, ctx, error):
        """Base error handler for the `help` command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # ping
    # ----------------------------------------
    @commands.command()
    async def ping(self, ctx):
        """Checks if the bot is up"""
        self.log_command_call("ping", ctx.message)
        embed_output = create_embed(description="pong")
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
