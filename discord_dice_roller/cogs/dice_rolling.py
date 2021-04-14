"""Commands related to rolling the dice"""

# Built-in
import random
import re
from enum import Enum

# Third-party
from discord.ext import commands


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class DiceRolling(commands.Cog):
    """Commands related to rolling dice"""

    last_dice_roll_per_user = {}
    default_error_message = "Oops, something went wrong! :("

    def __init__(self, bot):
        """
        Initializes the instance
        :param discord.ext.commands.Bot bot:
        """
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, *args):
        """Rolls the dice using the provided instructions"""
        user_id = ctx.message.author.id
        dice_roll = DiceRoll(args)
        if dice_roll.is_valid:
            _, output = dice_roll.roll()
            self.last_dice_roll_per_user[user_id] = dice_roll
        else:
            output = dice_roll.error_output
        await ctx.send(output)

    @roll.error
    async def roll_error(self, ctx, error):
        """Error handler for `roll`"""
        # TODO: Log errors
        print(error)
        await ctx.send(self.default_error_message)

    @commands.command()
    async def reroll(self, ctx, *args):
        """Rolls the dice using the player's last VALID instructions"""
        user_id = ctx.message.author.id
        last_dice_roll = self.last_dice_roll_per_user.get(user_id, None)
        if last_dice_roll is None:
            output = "You have yet to send one valid !roll command"
        else:
            dice_roll = last_dice_roll.copy()
            _, output = dice_roll.roll()
        await ctx.send(output)

    @reroll.error
    async def reroll_error(self, ctx, error):
        """Error handler for `reroll`"""
        # TODO: Log errors
        print(error)
        await ctx.send(self.default_error_message)


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
DICE_REGEX = re.compile(r"(?P<qty>\d{1,2})d(?P<value>\d{1,3})")
MODIFIER_REGEX = re.compile(r"[-+]\d{1,3}")
SIMPLE_ACTION_REGEX = re.compile(r"adv|dis")
COMPLEX_ACTION_REGEX = re.compile(r"(?P<action>dl|dh|kl|kh)(?P<value>\d{1,3})")
CHECK_REGEX = re.compile(r"(?P<comparator>=|!=|>|<|>=|<=)(?P<value>\d{1,3})")
OPTION_REGEX = re.compile(r"--(?P<option>verbose|debug)")


class RollAction(Enum):
    """List of available actions when rolling dice"""

    DROP_LOW = "dl"
    DROP_HIGH = "dh"
    KEEP_LOW = "kl"
    KEEP_HIGH = "kh"
    ADVANTAGE = "adv"
    DISADVANTAGE = "dis"


class RollOption(Enum):
    """List of options when rolling dice"""

    VERBOSE = "verbose"
    DEBUG = "debug"


class DiceRoll:
    """An individual dice roll made from the user's instructions"""

    def __init__(self, instructions):
        """
        Parses and sets the instance attributes. Also computes errors.
        :param [str] instructions: The arguments from the !roll command
        """
        random.seed()
        self.instructions = instructions
        self._init_properties()
        self._parse_input()
        self._check_data_integrity()
        if self.is_valid:
            self._maybe_update_instructions()

    @property
    def errors(self):
        """
        :return: Our instance's error messages (compute during __init__)
        :rtype: [str]
        """
        return self.parsing_errors + self.logic_errors

    @property
    def error_output(self):
        """
        :return: The error output for discord
        :rtype: [str]
        """
        return self._format_errors()

    @property
    def result_output(self):
        """
        :return: The result output for discord
        :rtype: str
        """
        return self._format_results()

    @property
    def is_valid(self):
        """
        :return: Whether the instance is valid and the dice can be rolled
        :rtype: bool
        """
        return len(self.parsing_errors) == len(self.logic_errors) == 0

    def copy(self):
        """
        :return: Creates a new DiceRoll instance using this one's instructions
        :rtype: DiceRoll
        """
        return DiceRoll(self.instructions)

    def roll(self):
        """
        Rolls our dice and takes into account all of our settings
        :return: Both the results and formatted results (for discord)
        :rtype: dict, str
        """
        if not self.is_valid:
            raise RuntimeError("Cannot roll the dice, instructions are invalid.")
        self._roll_dice()
        if self.action is not None:
            self._perform_action()
        if self.modifier is not None:
            self._apply_modifier()
        if self.check is not None:
            self._perform_check()
        return self.results, self.result_output

    # ----------------------------------------
    # Init helpers
    # ----------------------------------------
    def _check_data_integrity(self):
        """Check if the parsed instructions are actually usable"""
        if not self._has_dice():
            return
        self._has_no_extra_instructions()
        if self.action is not None:
            self._has_valid_action()

    def _has_dice(self):
        """Checks if our instance has dice"""
        if len(self.dice) == 0:
            self.logic_errors.append(
                "You did not provide dice to roll (example: 2d10)."
            )
            return False
        return True

    def _has_no_extra_instructions(self):
        """Checks that we have 0-to-1 instruction for modifier/action/check"""
        for key, values in self.match_tracking.items():
            if len(values) > 1:
                self.logic_errors.append(
                    f"{key}: Expected at most 1 value, but you provided multiple ({values})."
                )

    def _has_valid_action(self):
        """Checks if the keep/drop action can technically be performed"""
        action, amount = self.action
        # Need at least one die
        if len(self.dice) > 1:
            self.logic_errors.append("Cannot use keep/drop when using different dice.")
            return
        # ADV/DIS actions require only 1 die
        dice_count = sum([die[0] for die in self.dice])
        if action in {RollAction.ADVANTAGE, RollAction.DISADVANTAGE}:
            if dice_count > 1:
                self.logic_errors.append(
                    "When rolling with (dis)advantage, only declare 1 die."
                )
            return
        # KEEP/DROP actions cannot exceed dice count
        if amount >= dice_count:
            self.logic_errors.append(
                f"Cannot keep/drop more dice than you are roll (dice: {dice_count}, keep/drop: {amount})."
            )

    def _init_properties(self):
        """Setups the default values for most properties"""
        # Roll attributes
        self.dice = []  # [(1, 6)]
        self.modifier = None  # -7
        self.action = None  # (RollAction.KEEP, 3)
        self.check = None  # (">=", 4)
        self.options = []  # [RollOption.VERBOSE]
        # Validators
        self.parsing_errors = []
        self.logic_errors = []
        self.match_tracking = {
            "modifier": [],
            "action": [],
            "check": [],
        }
        # Results
        self.results = {
            "dice": [],
            "dice_post_action": [],
            "total": 0,
            "success": None,
        }

    def _maybe_update_instructions(self):
        """Updates the `dice` count if ADV/DIS action"""
        if self.action is None:
            return
        action, amount = self.action
        if action in {RollAction.ADVANTAGE, RollAction.DISADVANTAGE}:
            _, size = self.dice[0]
            self.dice = [(2, size)]

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
            match = re.fullmatch(SIMPLE_ACTION_REGEX, instruction)
            if match is not None:
                action = RollAction(instruction)
                self.action = (action, 1)
                self.match_tracking["action"].append(instruction)
                continue
            # Action again
            match = re.fullmatch(COMPLEX_ACTION_REGEX, instruction)
            if match is not None:
                action_text = match.group("action")
                action = RollAction(action_text)
                value = int(match.group("value"))
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

    # ----------------------------------------
    # Roll helpers
    # ----------------------------------------
    def _apply_modifier(self):
        """Applies the modifier to the total"""
        total = self.results["total"]
        self.results["modifier"] = self.modifier
        self.results["total"] = total + self.modifier

    def _keep_n_dice(self, n, highest):
        """
        Only keeps the n lowest/highest dice and updates the total
        (We assume we only one 1 dice-type)
        :param int n: Amount of dice to keep
        :param bool highest: Whether to keep the highest (or lowest) dice
        """
        rolls = self.results["dice"][0][1].copy()
        rolls.sort(reverse=highest)
        kept_values = rolls[:n]
        self.results["dice_post_action"] = kept_values
        self.results["total"] = sum(kept_values)

    def _perform_action(self):
        """
        Updates the total and dice rolls based on the given action
        Current actions only work with 1-die-type rolls
        """
        action, value = self.action
        dice_count = sum([len(values) for _, values in self.results["dice"]])
        if action == RollAction.DROP_LOW:
            self._keep_n_dice(dice_count - value, True)
        elif action == RollAction.DROP_HIGH:
            self._keep_n_dice(dice_count - value, False)
        elif action == RollAction.KEEP_LOW:
            self._keep_n_dice(value, False)
        elif action == RollAction.KEEP_HIGH:
            self._keep_n_dice(value, True)
        elif action == RollAction.ADVANTAGE:
            self._keep_n_dice(1, True)
        elif action == RollAction.DISADVANTAGE:
            self._keep_n_dice(1, False)

    def _perform_check(self):
        comparator, value = self.check
        success = eval(f"{self.results['total']} {comparator} {value}")
        self.results["success"] = success

    def _roll_dice(self):
        """Rolls the dice, store their results, and updates the total"""
        all_rolls = []
        total = 0
        for quantity, size in self.dice:
            rolls = [random.randint(1, size) for _ in range(quantity)]
            total += sum(rolls)
            all_rolls.append((self.dice, rolls))
        self.results["dice"] = all_rolls
        self.results["total"] = total

    # ----------------------------------------
    # User feedback
    # ----------------------------------------
    def _format_errors(self):
        """
        :return: Formats the error into a user-friendly discord output
        :rtype: str
        """
        return "\n".join(self.errors)

    def _format_results(self):
        """
        :return: Formats the results into a user-friendly discord output
        :rtype: str
        """
        return "\n".join([f"{k}: {v}" for k, v in self.results.items()])
