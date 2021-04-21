"""Utilities for our files and folders"""

# Built-in
import json
import os

# --------------------------------------------------------------------------------
# > Content
# --------------------------------------------------------------------------------
DATA_FOLDER = os.path.join(os.getcwd(), "data")
USER_SETTINGS_FILEPATH = os.path.join(DATA_FOLDER, "user_settings.json")
GUILD_SETTINGS_FILEPATH = os.path.join(DATA_FOLDER, "guild_settings.json")


def init_data_files():
    """
    Creates the data folder, user settings file,
    and guild settings file, but only if they are missing
    """
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    for path in [GUILD_SETTINGS_FILEPATH, USER_SETTINGS_FILEPATH]:
        if os.path.exists(path):
            continue
        with open(path, "w") as f:
            json.dump({}, f)
