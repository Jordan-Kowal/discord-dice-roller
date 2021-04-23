"""Utilities for our files and folders"""

# Built-in
import json
import os
from collections import OrderedDict

# --------------------------------------------------------------------------------
# > Global
# --------------------------------------------------------------------------------
SETTINGS_FOLDER = os.path.join(os.getcwd(), "../settings")


def init_settings_files():
    """If missing, creates the settings folder and the empty JSON files"""
    if not os.path.exists(SETTINGS_FOLDER):
        os.makedirs(SETTINGS_FOLDER)
    for path in [
        GUILD_SETTINGS_FILEPATH,
        USER_SHORTCUTS_FILEPATH,
        USER_SETTINGS_FILEPATH,
    ]:
        if os.path.exists(path):
            continue
        with open(path, "w") as f:
            json.dump({}, f)


def get_key(filepath, key, default=None):
    """
    Opens the file and fetches the value at said key
    :param str filepath: The path to the file
    :param str key: The key to fetch
    :param default: The value to return if no key is found
    :return: The value at the key (or the default value)
    """
    with open(filepath, "r") as f:
        file_content = json.load(f)
    return file_content.get(key, default)


def update_key(filepath, key, value):
    """
    Updates the key in a given JSON file. Dict values are sorted alphabetically.
    :param str filepath: The path to the file
    :param str key: The key to update
    :param value: The value for said key
    """
    with open(filepath, "r") as f:
        file_content = json.load(f)
    if type(value) == dict:
        file_content[key] = OrderedDict(sorted(value.items(), key=lambda t: t[0]))
    else:
        file_content[key] = value
    with open(filepath, "w") as f:
        json.dump(file_content, f, indent=2)


# --------------------------------------------------------------------------------
# > User shortcuts
# --------------------------------------------------------------------------------
USER_SHORTCUTS_FILEPATH = os.path.join(SETTINGS_FOLDER, "user_shortcuts.json")


def get_user_shortcuts(user_id):
    """
    Gets the user's shortcuts from the JSON file
    :param str user_id: The discord user id as string
    :return: The user's shortcuts
    :rtype: dict
    """
    return get_key(USER_SHORTCUTS_FILEPATH, user_id, {})


def update_user_shortcuts(user_id, user_data):
    """
    Updates the JSON file with the new user's shortcuts (sorted alphabetically)
    :param str user_id: The discord user id
    :param dict user_data: The new shortcuts for the user
    """
    update_key(USER_SHORTCUTS_FILEPATH, user_id, user_data)


# --------------------------------------------------------------------------------
# > User settings
# --------------------------------------------------------------------------------
USER_SETTINGS_FILEPATH = os.path.join(SETTINGS_FOLDER, "user_settings.json")
DEFAULT_USER_SETTINGS = {"verbose": True}


def get_user_settings(user_id):
    """
    Gets the user's settings from the JSON file
    :param str user_id: The discord user id as string
    :return: The user's shortcuts
    :rtype: dict
    """
    return get_key(USER_SETTINGS_FILEPATH, user_id, {})


def update_user_settings(user_id, user_data):
    """
    Updates the JSON file with the new user's settings (sorted alphabetically)
    :param str user_id: The discord user id
    :param dict user_data: The new shortcuts for the user
    """
    update_key(USER_SETTINGS_FILEPATH, user_id, user_data)


# --------------------------------------------------------------------------------
# > Guild settings
# --------------------------------------------------------------------------------
GUILD_SETTINGS_FILEPATH = os.path.join(SETTINGS_FOLDER, "guild_settings.json")
DEFAULT_GUILD_SETTINGS = {"prefix": "!"}


def get_command_prefix(_bot, message):
    """
    Gets the command prefix based on the guild sending the message
    :param Bot _bot: Our bot instance
    :param Message message: Discord message
    :return: The prefix for the current guild
    :rtype: str
    """
    guild_id = str(message.guild.id)
    guild_settings = get_guild_settings(guild_id)
    return guild_settings.get("prefix", DEFAULT_GUILD_SETTINGS["prefix"])


def get_guild_settings(guild_id):
    """
    Gets the guild's settings from the JSON file
    :param str guild_id: The discord/server id
    :return: The guild's settings
    :rtype: dict
    """
    return get_key(GUILD_SETTINGS_FILEPATH, guild_id, {})


def update_guild_settings(guild_id, guild_data):
    """
    Updates the JSON file with the new guild's settings (sorted alphabetically)
    :param str guild_id: The discord guild/server id
    :param dict guild_data: The new shortcuts for the user
    """
    update_key(GUILD_SETTINGS_FILEPATH, guild_id, guild_data)
