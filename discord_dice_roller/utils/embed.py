"""Utilities for embed messages"""

# Third-party
import discord


# --------------------------------------------------------------------------------
# > Utilities
# --------------------------------------------------------------------------------
def create_embed(**kwargs):
    """
    Creates an embed with a default type and color
    :param kwargs: Standard discord.Embed kwargs
    :return: A preset discord Embed
    :rtype: Embed
    """
    kwargs.setdefault("type", "rich")
    kwargs.setdefault("color", discord.Color.blue())
    embed = discord.Embed(**kwargs)
    return embed


def create_error_embed(**kwargs):
    """
    Same as create_embed but with a default title and color set to red
    :param kwargs: Standard discord.Embed kwargs
    :return: A preset discord Embed
    :rtype: Embed
    """
    kwargs.setdefault("title", "Error")
    kwargs.setdefault("color", discord.Color.red())
    return create_embed(**kwargs)


def create_warning_embed(**kwargs):
    """
    Same as create_embed but with a default title and color set to orange
    :param kwargs: Standard discord.Embed kwargs
    :return: A preset discord Embed
    :rtype: Embed
    """
    kwargs.setdefault("title", "Warning")
    kwargs.setdefault("color", discord.Color.orange())
    return create_embed(**kwargs)
