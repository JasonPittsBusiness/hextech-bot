# hextech-bot

Hextech bot is a discord bot that tracks statistics for League of Legends players.

## Prerequisites

- Install [Docker](https://www.docker.com/get-started/)
- A [Discord bot token](https://docs.discord.com/developers/quick-start/getting-started)
  - The discord bot will need the Message Content Intent set to on under your apps bot page
  - The discord bot will need the scopes set to applications.commands and bot under your apps installation page
  - The discord bot will need the permissions set to Send Messages under your apps installation page
- [Riot API key](https://developer.riotgames.com/docs/portal#_getting-started)
  - [Developer keys](https://developer.riotgames.com/docs/portal#_getting-started:~:text=DEVELOPMENT%20API%20KEYS) expire every 24 hours
  - [Personal keys](https://developer.riotgames.com/docs/portal#_getting-started:~:text=PERSONAL%20API%20KEYS) do not expire so this is recommended for the bot
- Change the variables in the .env to your Discord bot token and Riot API key

## Installation

### Linux

Run each command below in your terminal

1. Open a terminal.
2. Make a folder for the bot and move into it:

   ```bash
   cd ~
   mkdir hextech-bot
   cd hextech-bot
   ```

3. Create the `.env` file:

   ```bash
   printf "BOT_TOKEN=your-bot-token\nRIOT_API_KEY=your-riot-api-key\n" > .env
   ```

4. Open `.env` and replace the placeholders with your Discord bot token and Riot API key:

   ```bash
   nano .env
   ```

5. Create an empty database file:

   ```bash
   touch hextech.db
   ```

6. Start the bot:

   ```bash
   docker run -d \
     --name hextech-bot \
     --env-file .env \
     -v $(pwd)/hextech.db:/usr/src/app/hextech.db \
     --restart unless-stopped \
     jasonpittsjrbusiness/hextech-bot
   ```

### Windows

1. Open PowerShell.
2. Make a folder for the bot and move into it:

   ```powershell
   cd ~
   mkdir hextech-bot
   cd hextech-bot
   ```

3. Create the `.env` file:

   ```powershell
   Set-Content .env "BOT_TOKEN=your-bot-token", "RIOT_API_KEY=your-riot-api-key"
   ```

4. Open `.env` and replace the placeholders with your Discord bot token and Riot API key:

   ```powershell
   notepad .env
   ```

5. Create an empty database file:

   ```powershell
   New-Item hextech.db
   ```

6. Start the bot:

   ```powershell
   docker run -d `
     --name hextech-bot `
     --env-file .env `
     -v ${PWD}\hextech.db:/usr/src/app/hextech.db `
     --restart unless-stopped `
     jasonpittsjrbusiness/hextech-bot
   ```

## Usage

For the full current list of commands run !help

| Command                        | Description                                                                           |
| ------------------------------ | ------------------------------------------------------------------------------------- |
| `!rank Name#Tag [queue]`       | Show a player's rank. Queue is optional and defaults to solo.                         |
| `!leaderboard`                 | Show this server's leaderboard.                                                       |
| `!leaderboard add Name#Tag`    | Add a player to the leaderboard.                                                      |
| `!leaderboard remove Name#Tag` | Remove a player from the leaderboard.                                                 |
| `!leaderboard subscribe`       | Subscribes the current channel to a daily leaderboard post at 11 AM and 11 PM central |
| `help`                         | List all available commands for this bot                                              |

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://github.com/JasonPittsBusiness/hextech-bot/blob/main/LICENSE)
