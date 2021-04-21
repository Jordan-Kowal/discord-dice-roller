"""Cog for changing/customizing the bot settings"""


# Built-in
import json
import re

# Third-party
from discord.ext import commands

# Application
from discord_dice_roller.utils.cog import ImprovedCog
from discord_dice_roller.utils.dice_roll import (
    CHECK_REGEX,
    COMPLEX_ACTION_REGEX,
    DICE_REGEX,
    MODIFIER_REGEX,
    SIMPLE_ACTION_REGEX,
    DiceRoll,
    generate_discord_markdown_string,
)
from discord_dice_roller.utils.embed import create_embed, create_error_embed
from discord_dice_roller.utils.files import USER_SETTINGS_FILEPATH


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class ConfigCog(ImprovedCog):
    """Allows user to customize some settings for themselves or their guild"""

    # ----------------------------------------
    # save
    # ----------------------------------------
    @commands.command()
    async def save(self, ctx, name, *args):
        """Creates a shortcut for a group of roll instructions"""
        errors = self._validate_set_instructions(name, *args)
        if len(errors) > 0:
            description = "\n".join(errors)
            embed = create_error_embed(description=description)
        else:
            user_str_id = str(ctx.message.author.id)
            instructions_as_string = " ".join(args)
            # Fetch settings
            with open(USER_SETTINGS_FILEPATH, "r") as f:
                content = json.load(f)
            # Update user data
            user_content = content.get(user_str_id, {})
            user_content[name] = instructions_as_string
            content[user_str_id] = user_content
            # Write back in file
            with open(USER_SETTINGS_FILEPATH, "w") as f:
                json.dump(content, f)
            description = (
                f"The `{name}` shortcut now points to `{instructions_as_string}`"
            )
            embed = create_embed(title="Settings updated!", description=description)
        await ctx.send(embed=embed)

    @save.error
    async def save_error(self, ctx, error):
        """Base error handler for the !save command"""
        await self.log_error_and_apologize(ctx, error)

    @staticmethod
    def _validate_set_instructions(name, *args):
        """
        Checks if the `name` and the `args` are valid
        If not, append errors to the list
        :param str name: Name of the shortcut
        :param [str] args: Supposedly DiceRoll instructions
        :return: The list of error messages
        :rtype: [str]
        """
        errors = []
        for regex in [
            CHECK_REGEX,
            COMPLEX_ACTION_REGEX,
            DICE_REGEX,
            MODIFIER_REGEX,
            SIMPLE_ACTION_REGEX,
        ]:
            match = re.fullmatch(regex, name)
            if match is not None:
                errors.append(
                    "[Shortcut] Cannot use an actual roll instruction as a shortcut"
                )
                break
        if len(args) == 0:
            errors.append(
                "[DiceRoll] Please provide instructions after your shortcut name"
            )
        else:
            dice_roll = DiceRoll(args)
            errors.extend(dice_roll.errors)
        return errors

    # ----------------------------------------
    # show
    # ----------------------------------------
    @commands.command()
    async def show(self, ctx):
        """Shows the current shortcuts for the user"""
        user_str_id = str(ctx.message.author.id)
        with open(USER_SETTINGS_FILEPATH, "r") as f:
            content = json.load(f)
        shortcuts = content.get(user_str_id, None)
        if shortcuts is None:
            description = "Looks like you have no existing shortcuts!"
            embed = create_error_embed(description=description)
        else:
            description = "\n".join([f"{k}: {v}" for k, v in shortcuts.items()])
            description = generate_discord_markdown_string([description])
            embed = create_embed(
                title="Here are your shortcuts:", description=description
            )
        await ctx.send(embed=embed)

    @show.error
    async def show_error(self, ctx, error):
        """Base error handler for the !show command"""
        await self.log_error_and_apologize(ctx, error)
