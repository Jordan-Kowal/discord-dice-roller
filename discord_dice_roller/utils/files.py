"""Utilities for our files and folders"""

# Built-in
import json
import os
from collections import OrderedDict

# --------------------------------------------------------------------------------
# > Content
# --------------------------------------------------------------------------------
DATA_FOLDER = os.path.join(os.getcwd(), "data")
USER_SHORTCUTS_FILEPATH = os.path.join(DATA_FOLDER, "user_shortcuts.json")
GUILD_SETTINGS_FILEPATH = os.path.join(DATA_FOLDER, "guild_settings.json")


def init_data_files():
    """
    Creates the data folder, user settings file,
    and guild settings file, but only if they are missing
    """
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    for path in [GUILD_SETTINGS_FILEPATH, USER_SHORTCUTS_FILEPATH]:
        if os.path.exists(path):
            continue
        with open(path, "w") as f:
            json.dump({}, f)


def get_shortcuts_content():
    """
    :return: The content of the user shortcuts JSON file
    :rtype: dict
    """
    with open(USER_SHORTCUTS_FILEPATH, "r") as f:
        content = json.load(f)
    return content


def get_user_shortcuts(user_id, default=None):
    """
    Opens the shortcuts JSON file and returns both its content and the user's content
    :param user_id: The discord user id
    :type user_id: str or int
    :param default: Default value if the user has no existing shortcuts
    :return: The content of the JSON file and the user subpart
    :rtype: dict, dict
    """
    content = get_shortcuts_content()
    user_id = str(user_id)
    return content, content.get(user_id, default)


def update_user_shortcuts(user_id, user_data, file_content=None):
    """
    Updates the JSON file with the new user's shortcuts (sorted alphabetically)
    :param user_id: The discord user id
    :type user_id: str or int
    :param dict user_data: The new shortcuts for the user
    :param dict file_content: The current file content (before update)
    """
    if file_content is None:
        file_content = get_shortcuts_content()
    user_id = str(user_id)
    file_content[user_id] = OrderedDict(sorted(user_data.items(), key=lambda t: t[0]))
    with open(USER_SHORTCUTS_FILEPATH, "w") as f:
        json.dump(file_content, f, indent=2)
