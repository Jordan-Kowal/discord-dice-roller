"""Main file for our bot"""

# Built-in
import os
import random

# Third-party
from discord.ext import commands
from dotenv import load_dotenv

# Application
from discord_dice_roller.cogs import DiceRollingCog, UtilityCog
from discord_dice_roller.utils.logging import setup_logging

# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # Env setup
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    random.seed()
    # Logging setup
    setup_logging()
    # Bot setup
    bot = commands.Bot(command_prefix=os.getenv("COMMAND_PREFIX"), help_command=None)
    bot.add_cog(DiceRollingCog(bot))
    bot.add_cog(UtilityCog(bot))
    # Execute
    bot.run(TOKEN)
