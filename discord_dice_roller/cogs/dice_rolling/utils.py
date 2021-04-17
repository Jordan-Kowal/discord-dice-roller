"""Utilities shared across the whole cog"""

# Built-in
import random


# --------------------------------------------------------------------------------
# > Functions
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


# --------------------------------------------------------------------------------
# > Classes
# --------------------------------------------------------------------------------
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
