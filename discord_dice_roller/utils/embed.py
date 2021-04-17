"""Utilities for embed messages"""

# Third-party
import discord


# --------------------------------------------------------------------------------
# > Utilities
# --------------------------------------------------------------------------------
def create_embed(**kwargs):
    """
    Adds a default type and thumbnail to a discord Embed
    :param kwargs: Standard discord.Embed kwargs
    :return: A preset discord Embed
    :rtype: Embed
    """
    embed = discord.Embed(type="rich", **kwargs)
    embed.set_thumbnail(url="https://i.imgur.com/Nn2JKQI.png")
    return embed
