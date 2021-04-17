"""Module for the RollModifier class"""

# Local
from .utils import RollComponent, generate_discord_markdown_string


# --------------------------------------------------------------------------------
# > Classes
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
