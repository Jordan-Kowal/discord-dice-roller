"""Utilities shared across the whole cog"""

# Built-in
import random
import re

# Third-party
from discord import Color

# Application
from discord_dice_roller.utils.embed import create_embed, create_error_embed

# --------------------------------------------------------------------------------
# > Constants
# --------------------------------------------------------------------------------
DICE_REGEX = re.compile(r"(?P<qty>[1-9]\d{0,2})d(?P<sides>[1-9]\d{0,2})")
SIMPLE_ACTION_REGEX = re.compile(r"adv|dis|crit")
COMPLEX_ACTION_REGEX = re.compile(r"(?P<action>dl|dh|kl|kh)(?P<value>[1-9]\d{0,2})")
CHECK_REGEX = re.compile(r"(?P<comparator>=|!=|>|<|>=|<=)(?P<value>[1-9]\d{0,4})")
MODIFIER_REGEX = re.compile(r"[-+][1-9]\d{0,4}")


# --------------------------------------------------------------------------------
# > Base helpers
# --------------------------------------------------------------------------------
def generate_discord_markdown_string(lines):
    """
    Wraps a list of message into a discord markdown block
    :param [str] lines:
    :return: The wrapped string
    :rtype: str
    """
    output = ["```markdown"] + lines + ["```"]
    return "\n".join(output)


class Die:
    """A die you can roll"""

    def __init__(self, sides):
        """
        Creates a die of N sides that can be rolled
        :param int sides: Number of sides the die have
        """
        self.sides = sides
        self.value = None

    def roll(self):
        """
        :return: Rolls the die and returns the value
        :rtype: int
        """
        self.value = random.randint(1, self.sides)
        return self.value

    def copy(self):
        """
        :return: Creates and returns an identical Die from our instance
        :rtype: Die
        """
        die = Die(self.sides)
        die.value = self.value
        return die


class RollComponent:
    """Provides the skeleton for a DiceRoll component"""

    def __init__(self, dice_roll):
        """
        Initializes the component
        :param DiceRoll dice_roll: The DiceRoll instance the component is linked to
        """
        self.dice_roll = dice_roll
        self.errors = []

    def validate(self):
        """Should fill the `errors` property"""
        NotImplemented()

    def apply(self):
        """Should update the `dice_roll.total`"""
        NotImplemented()

    def update_embed(self, embed):
        """
        Should add a field and content to an existing embed
        :param Embed embed: An existing discord Embed message
        """
        NotImplemented()


# --------------------------------------------------------------------------------
# > Modifier Component
# --------------------------------------------------------------------------------
class RollModifier(RollComponent):
    """Applies a modifier at the end of your DiceRoll"""

    def __init__(self, dice_roll, value):
        """
        Initializes the instance
        :param DiceRoll dice_roll: The DiceRoll instance to link it to
        :param int value: The modifier amount (can be negative)
        """
        super().__init__(dice_roll)
        self.value = value

    def validate(self):
        """Adds an error if the value is at 0"""
        if self.value == 0:
            message = "[Modifier] Cannot have a modifier of 0"
            self.errors.append(message)

    def apply(self):
        """Updates the DiceRoll total by adding the modifier value"""
        self.dice_roll.total += self.value

    def update_embed(self, embed):
        """
        Adds a field which indicates the new total after the modifier was applied
        :param Embed embed: The embed massage to update
        """
        sign = "+" if self.value > 0 else "-"
        abs_value = abs(self.value)
        previous_total = self.dice_roll.total - self.value
        message = f"# {previous_total} {sign} {abs_value} = {self.dice_roll.total}"
        text = generate_discord_markdown_string([message])
        embed.add_field(
            name=f"Modifier {sign}{abs_value}", value=text, inline=False,
        )


# --------------------------------------------------------------------------------
# > Check Component
# --------------------------------------------------------------------------------
class RollCheck(RollComponent):
    """Performs a check at the very end of your DiceRoll"""

    def __init__(self, dice_roll, comparator, value):
        """
        Initializes the instance
        :param DiceRoll dice_roll: The DiceRoll instance to link it to
        :param str comparator: Comparaison that will be used, like > or <=
        :param int value: The value on the right side of the equation
        """
        super().__init__(dice_roll)
        self.comparator = comparator
        self.value = value
        self.success = None

    def validate(self):
        """Nothing to validate. Already done by the regex in DiceRoll"""
        pass

    def apply(self):
        """Compares the DiceRoll total to the provided value, using the comparator"""
        self.success = eval(f"{self.dice_roll.total} {self.comparator} {self.value}")

    def update_embed(self, embed):
        """
        Updates the title and color of the message based on the check results
        :param Embed embed: The embed message to update
        """
        if self.success:
            color = Color.green()
            title = f"Success with {self.dice_roll.total}!"
        else:
            color = Color.orange()
            title = f"Failure with {self.dice_roll.total}!"
        embed.title = title
        embed.color = color


# --------------------------------------------------------------------------------
# > Action Component
# --------------------------------------------------------------------------------
def create_roll_action(dice_roll, name, value=0):
    """
    Creates and returns the matching action using the right parameters
    :param DiceRoll dice_roll: The DiceRoll instance to link it to
    :param str name: Name or shortcut of the action
    :param int value: Value associated with the action
    :return: The created BaseAction that matches the provided name
    :rtype: BaseAction
    """
    action_map = {
        "dl": (KeepDropAction, [value, False, False]),
        "dh": (KeepDropAction, [value, False, True]),
        "kl": (KeepDropAction, [value, True, False]),
        "kh": (KeepDropAction, [value, True, True]),
        "adv": (Advantage, []),
        "dis": (Disadvantage, []),
        "crit": (CriticalHit, []),
    }
    action_class, args = action_map[name]
    return action_class(dice_roll, *args)


class BaseAction(RollComponent):
    """Base class to provide utilities to all actual Actions"""

    name = None

    def __init__(self, dice_roll):
        """
        Initializes the action
        :param DiceRoll dice_roll: The DiceRoll instance to link it to
        """
        super().__init__(dice_roll)
        self.dice_roll = dice_roll

    def _validate_one_die(self):
        """Adds an error if there is more than 1 dice"""
        if len(self.dice_roll.dice) != 1:
            message = f"[Action] `{self.name}` action can only be used with 1 die."
            self.errors.append(message)

    def _validate_one_die_type(self):
        """Adds an error if we have several dice types"""
        dice_sides = {die.sides for die in self.dice_roll.dice}
        if len(dice_sides) > 1:
            message = f"[Action] `{self.name}` action cannot be used with dice of different sizes."
            self.errors.append(message)


class Advantage(BaseAction):
    """Action to roll a second die and keep the best one"""

    name = "Advantage"

    def __init__(self, dice_roll):
        """
        Initializes the action and its state
        :param DiceRoll dice_roll: The DiceRoll instance to link it to
        """
        super().__init__(dice_roll)
        self.existing_die = None
        self.die = None

    def validate(self):
        """Checks if the DiceRoll only has one die"""
        self._validate_one_die()

    def apply(self):
        """Copies the existing die, re-rolls it, and keeps it if it's better"""
        self.existing_die = self.dice_roll.dice[0]
        self.die = self.existing_die.copy()
        self.die.roll()
        if self.die.value > self.existing_die.value:
            self.dice_roll.total = self.die.value

    def update_embed(self, embed):
        """
        Adds a field with the action result
        :param Embed embed: Embed message to update
        """
        if self.die.value > self.existing_die.value:
            result = f"Rolled {self.die.value} and kept it!"
        else:
            result = f"Rolled {self.die.value} and discarded it!"
        text = generate_discord_markdown_string([result])
        embed.add_field(
            name=self.name, value=text, inline=False,
        )


class Disadvantage(BaseAction):
    """Action to roll a second die and keep the worse one"""

    name = "Disadvantage"

    def __init__(self, dice_roll):
        """
        Initializes the action and its state
        :param DiceRoll dice_roll: The DiceRoll instance to link it to
        """
        super().__init__(dice_roll)
        self.existing_die = None
        self.die = None

    def validate(self):
        """Checks if the DiceRoll only has one die"""
        self._validate_one_die()

    def apply(self):
        """Copies the existing die, re-rolls it, and keeps it if it's worse"""
        self.existing_die = self.dice_roll.dice[0]
        self.die = self.existing_die.copy()
        self.die.roll()
        if self.die.value < self.existing_die.value:
            self.dice_roll.total = self.die.value

    def update_embed(self, embed):
        """
        Adds a field with the action result
        :param Embed embed: Embed message to update
        """
        if self.die.value < self.existing_die.value:
            result = f"Rolled {self.die.value} and kept it!"
        else:
            result = f"Rolled {self.die.value} and discarded it!"
        text = generate_discord_markdown_string([result])
        embed.add_field(
            name=self.name, value=text, inline=False,
        )


class CriticalHit(BaseAction):
    """Action to make a critical hit and double your dice/damage output"""

    name = "Critical hit"

    def validate(self):
        """Nothing to validate"""
        pass

    def apply(self):
        """Multiplies the dice score by 2"""
        self.before_total = self.dice_roll.total
        self.dice_roll.total *= 2
        self.after_total = self.dice_roll.total

    def update_embed(self, embed):
        """
        Adds a field indicating the new total
        :param Embed embed: Embed message to update
        """
        messages = [
            "All your dice scores are multiplied by 2",
            f"# {self.before_total} x 2 = {self.after_total}",
        ]
        text = generate_discord_markdown_string(messages)
        embed.add_field(
            name=self.name, value=text, inline=False,
        )


class KeepDropAction(BaseAction):
    """Action to keep or drop dice"""

    def __init__(self, dice_roll, amount, keep, high):
        """
        Initializes the action and its state
        :param DiceRoll dice_roll: The DiceRoll instance to link it to
        :param int amount: Amount of dice to keep or drop
        :param bool keep: Whether we keep (or drop)
        :param bool high: Whether the remaining dice are the highest (or lowest)
        """
        super().__init__(dice_roll)
        self.remaining_dice = []
        self.discarded_dice = []
        self.amount = amount
        self.keep = keep
        self.high = high
        self.name = self._compute_name()

    def validate(self):
        """Checks the dice count and types"""
        self._validate_one_die_type()
        self._validate_drop_keep_count(self.amount)

    def apply(self):
        """
        Keeps/drops the dice by splitting them into `remaining` and `discarded`
        Then updates the total by add the `remaining` only
        """
        dice = self.dice_roll.dice.copy()
        dice.sort(key=lambda x: x.value, reverse=self.high)
        if self.keep:
            # Keep High
            if self.high:
                self.remaining_dice = dice[: self.amount]
                self.discarded_dice = dice[self.amount :]
            # Keep Low
            else:
                self.remaining_dice = dice[self.amount :]
                self.discarded_dice = dice[: self.amount]
        else:
            # Drop High
            if self.high:
                self.remaining_dice = dice[self.amount :]
                self.discarded_dice = dice[: self.amount]
            # Drop Low
            else:
                self.remaining_dice = dice[: self.amount]
                self.discarded_dice = dice[self.amount :]
        self.before_total = self.dice_roll.total
        self.dice_roll.total = sum([die.value for die in self.remaining_dice])
        self.after_total = self.dice_roll.total

    def update_embed(self, embed):
        """
        Adds a field which list the discarded and remaining dice
        :param Embed embed: The embed message to update
        """
        remaining_values = [str(die.value) for die in self.remaining_dice]
        discarded_values = [str(die.value) for die in self.discarded_dice]
        messages = [
            f"[Discarded dice]({', '.join(discarded_values)})",
            f"[Remaining dice]({', '.join(remaining_values)})",
            f"Went down from {self.before_total} to {self.after_total}",
        ]
        text = generate_discord_markdown_string(messages)
        embed.add_field(
            name=self.name, value=text, inline=False,
        )

    def _compute_name(self):
        """
        :return: Computes and returns the action name based on its attributes
        :rtype: str
        """
        verb = "Keep" if self.keep else "Drop"
        direction = "high" if self.high else "low"
        return f"{verb} {direction} {self.amount}"

    def _validate_drop_keep_count(self, n):
        """
        Adds an error if we cannot drop/keep that many dice
        :param int n: Number of dice to drop/keep
        """
        if len(self.dice_roll.dice) <= n:
            message = f"[Action] You must roll more dice (`{n}`) than what you drop/keep (`{self.amount}`)."
            self.errors.append(message)


# --------------------------------------------------------------------------------
# > Dice Roll
# --------------------------------------------------------------------------------
class DiceRoll:
    """The state and action of rolling dice with various options"""

    def __init__(self, instructions):
        """
        Initializes the state, then parses and validates the instructions
        :param [str] instructions: The user's instructions, like "1d6" or "adv"
        """
        self.instructions = instructions
        # Roll parameters
        self.dice = []
        self.modifier = None
        self.action = None
        self.check = None
        # Results
        self.total = 0
        self.rolled = False
        # Error control
        self.action_counter = 0
        self.check_counter = 0
        self.modifier_counter = 0
        self._errors = []
        # Parsing
        self._parse_instructions()
        self._validate()

    # ----------------------------------------
    # API properties
    # ----------------------------------------
    @property
    def components(self):
        """
        :return: The ordered component instances linked to our DiceRoll
        :rtype: [RollComponent]
        """
        # Order matters
        potential_components = [self.action, self.modifier, self.check]
        return [c for c in potential_components if c is not None]

    @property
    def is_valid(self):
        """
        :return: Whether the instance is valid and can be played
        :rtype: bool
        """
        return len(self.errors) == 0

    @property
    def errors(self):
        """
        :return: The instance's and its components' errors
        :rtype: [str]
        """
        component_errors = []
        for component in self.components:
            component_errors.extend(component.errors)
        return self._errors + component_errors

    @property
    def errors_as_embed(self):
        """
        :return: Formats the errors into a Discord Embed
        :rtype: Embed
        """
        description = "\n".join(self.errors)
        return create_error_embed(description=description)

    @property
    def result_as_embed(self):
        """
        :return: Formats our instance's result into a Discord Embed
        :rtype: Embed
        """
        title = f"You rolled {self.total}"
        embed = create_embed(title=title)
        self._update_embed_with_dice_rolls(embed)
        for component in self.components:
            component.update_embed(embed)
        return embed

    # ----------------------------------------
    # API methods
    # ----------------------------------------
    def roll(self):
        """
        If valid: rolls the dice, applies all components, and returns the results
        Else: returns the errors
        :return: The embed results or errors
        :rtype: Embed
        """
        # Maybe skip
        if self.rolled:
            raise RuntimeError("This DiceRoll has already been rolled")
        if not self.is_valid:
            return self.errors_as_embed
        # Do roll
        for die in self.dice:
            self.total += die.roll()
        for component in self.components:
            component.apply()
        self.rolled = True
        return self.result_as_embed

    def copy(self):
        """
        :return: A new DiceRoll using our instance's instructions
        :rtype: DiceRoll
        """
        return DiceRoll(self.instructions)

    # ----------------------------------------
    # Helpers: parsing
    # ----------------------------------------
    def _parse_instructions(self):
        """Tries to parse all instruction using our regexes"""
        parsing_functions = [
            self._maybe_parse_dice,
            self._maybe_parse_action,
            self._maybe_parse_modifier,
            self._maybe_parse_check,
        ]
        for instruction in self.instructions:
            for parsing_func in parsing_functions:
                if parsing_func(instruction):
                    break
            else:
                message = (
                    f"[Instruction] Did not understand the instruction: `{instruction}`"
                )
                self._errors.append(message)

    def _maybe_parse_dice(self, instruction):
        """
        Checks if the instruction is a dice roll
        :param str instruction: String to parse
        :return: Whether it was a match
        :rtype: bool
        """
        match = re.fullmatch(DICE_REGEX, instruction)
        if match is not None:
            qty = int(match.group("qty"))
            sides = int(match.group("sides"))
            for i in range(qty):
                self.dice.append(Die(sides))
            return True
        return False

    def _maybe_parse_action(self, instruction):
        """
        Checks if the instruction is an action call
        :param str instruction: String to parse
        :return: Whether it was a match
        :rtype: bool
        """
        match = re.fullmatch(SIMPLE_ACTION_REGEX, instruction)
        if match is not None:
            self.action = create_roll_action(self, instruction)
            self.action_counter += 1
            return True
        match = re.fullmatch(COMPLEX_ACTION_REGEX, instruction)
        if match is not None:
            action_text = match.group("action")
            value = int(match.group("value"))
            self.action = create_roll_action(self, action_text, value)
            self.action_counter += 1
            return True
        return False

    def _maybe_parse_modifier(self, instruction):
        """
        Checks if the instruction is to apply a modifier
        :param str instruction: String to parse
        :return: Whether it was a match
        :rtype: bool
        """
        match = re.fullmatch(MODIFIER_REGEX, instruction)
        if match is not None:
            value = int(instruction)
            self.modifier = RollModifier(self, value)
            self.modifier_counter += 1
            return True
        return False

    def _maybe_parse_check(self, instruction):
        """
        Checks if the instruction is roll check/condition
        :param str instruction: String to parse
        :return: Whether it was a match
        :rtype: bool
        """
        match = re.fullmatch(CHECK_REGEX, instruction)
        if match is not None:
            comparator = match.group("comparator")
            value = int(match.group("value"))
            self.check = RollCheck(self, comparator, value)
            self.check_counter += 1
            return True
        return False

    # ----------------------------------------
    # Helpers: validation
    # ----------------------------------------
    def _validate(self):
        """Checks if our instance and its components are valid based on their states"""
        # Has dice
        if len(self.dice) == 0:
            message = "[Dice] You must provide at least one die (example: `1d6`)"
            self._errors.append(message)
        # Has 1 component of each max
        for text, counter in zip(
            ["Action", "Modifier", "Check"],
            [self.action_counter, self.modifier_counter, self.check_counter],
        ):
            if counter > 1:
                message = f"[{text}] You can only declare 1 {text.lower()} (provided: `{counter}`)"
                self._errors.append(message)
        # We check components only if no error so far
        if len(self._errors) > 0:
            return
        for component in self.components:
            component.validate()

    # ----------------------------------------
    # Helpers: output
    # ----------------------------------------
    def _update_embed_with_dice_rolls(self, embed):
        """
        Adds a `Dice` recap to the embed
        :param Embed embed: The embed to update
        """
        dice_per_sides = {}
        for die in self.dice:
            existing_list = dice_per_sides.get(die.sides, [])
            existing_list.append(die.value)
            dice_per_sides[die.sides] = existing_list
        lines = []
        total_score = 0
        for sides, values in dice_per_sides.items():
            line_score = sum(values)
            total_score += line_score
            string_values = [str(v) for v in values]
            line = f"[{len(values)}d{sides}]({', '.join(string_values)}) = {line_score}"
            lines.append(line)
        lines.append(f"# {total_score}")
        text = generate_discord_markdown_string(lines)
        embed.add_field(
            name=f"Dice rolls", value=text, inline=False,
        )
