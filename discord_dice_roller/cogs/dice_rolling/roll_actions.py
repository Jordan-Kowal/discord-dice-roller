"""Module for the all the Action classes"""

# Local
from .utils import RollComponent, generate_discord_markdown_string


# --------------------------------------------------------------------------------
# > Utility
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


# --------------------------------------------------------------------------------
# > Simple Actions
# --------------------------------------------------------------------------------
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


# --------------------------------------------------------------------------------
# > Complex Actions
# --------------------------------------------------------------------------------
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
