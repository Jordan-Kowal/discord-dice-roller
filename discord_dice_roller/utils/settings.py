"""Utilities for our files and folders"""

# Built-in
import json
import os
from collections import OrderedDict

# --------------------------------------------------------------------------------
# > Global
# --------------------------------------------------------------------------------
DEFAULT_PREFIX = "!"
SETTINGS_FOLDER = os.path.join(os.getcwd(), "settings")
USER_SHORTCUTS_FILEPATH = os.path.join(SETTINGS_FOLDER, "user_shortcuts.json")
USER_SETTINGS_FILEPATH = os.path.join(SETTINGS_FOLDER, "user_settings.json")
GUILD_SETTINGS_FILEPATH = os.path.join(SETTINGS_FOLDER, "guild_settings.json")


def init_settings_files():
    """
    Creates the data folder, user settings file,
    and guild settings file, but only if they are missing
    """
    if not os.path.exists(SETTINGS_FOLDER):
        os.makedirs(SETTINGS_FOLDER)
    for path in [GUILD_SETTINGS_FILEPATH, USER_SHORTCUTS_FILEPATH]:
        if os.path.exists(path):
            continue
        with open(path, "w") as f:
            json.dump({}, f)


# --------------------------------------------------------------------------------
# > User shortcuts
# --------------------------------------------------------------------------------
def get_user_shortcuts(user_id):
    """
    Opens the shortcuts JSON file and returns both its content and the user's content
    :param user_id: The discord user id
    :type user_id: str or int
    :return: The content of the JSON file and the user subpart
    :rtype: dict, dict
    """
    with open(USER_SHORTCUTS_FILEPATH, "r") as f:
        file_content = json.load(f)
    user_id = str(user_id)
    return file_content, file_content.get(user_id, {})


def update_user_shortcuts(user_id, user_data, file_content=None):
    """
    Updates the JSON file with the new user's shortcuts (sorted alphabetically)
    :param user_id: The discord user id
    :type user_id: str or int
    :param dict user_data: The new shortcuts for the user
    :param dict file_content: The current file content (before update)
    """
    if file_content is None:
        with open(USER_SHORTCUTS_FILEPATH, "r") as f:
            file_content = json.load(f)
    user_id = str(user_id)
    file_content[user_id] = OrderedDict(sorted(user_data.items(), key=lambda t: t[0]))
    with open(USER_SHORTCUTS_FILEPATH, "w") as f:
        json.dump(file_content, f, indent=2)


# --------------------------------------------------------------------------------
# > User settings
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# > Guild settings
# --------------------------------------------------------------------------------
def get_command_prefix(_bot, message):
    """
    Gets the command prefix based on the guild sending the message
    Callback for the Bot.command_prefix
    :param Bot _bot: Our bot instance
    :param Message message: Discord message
    :return: The prefix for the current guild
    :rtype: str
    """
    guild_id = str(message.guild.id)
    _, guild_settings = get_guild_settings(guild_id)
    return guild_settings.get("prefix", DEFAULT_PREFIX)


def get_guild_settings(guild_id):
    """
    Opens the guild settings JSON file and returns both its content and the guild's content
    :param guild_id: The guild/server ID
    :type guild_id: str or int
    :return: The file content and the guild settings
    :rtype: dict, dict
    """
    guild_id = str(guild_id)
    with open(GUILD_SETTINGS_FILEPATH, "r") as f:
        file_content = json.load(f)
    return file_content, file_content.get(guild_id, {})


def update_guild_settings(guild_id, guild_data, file_content=None):
    """
    Updates the JSON file with the new guild's settings (sorted alphabetically)
    :param guild_id: The discord user id
    :type guild_id: str or int
    :param dict guild_data: The new shortcuts for the user
    :param dict file_content: The current file content (before update)
    """
    if file_content is None:
        with open(GUILD_SETTINGS_FILEPATH, "r") as f:
            file_content = json.load(f)
    guild_id = str(guild_id)
    file_content[guild_id] = OrderedDict(sorted(guild_data.items(), key=lambda t: t[0]))
    with open(GUILD_SETTINGS_FILEPATH, "w") as f:
        json.dump(file_content, f, indent=2)
