"""Commands related to rolling the dice"""

# Built-in
import re
from enum import Enum

# Third-party
from discord.ext import commands


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class DiceRolling(commands.Cog):
    """Commands related to rolling dice"""

    def __init__(self, bot):
        """
        Initializes the instance
        :param discord.ext.commands.Bot bot:
        """
        self.bot = bot

    # ----- Commands -----
    @commands.command()
    async def roll(self, ctx, *args):
        """Rolls the dice using the provided instructions"""
        DiceRoll(args)
        await ctx.send("Received")

    @roll.error
    async def roll_error(self, ctx, error):
        """Error handler for `roll`"""
        await ctx.send("Oops, something went wrong! :(")

    @commands.command()
    async def reroll(self, ctx, *args):
        """Rolls the dice using the player's last instructions"""
        await ctx.send("Received")

    @roll.error
    async def reroll_error(self, ctx, error):
        """Error handler for `reroll`"""
        await ctx.send("Oops, something went wrong! :(")


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
DICE_REGEX = re.compile(r"(?P<qty>\d{1,2})d(?P<value>\d{1,3})")
MODIFIER_REGEX = re.compile(r"[-+]\d{1,3}")
ACTION_REGEX = re.compile(r"[kd]\d{1,3}")
CHECK_REGEX = re.compile(r"(?P<comparator>=|!=|>|<|>=|<=)(?P<value>\d{1,3})")
OPTION_REGEX = re.compile(r"--(?P<option>verbose|debug)")


class RollAction(Enum):
    """List of available actions when rolling dice"""

    DROP = "d"
    KEEP = "k"


class RollOption(Enum):
    """List of options when rolling dice"""

    VERBOSE = "verbose"
    DEBUG = "debug"


class DiceRoll:
    """An individual dice roll made from the user's instructions"""

    # Roll attributes
    dice = []  # [(1, 6)]
    modifier = None  # -7
    action = None  # (RollAction.KEEP, 3)
    check = None  # (">=", 4)
    options = []  # [RollOption.VERBOSE]

    # Validators
    parsing_errors = []
    logic_errors = []
    match_tracking = {
        "modifier": [],
        "action": [],
        "check": [],
    }

    def __init__(self, instructions):
        """
        Parses and sets the instance attributes. Also computes errors.
        :param [str] instructions: The arguments from the !roll command
        """
        self.instructions = instructions
        self._parse_input()
        self._check_data_integrity()

    def roll(self):
        """TBD"""
        if not self.is_valid:
            raise RuntimeError("Cannot roll the dice, instructions are invalid.")

    @property
    def error_messages(self):
        """
        :return: Our instance's error messages (compute during __init__)
        :rtype: [str]
        """
        return self.parsing_errors + self.logic_errors

    @property
    def is_valid(self):
        """
        :return: Whether the instance is valid and the dice can be rolled
        :rtype: bool
        """
        return len(self.parsing_errors) == len(self.logic_errors) == 0

    # ----------------------------------------
    # Private
    # ----------------------------------------
    def _check_data_integrity(self):
        """Check if the parsed instructions are actually usable"""
        if not self._check_has_dice():
            return
        self._check_instruction_stacks()
        if self.action is not None:
            self._check_action_is_possible()

    def _check_has_dice(self):
        """Checks if our instance has dice"""
        if len(self.dice) == 0:
            self.logic_errors.append(
                "You did not provide dice to roll (example: 2d10)."
            )
            return False
        return True

    def _check_instruction_stacks(self):
        """Checks that we have 0-to-1 instruction for modifier/action/check"""
        for key, values in self.match_tracking.items():
            if len(values) > 1:
                self.logic_errors.append(
                    f"{key}: Expected at most 1 value, but you provided multiple ({values})."
                )

    def _check_action_is_possible(self):
        """Checks if the keep/drop action can technically be performed"""
        if len(self.dice) > 1:
            self.logic_errors.append(f"Cannot use keep/drop when using different dice.")
        else:
            dice_count = sum([die[0] for die in self.dice])
            amount = self.action[1]
            if amount >= dice_count:
                self.logic_errors.append(
                    f"Cannot keep/drop more dice than you are roll (dice: {dice_count}, keep/drop: {amount}."
                )

    def _parse_input(self):
        """Parses the user input to update the instance's properties"""
        for instruction in self.instructions:
            # Dice
            match = re.fullmatch(DICE_REGEX, instruction)
            if match is not None:
                qty = int(match.group("qty"))
                value = int(match.group("value"))
                self.dice.append((qty, value))
                continue
            # Modifier
            match = re.fullmatch(MODIFIER_REGEX, instruction)
            if match is not None:
                self.modifier = int(instruction)
                self.match_tracking["modifier"].append(instruction)
                continue
            # Action
            match = re.fullmatch(ACTION_REGEX, instruction)
            if match is not None:
                action = RollAction(instruction[0])
                value = int(instruction[1:])
                self.action = (action, value)
                self.match_tracking["action"].append(instruction)
                continue
            # Check
            match = re.fullmatch(CHECK_REGEX, instruction)
            if match is not None:
                comparator = match.group("comparator")
                value = int(match.group("value"))
                self.check = (comparator, value)
                self.match_tracking["check"].append(instruction)
                continue
            # Options
            match = re.fullmatch(OPTION_REGEX, instruction)
            if match is not None:
                option_value = match.group("option")
                option = RollOption(option_value)
                self.options.append(option)
                continue
            # Errors
            self.parsing_errors.append(f"Invalid instruction: {instruction}")


# Rules:
#   Keep/Drop value cannot exceed equal or exceed number of dices
#   Keep/Drop only available if 1 type of dice
