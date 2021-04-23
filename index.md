## Welcome to the user guide

### Summary
- [Invite the bot](#invite-the-bot)
- [Command list](#command-list)
- [Roll instructions](#roll-instructions)
- [Settings](#settings)
- [Found a bug?](#found-a-bug?)


### Invite the bot

First, you need to add the bot to your guild(s). To do so, simply click 
[this link](https://discord.com/api/oauth2/authorize?client_id=831199138364129281&permissions=76800&scope=bot)
and choose which guild/server you want it to join. This link includes the bot's request for permissions, which are:

| Permission | Why? |
| --- | --- |
| **View Channels** | To interact with various channels |
| **Send Messages** | To respond to your command calls in the right channel |
| **Manage Messages** | To delete his messages and the users' command calls when using the `clear` command |
| **Read Message History** | Same reason as **Manage Messages** |


### Command list

First, let's see which commands are available. 
They have been grouped by category to make it easier to read. 

Quick legend:
- `[parameter]` means the parameter is **required**
- `?[parameter]` means the parameter is **optional**
- `[parameter]*` means the parameter is **repeatable**

| Command | Description |
| --- | --- |
| **Rolling dice** |  |
| `reroll` | Rolls the dice using the same settings as the user's last valid dice roll |
| `roll [instruction]*` | Rolls the dice using the provided instructions |
| `use [shortcut] ?[instruction]*` | Rolls the dice using a user's shortcut and maybe additional instr |
| **Shortcut management** |  |
| `remove [shortcut]` | Remove one specific shortcut for the user |
| `removeall` | Remove all of the user's shortcuts |
| `save [shortcut] [instruction]*` | Creates a new shortcut mapped to those instructions for the user |
| `show` | Show the list of existing shortcuts for the user |
| **Utility** | |
| `about` | Provides a recap of the bot main information (author, version, links, etc.) |
| `clear [qty]` | Checks the N last messages and removes those that are command calls or belongs to the bot |
| `help` | Provides a link that redirects you to the official documentation |
| `ping` | Simply checks if the bot is up and running |
| `@DiceRoller` | Mention him to know what `command prefix` he responds to |
| **Settings** | |
| `setprefix [value]` | Change the `command prefix` at the guild/server level. Needs admin privileges |
| `settings ?[name=value]*` | Shows the user current settings and allows editing on the fly |

The commands you'll be using the most are: 
- `roll` to roll the dice
- `use` to roll the dice using a shortcut
- `save` to create a new shortcut

Those 3 commands happen to be a bit more complex as they expect a set of **roll instructions** 
that follows specific rules. We'll go into more detail later on in this document.


### Roll instructions

The `roll`, `use`, and `save` commands are those you'll use the most,
and all required **roll instructions**. Those instructions are very specific and
follow a certain set of rules. So, what are they?

| Name | Status | Description | Example |
| --- | --- | --- | --- |
| `Dice` | Required (1 or more) | Dice to roll at the start | `3d20` or `1d20 2d6` |
| `Action` | Optional (1 max) | A specific action applied to your dice | See the list of actions below |
| `Modifier` | Optional (1 max) | A raw number to add/subtract at your final total | `+10` or `-5` |
| `Check` | Optional (1 max) | Automatically performs the check at the end of the roll | `>10` or `<=15` |

| Action | Description | Comment |
| --- | --- | --- |
| **Classic** |  |  |
| `adv` | Rerolls and keeps the best | Usable if rolling only 1 die |
| `dis` | Rerolls and keeps the worst | Usable if rolling only 1 die |
| <br/> |  |  |
| **Keep/Drop X dices** | Example: `5d8 dl3` | Usable only if enough dice and only 1 die type |
| `dh[X]` | Drops the X best dice |  |
| `dl[X]` | Drops the X worst dice |  |
| `kh[X]` | Keeps the X best dice |  |
| `kl[X]` | Keeps the X worst dice |  |
| <br/> |  |  |
| **Others** |  |  |
| `crit` | Double all your original dice | Works with any number of dice. Applied before the `modifier` |

To help you out, here are a few examples:
```bash
!roll 3d10 # Simply roll 3 die of 10 sides 
!roll 1d10 adv +5 # Roll 1d10, reroll it and keeps the best, then add 5
!roll 2d10 crit -1 >25 # Roll 2d10, multiply the result by 2, subtract 1, checks if higher than 25
!save test 1d10 adv # 'test' is now bound to "1d10 adv"
!use test # Is equivalent to "!roll 1d10 adv"
!use test +5 # We can add other compatible instructions on top of it
```


### Settings

The `settings` command is a bit special as it allows you to both see and set your settings.
- If you want to view your settings: `!settings`
- If you want to update your verbose setting: `!settings verbose=False`

Here are the available settings:

| Setting | Default value | Description |
| --- | --- | --- |
| **verbose** | `True`  | Makes the output of `roll` and `use` more detailed |


### Found a bug?

You can report any potential issue 
directly on the [GitHub repository](https://github.com/Jordan-Kowal/discord-dice-roller/issues)
