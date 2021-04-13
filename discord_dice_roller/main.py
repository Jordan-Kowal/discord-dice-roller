"""Main file for our bot"""

# Built-in
import os

# Third-party
from discord.ext import commands
from discord_dice_roller.cogs import DiceRolling
from dotenv import load_dotenv

# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # Env setup
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    # Bot setup
    bot = commands.Bot(command_prefix="!")
    bot.add_cog(DiceRolling(bot))
    # Execute
    bot.run(TOKEN)
