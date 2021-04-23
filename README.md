# Discord Dice Roller

This guide is for those who wish to setup their own bot instance using this repository.
If you simply wish to invite and use the already-hosted bot on your discord guild,
checkout the [Official Page](https://jordan-kowal.github.io/discord-dice-roller/) instead.


### Summary
- [Create a bot on discord](#create-a-bot-on-discord)
- [Get this project](#get-this-project)
- [Make some changes](#make-some-changes)
- [Run it with docker](#run-it-with-docker)


### Create a bot on discord
To run your own bot, you'll first need to create an account for said bot.
To do so, follow [this guide](https://discordpy.readthedocs.io/en/stable/discord.html) made by the
`discord.py` team. It will basically walk you through:
- Creating an app
- Creating a bot within that app
- Creating an **invite link** for that bot

In our case, the required permissions are `76800`. Which translates into:
- **View Channels**: To view available channels
- **Send Messages**: To answer our user's commands
- **Manage Messages**: To delete command calls and our bot's messages when using the `clear` command
- **Read Message History**: Same as **Manage Messages**


### Get this project
If we ignore the venv/docker part, there are only 2 parts required for the project to work:
- `fork` or `clone` this repository
- Create an `.env` file and put your bot's authentication token in it (which can be found in your discord app settings)

Here's a quick example:
```bash
cd /where/you/want/to/go
git clone git@github.com:Jordan-Kowal/discord-dice-roller.git
cd discord-dice-roller
cp .env.sample .env
nano .env
# Add your actual token value into the file
```


### Make some changes
If you want to contribute or simply change the codebase locally, you'll need:
- A virtual environment
- Install the `pre-commit` hooks

Once you've made and activated your virtual env, you can run the following commands.
It will install all the necessary dependencies and setup the `pre-commit` hooks:

```bash
pip install -r requirements.txt
pip install -r requirements.dev.txt
pre-commit install
```

To run the bot, simply run the `main.py` file from within your venv. That's it.


### Run it with docker
If you wish to run the bot *for real*, I've provided a `Dockerfile` and `docker-compose`.
Make sure you've updated your `.env` file and simply run `docker-compose up`.
It should work.
