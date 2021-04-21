"""Utilities for embed messages"""

# Third-party
import discord


# --------------------------------------------------------------------------------
# > Utilities
# --------------------------------------------------------------------------------
def create_embed(**kwargs):
    """
    Creates an embed with a default type, color, and thumbnail
    :param kwargs: Standard discord.Embed kwargs
    :return: A preset discord Embed
    :rtype: Embed
    """
    kwargs.setdefault("type", "rich")
    kwargs.setdefault("color", discord.Color.blue())
    embed = discord.Embed(**kwargs)
    embed.set_thumbnail(url="https://i.imgur.com/Nn2JKQI.png")
    return embed


def create_error_embed(**kwargs):
    """
    Same as create_embed but with a default title and color set to red
    :param kwargs: Standard discord.Embed kwargs
    :return: A preset discord Embed
    :rtype: Embed
    """
    kwargs.setdefault("title", "Woopsie! :(")
    kwargs.setdefault("color", discord.Color.red())
    return create_embed(**kwargs)
