"""Cog for changing/customizing the bot settings"""


# Third-party
from discord import Color
from discord.ext import commands

# Application
from discord_dice_roller.utils.cog import ImprovedCog
from discord_dice_roller.utils.embed import create_embed


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class ConfigCog(ImprovedCog):
    """Allows user to customize some settings for themselves or their guild"""

    @commands.command()
    async def setroll(self, ctx, name, *args):
        """TBD"""
        pass

    @setroll.error
    async def setroll_error(self, ctx, error):
        """Base error handler for the !help command"""
        await self.log_error_and_apologize(ctx, error)
