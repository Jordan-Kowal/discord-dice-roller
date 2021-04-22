"""Commands related to rolling the dice"""

# Third-party
from discord.ext import commands

# Local
from ..utils.cog import ImprovedCog
from ..utils.dice_roll import DiceRoll
from ..utils.embed import create_warning_embed
from ..utils.settings import get_user_shortcuts


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class DiceRollingCog(ImprovedCog):
    """
    Provides commands to roll dice with various options
        > roll      Rolls the dice using the provided instructions
        > reroll    Rolls the dice using the player's last VALID instructions
        > use       Shows the current shortcuts for the user
    """

    last_roll_per_user = {}

    # ----------------------------------------
    # roll
    # ----------------------------------------
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

    # ----------------------------------------
    # reroll
    # ----------------------------------------
    @commands.command()
    async def reroll(self, ctx, *args):
        """Rolls the dice using the player's last VALID instructions"""
        user_id = ctx.message.author.id
        last_dice_roll = self.last_roll_per_user.get(user_id, None)
        if last_dice_roll is None:
            description = "You have yet to send one valid `!roll` command"
            embed_output = create_warning_embed(description=description)
        else:
            dice_roll = last_dice_roll.copy()
            embed_output = dice_roll.roll()
        await ctx.send(embed=embed_output)

    @reroll.error
    async def reroll_error(self, ctx, error):
        """Base error handler for the !reroll command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # use
    # ----------------------------------------
    @commands.command()
    async def use(self, ctx, name, *args):
        """Rolls the dice using a user's shortcut and maybe additional instructions"""
        user_id = str(ctx.message.author.id)
        _, user_shortcuts = get_user_shortcuts(user_id)
        if name not in user_shortcuts:
            description = f"Found no shortcut with the name `{name}` in your settings"
            embed = create_warning_embed(description=description)
        else:
            shortcut_instructions = user_shortcuts[name].split(" ")
            instructions = shortcut_instructions + list(args)
            dice_roll = DiceRoll(instructions)
            embed = dice_roll.roll()
            if dice_roll.is_valid:
                self.last_roll_per_user[user_id] = dice_roll
        await ctx.send(embed=embed)

    @use.error
    async def use_error(self, ctx, error):
        """Base error handler for the !use command"""
        await self.log_error_and_apologize(ctx, error)
