"""Main file for our bot"""

# Built-in
import os
import random

# Third-party
from discord.ext import commands
from dotenv import load_dotenv

# Application
from discord_dice_roller.cogs import (
    DiceRollingCog,
    GuildConfigCog,
    UserConfigCog,
    UtilityCog,
)
from discord_dice_roller.utils.logging import setup_logging
from discord_dice_roller.utils.settings import get_command_prefix, init_settings_files

# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # Env setup
    random.seed()
    load_dotenv()
    setup_logging()
    init_settings_files()
    # Bot setup
    bot = commands.Bot(command_prefix=get_command_prefix, help_command=None)
    bot.add_cog(DiceRollingCog(bot))
    bot.add_cog(UtilityCog(bot))
    bot.add_cog(UserConfigCog(bot))
    bot.add_cog(GuildConfigCog(bot))
    # Execute
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
