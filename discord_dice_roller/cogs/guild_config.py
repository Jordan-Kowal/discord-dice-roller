"""Cog allowing guilds to customize their settings"""

# Third-party
from discord.ext import commands

# Local
from ..utils.cog import ImprovedCog
from ..utils.embed import create_embed
from ..utils.settings import DEFAULT_PREFIX, get_guild_settings, update_guild_settings


# --------------------------------------------------------------------------------
# > Cog
# --------------------------------------------------------------------------------
class GuildConfigCog(ImprovedCog):
    """
    Allows administrators to customize some settings for their guild
    Commands:
        > setprefix     Changes prefix for this bot on this guild. Only usable by admins.
    Events:
        > on_message    On mentioned-first, returns the current prefix for this bot on this guild
    """

    # ----------------------------------------
    # setprefix
    # ----------------------------------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, prefix):
        """Changes prefix for this bot on this guild. Only usable by admins."""
        self.log_command_call("setprefix", ctx.message)
        guild_id = str(ctx.guild.id)
        file_content, settings = get_guild_settings(guild_id)
        settings["prefix"] = prefix
        update_guild_settings(guild_id, settings, file_content)
        description = f"From now on, I'll respond to the `{prefix}` command prefix"
        embed = create_embed(title="Settings updated!", description=description)
        await ctx.send(embed=embed)

    @setprefix.error
    async def setprefix_error(self, ctx, error):
        """Base error handler for the !setprefix command"""
        await self.log_error_and_apologize(ctx, error)

    # ----------------------------------------
    # on_message
    # ----------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        """On mentioned-first, returns the current prefix for this bot on this guild"""
        if len(message.mentions) == 0 or message.mentions[0] != self.bot.user:
            return
        self.log_command_call("getprefix", message)
        guild_id = str(message.guild.id)
        _, settings = get_guild_settings(guild_id)
        prefix_value = settings.get("prefix", DEFAULT_PREFIX)
        embed = create_embed(
            description=f"My current prefix on this guild is `{prefix_value}`"
        )
        await message.channel.send(embed=embed)
