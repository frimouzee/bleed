## Information
<div align="center">

Dumped src of [greed bot](https://axionbotz.vercel.app)

<img src="https://cdn.discordapp.com/attachments/1465329105082908837/1514185738298593280/v6sx527.png?ex=6a2a72dc&is=6a29215c&hm=ab7db938ed47c14f3bfa1b7c4f25365a40a25bccfa4fbe488853627ba4d7ee3e&"/>


</div>


## Token Setup & Configuration

To configure the bot, you need to set your Discord Bot Token:

1. Open the `config.json` file in the root folder of the project.
2. Put your token in the `token` field:
   ```json
   {
     "token": "YOUR_TOKEN_HERE"
   }
   ```
3. Save the file.

*Make sure your bot application has the required **Privileged Gateway Intents** (Presence Intent, Server Members Intent, and Message Content Intent) enabled in the Discord Developer Portal.*

## Running the Bot

Run the main file using python:
```bash
python bot.py
```
