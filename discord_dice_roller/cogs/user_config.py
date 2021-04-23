"""Cog allowing users to customize their settings"""


# Built-in
import re

# Third-party
from discord.ext import commands

# Application
from utils.cog import ImprovedCog
from utils.dice_roll import (
    CHECK_REGEX,
    COMPLEX_ACTION_REGEX,
    DICE_REGEX,
    MODIFIER_REGEX,
    SIMPLE_ACTION_REGEX,
    DiceRoll,
    generate_discord_markdown_string,
)
from utils.embed import create_embed, create_error_embed, create_warning_embed
from utils.settings import (
    DEFAULT_USER_SETTINGS,
    get_user_settings,
    get_user_shortcuts,
    update_user_settings,
    update_user_shortcuts,
)


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class UserConfigCog(ImprovedCog):
    """
    Allows user to customize some settings for themselves
    Provides the following actions:
        # Shortcuts
            > remove            Deletes an existing shortcut for the user
            > removeall         Deletes all the shortcuts of the user
            > save              Creates a shortcut for a group of roll instructions
            > show              Shows the current shortcuts for the user
        # Settings
            > settings          Shows the user settings and allows editing on the fly
    """

    MAX_SHORTCUTS = 20

    # ----------------------------------------
    # remove
    # ----------------------------------------
    @commands.command()
    async def remove(self, ctx, name):
        """Deletes an existing shortcut for the user"""
        self.log_command_call("remove", ctx.message)
        user_id = str(ctx.message.author.id)
        user_shortcuts = get_user_shortcuts(user_id)
        if name not in user_shortcuts.keys():
            description = f"Found no shortcut with the name `{name}` in your settings"
            embed = create_warning_embed(description=description)
        else:
            del user_shortcuts[name]
            update_user_shortcuts(user_id, user_shortcuts)
            description = f"The `{name}` shortcut has been removed successfully"
            embed = create_embed(title="Settings updated!", description=description)
        await ctx.send(embed=embed)

    @remove.error
    async def remove_error(self, ctx, error):
        """Base error handler for the `remove` command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # removeall
    # ----------------------------------------
    @commands.command()
    async def removeall(self, ctx):
        """Deletes all the shortcuts of the user"""
        self.log_command_call("removeall", ctx.message)
        user_id = str(ctx.message.author.id)
        user_shortcuts = get_user_shortcuts(user_id)
        if len(user_shortcuts.keys()) == 0:
            description = "Looks like you have no existing shortcuts!"
            embed = create_warning_embed(description=description)
        else:
            update_user_shortcuts(user_id, {})
            description = "All your shortcuts have been removed"
            embed = create_embed(title="Settings updated!", description=description)
        await ctx.send(embed=embed)

    @removeall.error
    async def removeall_error(self, ctx, error):
        """Base error handler for the `removeall` command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # save
    # ----------------------------------------
    @commands.command()
    async def save(self, ctx, name, *args):
        """Creates a shortcut for a group of roll instructions"""
        self.log_command_call("save", ctx.message)
        errors = self._validate_set_instructions(name, *args)
        if len(errors) > 0:
            description = "\n".join(errors)
            embed = create_error_embed(description=description)
        else:
            user_id = str(ctx.message.author.id)
            user_shortcuts = get_user_shortcuts(user_id)
            _max = (
                self.MAX_SHORTCUTS
                if name not in user_shortcuts
                else self.MAX_SHORTCUTS + 1
            )
            if len(user_shortcuts.items()) > _max:
                description = f"Cannot have more than `{self.MAX_SHORTCUTS}` shortcuts. \
                    \nPlease remove some using the `remove` command"
                embed = create_error_embed(description=description)
            else:
                instructions_as_string = " ".join(args)
                user_shortcuts[name] = instructions_as_string
                update_user_shortcuts(user_id, user_shortcuts)
                description = (
                    f"The `{name}` shortcut now points to `{instructions_as_string}`"
                )
                embed = create_embed(title="Settings updated!", description=description)
        await ctx.send(embed=embed)

    @save.error
    async def save_error(self, ctx, error):
        """Base error handler for the `save` command"""
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
            dice_roll = DiceRoll(args, {})
            errors.extend(dice_roll.errors)
        return errors

    # ----------------------------------------
    # show
    # ----------------------------------------
    @commands.command()
    async def show(self, ctx):
        """Shows the current shortcuts for the user"""
        self.log_command_call("show", ctx.message)
        shortcuts = get_user_shortcuts(str(ctx.message.author.id))
        if len(shortcuts.keys()) == 0:
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
        """Base error handler for the `show` command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # settings
    # ----------------------------------------
    @commands.command()
    async def settings(self, ctx, *args):
        """Shows the user settings and allows editing on the fly"""
        self.log_command_call("settings", ctx.message)
        new_settings, errors = self.maybe_parse_args(args)
        # We do not allow invalid args
        if len(errors) > 0:
            description = "\n".join(errors)
            embed = create_error_embed(description=description)
        else:
            user_id = str(ctx.message.author.id)
            user_custom_settings = get_user_settings(user_id)
            # Maybe update settings
            if len(new_settings.keys()) > 0:
                new_user_settings = {**user_custom_settings, **new_settings}
                update_user_settings(user_id, new_user_settings)
            # No need to re-fetch if updated
            user_settings = {
                **DEFAULT_USER_SETTINGS,
                **user_custom_settings,
                **new_settings,
            }
            description = "\n".join([f"{k}: `{v}`" for k, v in user_settings.items()])
            embed = create_embed(
                title="Your current settings are:", description=description
            )
        await ctx.send(embed=embed)

    @settings.error
    async def settings_error(self, ctx, error):
        """Base error handler for the `settings` command"""
        await self.log_error_and_apologize(ctx, error)

    @property
    def available_settings(self):
        """
        :return: Dict of option name to their regex values and their converter
        :rtype: dict
        """
        return {"verbose": ("True|False", self.verbose_converter)}

    @staticmethod
    def verbose_converter(value):
        """
        Converts the True/False string into a boolean
        :param str value: Expecting "True" or "False"
        :return: The boolean value
        :rtype: bool
        """
        return False if value == "False" else True

    def maybe_parse_args(self, args):
        """
        Checks each extra argument and either maps it to a new setting value or adds an error
        :param [str] args: Extra instructions given by the users
        :return: The new settings and the error list
        :rtype: dict, [str]
        """
        errors = []
        updates = {}
        for arg in args:
            matched = False
            for name, (values, converter) in self.available_settings.items():
                regex = re.compile(f"(?P<name>{name})=(?P<value>{values})")
                match = re.fullmatch(regex, arg)
                if match is None:
                    continue
                name = match.group("name")
                value = converter(match.group("value"))
                updates[name] = value
                matched = True
                break
            if not matched:
                message = f"[Instruction] This instruction is invalid: `{arg}`"
                errors.append(message)
        return updates, errors
