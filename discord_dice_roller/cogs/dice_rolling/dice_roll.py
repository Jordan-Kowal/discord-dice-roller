"""Module for the DiceRoll class"""

# Built-in
import re

# Third-party
from discord import Color

# Application
from discord_dice_roller.utils.embed import create_embed

# Local
from .roll_actions import create_roll_action
from .roll_checks import RollCheck
from .roll_modifiers import RollModifier
from .utils import Die, generate_discord_markdown_string

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
DICE_REGEX = re.compile(r"(?P<qty>[1-9]\d{0,2})d(?P<sides>[1-9]\d{0,2})")
SIMPLE_ACTION_REGEX = re.compile(r"adv|dis|crit")
COMPLEX_ACTION_REGEX = re.compile(r"(?P<action>dl|dh|kl|kh)(?P<value>[1-9]\d{0,2})")
CHECK_REGEX = re.compile(r"(?P<comparator>=|!=|>|<|>=|<=)(?P<value>[1-9]\d{0,4})")
MODIFIER_REGEX = re.compile(r"[-+][1-9]\d{0,4}")


# --------------------------------------------------------------------------------
# > DiceRoll
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
        return create_embed(
            title="Woopsie :(", description=description, color=Color.red(),
        )

    @property
    def result_as_embed(self):
        """
        :return: Formats our instance's result into a Discord Embed
        :rtype: Embed
        """
        title = f"You rolled {self.total}"
        embed = create_embed(title=title, description="", color=Color.blue())
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
