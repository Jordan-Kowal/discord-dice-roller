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
from discord_dice_roller.utils.embed import (
    create_embed,
    create_error_embed,
    create_warning_embed,
)
from discord_dice_roller.utils.files import (
    USER_SHORTCUTS_FILEPATH,
    get_shortcuts_content,
    get_user_shortcuts,
    update_user_shortcuts,
)


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class ConfigCog(ImprovedCog):
    """
    Allows user to customize some settings for themselves or their guild
    Provides the following actions:
        > remove        Deletes an existing shortcut for the user
        > removeall     Deletes all the shortcuts of the user
        > save          Creates a shortcut for a group of roll instructions
        > show          Shows the current shortcuts for the user
    """

    # ----------------------------------------
    # remove
    # ----------------------------------------
    @commands.command()
    async def remove(self, ctx, name):
        """Deletes an existing shortcut for the user"""
        user_id = str(ctx.message.author.id)
        file_content, user_shortcuts = get_user_shortcuts(user_id, {})
        if name not in user_shortcuts.keys():
            description = f"Found no shortcut with the name `{name}` in your settings"
            embed = create_warning_embed(description=description)
        else:
            del user_shortcuts[name]
            update_user_shortcuts(user_id, user_shortcuts, file_content)
            description = f"The `{name}` shortcut has been removed successfully"
            embed = create_embed(title="Settings updated!", description=description)
        await ctx.send(embed=embed)

    @remove.error
    async def remove_error(self, ctx, error):
        """Base error handler for the !remove command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # removeall
    # ----------------------------------------
    @commands.command()
    async def removeall(self, ctx):
        """Deletes all the shortcuts of the user"""
        user_id = str(ctx.message.author.id)
        file_content = get_shortcuts_content()
        if user_id in file_content.keys():
            del file_content[user_id]
        with open(USER_SHORTCUTS_FILEPATH, "w") as f:
            json.dump(file_content, f, indent=2)
        description = "All your shortcuts have been removed"
        embed = create_embed(title="Settings updated!", description=description)
        await ctx.send(embed=embed)

    @removeall.error
    async def removeall_error(self, ctx, error):
        """Base error handler for the !removeall command"""
        await self.log_error_and_apologize(ctx, error)

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
            user_id = str(ctx.message.author.id)
            file_content, user_shortcuts = get_user_shortcuts(user_id, {})
            instructions_as_string = " ".join(args)
            user_shortcuts[name] = instructions_as_string
            update_user_shortcuts(user_id, user_shortcuts, file_content)
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
        content, shortcuts = get_user_shortcuts(ctx.message.author.id)
        if shortcuts is None:
            description = "Looks like you have no existing shortcuts!"
            embed = create_warning_embed(description=description)
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
