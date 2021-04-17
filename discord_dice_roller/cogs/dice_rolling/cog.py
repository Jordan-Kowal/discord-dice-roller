"""Commands related to rolling the dice"""

# Third-party
from discord import Color
from discord.ext import commands

# Local
from .dice_roll import DiceRoll


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class DiceRollingCog(commands.Cog):
    """Provides commands to roll dice with various options"""

    last_roll_per_user = {}
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
        embed_output = dice_roll.roll()
        if dice_roll.is_valid:
            self.last_roll_per_user[user_id] = dice_roll
        await ctx.send(embed=embed_output)

    @roll.error
    async def roll_error(self, ctx, error):
        """Error handler for `roll`"""
        # TODO: Log errors
        print(error)
        await ctx.send(self.default_error_message)

    # @commands.command()
    # async def reroll(self, ctx, *args):
    #     """Rolls the dice using the player's last VALID instructions"""
    #     user_id = ctx.message.author.id
    #     last_dice_roll = self.last_dice_roll_per_user.get(user_id, None)
    #     if last_dice_roll is None:
    #         output = "You have yet to send one valid `!roll` command"
    #     else:
    #         dice_roll = last_dice_roll.copy()
    #         _, output = dice_roll.roll()
    #     await ctx.send(output)
    #
    # @reroll.error
    # async def reroll_error(self, ctx, error):
    #     """Error handler for `reroll`"""
    #     # TODO: Log errors
    #     print(error)
    #     await ctx.send(self.default_error_message)