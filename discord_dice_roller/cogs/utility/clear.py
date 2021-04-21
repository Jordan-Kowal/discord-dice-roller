"""Helpers for the `clear` command"""

# Built-in
import os

# --------------------------------------------------------------------------------
# > Settings
# --------------------------------------------------------------------------------
MIN_LIMIT = 1
MAX_LIMIT = 10


# --------------------------------------------------------------------------------
# > Functions
# --------------------------------------------------------------------------------
def should_delete(msg, bot, ctx):
    """
    Predicate to choose which message to delete in the `purge` API
    :param Message msg: Any discord message we are reading through
    :param Bot bot: The current bot's instance
    :param Context ctx: The command call context
    :return: Whether the message should be deleted
    :rtype: bool
    """
    # Do not remove the user's call
    if msg.id == ctx.message.id:
        return False
    # Remove command calls
    if msg.content.startswith(os.getenv("COMMAND_PREFIX")):
        return True
    # Remove our bot's messages
    if msg.author == bot.user:
        return True
    return False


def validate_clear_args(*args):
    """
    Checks we only got 1 arg and it's a int between MIN_LIMIT and MAX_LIMIT
    :param [str] args: The user's instructions
    :return: Whether the args were valid, their value, and the error message
    :rtype: bool, int or None, str
    """
    default_error = (
        f"The `limit` argument must be a number between {MIN_LIMIT} and {MAX_LIMIT}"
    )
    if len(args) != 1:
        error = f"This command expects only 1 argument, a number between {MIN_LIMIT} and {MAX_LIMIT}"
        return False, None, error
    try:
        limit = int(args[0])
    except ValueError:
        return False, None, default_error
    if not (MIN_LIMIT <= limit <= MAX_LIMIT):
        return False, None, default_error
    return True, limit, ""
