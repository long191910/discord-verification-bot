# Xaint Verification Bot

A simple asf verification bot coded by atiso.rip on cord

## Features

- CAPTCHA-based verification system
- Automatic role assignment upon successful verification
- Direct message communication with users
- Automatic setup of verification channels and roles
- Limit of 3 verification attempts per user
- Guild whitelist feature

## Setup

1. Create a Discord bot and obtain its token
2. Clone this repository
3. Install the required dependencies: `pip install -r module.txt`
4. Configure the `.env` file in the project directory with your bot token and other settings:
   ```
   DISCORD_TOKEN=your_bot_token_here
   VERIFIED_ROLE_ID=your_verified_role_id
   VERIFICATION_CHANNEL_ID=your_verification_channel_id
   UNVERIFIED_ROLE_ID=your_unverified_role_id
   WHITELISTED_GUILD_ID=your_guild_id
   ```
   Note: All IDs are required for proper functionality. The bot will automatically send a verification panel to the specified verification channel when it starts.
5. Run the bot: `python xaint.py`, `python3 xaint.py`

## Usage

1. **Automatic Verification Panel:**
   - When the bot starts, it automatically sends a verification panel to the configured verification channel
   - Users can click the verification button to start the verification process

2. **Verify Users:**
   - Users click the button from the automatically sent verification panel
   - The bot shows a CAPTCHA image in the channel
   - User enters the CAPTCHA code in the modal input box
   - Upon successful verification, the user is given the configured "Verified" role and unverified role has been removed.

## Guild Whitelist

The bot will only operate in the guild specified by `WHITELISTED_GUILD_ID` in the `.env` file. If the bot is added to any other guild, it will automatically leave that guild.

## How It Works

1. When a user clicks the verification button, the bot generates a random 6-character CAPTCHA code
2. The bot creates an image with the CAPTCHA code and sends it to the user via DM
3. The user must enter the correct CAPTCHA code within 3 attempts
4. On successful verification, the bot assigns the Verified role to the user
## Requirements

- Python 3.8+
- discord.py 2.3.2
- Pillow 10.0.0
- python-dotenv 1.0.1

## Contributing

Feel free to fork this repository and submit pull requests to improve the bot's functionality.
# discord-verification-bot
# discord-verification-bot
# discord-verification-bot
# discord-verification-bot
# discord-verification-bot
