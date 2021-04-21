"""Module for the RollCheck class"""


# Third-party
from discord import Color

# Local
from .utils import RollComponent


# --------------------------------------------------------------------------------
# > Classes
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
