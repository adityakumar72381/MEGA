import random
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Maoken
BOT_TOKEN = "7764136517:AAHip_csVx36mvmkwMqLcg5GXvYd7FhqAEo"
API_URL_TEMPLATE = "https://api.telegram.org/bot{}/setMessageReaction"

# List to store tokens of all bots (main and cloned)
bot_tokens = [BOT_TOKEN]

# Emoji List
EMOJIS = ["❤️", "🥰", "😍", "😊", "😘", "🔥", "🎉", "😂"]

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# Command to Clone a Bot
async def clone_bot(update: Update, context):
    try:
        if not context.args:
            await update.message.reply_text("Usage: /clone <bot_token>")
            return

        new_token = context.args[0]

        # Validate the new token by calling getMe
        validate_url = f"https://api.telegram.org/bot{new_token}/getMe"
        response = requests.get(validate_url)

        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_tokens.append(new_token)  # Add token to the list
                bot_info = data.get("result", {})
                logger.info(f"Cloned new bot: {bot_info}")
                await update.message.reply_text(
                    f"Cloned bot: @{bot_info.get('username')} (ID: {bot_info.get('id')})"
                )
            else:
                await update.message.reply_text("Failed to clone bot: Invalid token")
        else:
            logger.error(
                f"Failed to validate bot token: {response.status_code} - {response.text}"
            )
            await update.message.reply_text(
                f"Error: Unable to validate token. Status {response.status_code}"
            )
    except Exception as e:
        logger.error(f"Error in clone_bot: {e}")
        await update.message.reply_text("An error occurred while cloning the bot.")


# React with Emoji (Private chat and Channel Messages)
async def react_to_message(update: Update, context):
    try:
        # Check if the message is from a private chat or a channel
        message = update.message or update.channel_post  # Either from private or channel
        
        if message:
            # Extract chat_id and message_id
            chat_id = message.chat.id
            message_id = message.message_id
            
            # Choose a random emoji from the list
            random_emoji = random.choice(EMOJIS)

            # Send reactions using all bot tokens
            for token in bot_tokens:
                api_url = API_URL_TEMPLATE.format(token)
                payload = {
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "reaction": [
                        {
                            "type": "emoji",
                            "emoji": random_emoji,
                            "is_big": True
                        }
                    ]
                }

                # Send the POST request to the Telegram API
                response = requests.post(api_url, json=payload)

                # Handle response
                if response.status_code == 200:
                    logger.info(f"Reaction Sent by bot {token[:10]}: {response.json()}")
                else:
                    logger.error(
                        f"Failed to send reaction by bot {token[:10]}: {response.status_code} - {response.text}"
                    )
    except Exception as e:
        logger.error(f"Error in react_to_message: {e}")


# Bot Setup
app = Application.builder().token(BOT_TOKEN).build()

# Command to clone bots
app.add_handler(CommandHandler("clone", clone_bot))

# Handlers for both private and channel messages
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, react_to_message))  # Private chats
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, react_to_message))  # Channels

# Start Bot
logger.info("Bot is running...")
app.run_polling()
