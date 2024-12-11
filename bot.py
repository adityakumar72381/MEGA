from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters, CallbackQueryHandler
import aiohttp
import asyncio
import logging

# Replace with your bot toke
# Replace with your bot token
BOT_TOKEN = "7764136517:AAGLKNQ5LZhmCGhCvtenteq72jbJD4sDXf0"

# API Endpoints
API_URL_CHANNEL = "https://reactions3.adityakumar72381.workers.dev/"  # First API for channel messages
API_URL_BOT_CHAT = "https://reactionbot.adityakumar72381.workers.dev/"  # Second API for bot chat messa
# Admin Contact Info
ADMIN_CHAT_ID = "6128121762"

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_reaction_to_api(api_url: str, chat_id: int, message_id: int):
    """Send reaction asynchronously to the given API."""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Reaction sent successfully to {api_url} for message ID {message_id}")
                else:
                    logger.error(f"Failed to send reaction to {api_url}: {response.status} - {await response.text()}")
    except Exception as e:
        logger.error(f"Error sending reaction to {api_url}: {e}")

async def handle_update(update: Update, context: CallbackContext):
    """Handle incoming updates and send reactions."""
    try:
        if update.message:
            chat_id = update.message.chat_id
            message_id = update.message.message_id
            if update.message.chat.type == "channel":
                api_url = API_URL_CHANNEL
                logger.info("Detected message from a channel.")
            else:
                api_url = API_URL_BOT_CHAT
                logger.info("Detected message from bot chat.")
            asyncio.create_task(send_reaction_to_api(api_url, chat_id, message_id))
        elif update.channel_post:
            chat_id = update.channel_post.chat_id
            message_id = update.channel_post.message_id
            logger.info("Detected channel post.")
            asyncio.create_task(send_reaction_to_api(API_URL_CHANNEL, chat_id, message_id))
        else:
            logger.warning("Update does not contain a message or channel post.")
    except Exception as e:
        logger.error(f"Error handling update: {e}")

async def start(update: Update, context: CallbackContext):
    """Handle the /start command."""
    user_name = update.message.from_user.first_name  # Correctly fetch the user's first name
    welcome_message = f"""
*👋 Hello there, {user_name}!*

*Welcome to the Auto Reaction Bot 🎉*, ready to sprinkle your conversations with a little extra happiness!

💁‍♂️ *Here's how I spice up your chats:*

🏖 *Channel*: Add me to your channels, and I'll keep the vibe positive by reacting to messages with engaging emojis.

*Note:* _You must add me to the channel before adding cloned bots._
    """

    keyboard = [
        [InlineKeyboardButton("✨ Want more reactions?", callback_data="more_reactions")],
        [InlineKeyboardButton("👥 Join our community", url="https://t.me/automated_world")],
        [InlineKeyboardButton("📞 Contact support", url="https://t.me/Yoursadityaaa")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        welcome_message, parse_mode="Markdown", reply_markup=reply_markup
    )

async def button_callback(update: Update, context: CallbackContext):
    """Handle inline button presses."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    if query.data == "more_reactions":
        # Send the list of available bots
        bot_list = """
Here are some bots you can add to your channels for more reactions:

1. Bot 1 - @Reactiongivers1bot
2. Bot 2 - @Reactiongivers2bot
3. Bot 3 - @Reactiongivers3bot
4. Bot 4 - @Reactiongivers4bot
5. Bot 5 - @Reactiongivers5bot
6. Bot 6 - @Reactiongivers6bot
7. Bot 7 - @Reactiongivers7bot
8. Bot 8 - @Reactiongivers8bot
9. Bot 9 - @Reactiongivers9bot
  Bot 10 - @Reactiongiver10bot
        """
        keyboard = [
            [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/Yoursadityaaa")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(bot_list, reply_markup=reply_markup)

    elif query.data == "back_to_start":
        # Edit the existing message, no new message sent
        user_name = query.from_user.first_name
        welcome_message = f"""
*👋 Hello there, {user_name}!*

*Welcome to the Auto Reaction Bot 🎉*, ready to sprinkle your conversations with a little extra happiness!

💁‍♂️ *Here's how I spice up your chats:*

🏖 *Channel*: Add me to your channels, and I'll keep the vibe positive by reacting to messages with engaging emojis.

*Note:* _You must add me to the channel before adding cloned bots._
        """
        keyboard = [
            [InlineKeyboardButton("✨ Want more reactions?", callback_data="more_reactions")],
            [InlineKeyboardButton("👥 Join our community", url="https://t.me/automated_world")],
            [InlineKeyboardButton("📞 Contact support", url="https://t.me/Yoursadityaaa")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            welcome_message, parse_mode="Markdown", reply_markup=reply_markup
        )

def main():
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, handle_update))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start the bot
    application.run_polling()
    logger.info("Bot started...")

if __name__ == "__main__":
    main()
