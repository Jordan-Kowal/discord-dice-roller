"""Commands related to rolling the dice"""

# Third-party
from discord import Color
from discord.ext import commands

# Application
from discord_dice_roller.utils.cog import ImprovedCog
from discord_dice_roller.utils.dice_roll import DiceRoll
from discord_dice_roller.utils.embed import create_embed


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class DiceRollingCog(ImprovedCog):
    """Provides commands to roll dice with various options"""

    last_roll_per_user = {}

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
        """Base error handler for the !roll command"""
        await self.log_error_and_apologize(ctx, error)

    @commands.command()
    async def reroll(self, ctx, *args):
        """Rolls the dice using the player's last VALID instructions"""
        user_id = ctx.message.author.id
        last_dice_roll = self.last_roll_per_user.get(user_id, None)
        if last_dice_roll is None:
            embed_output = create_embed(
                title="Woopsie! :(",
                description="You have yet to send one valid `!roll` command",
                color=Color.red(),
            )
        else:
            dice_roll = last_dice_roll.copy()
            embed_output = dice_roll.roll()
        await ctx.send(embed=embed_output)

    @reroll.error
    async def reroll_error(self, ctx, error):
        """Error handler for `reroll`"""
        await self.log_error_and_apologize(ctx, error)
