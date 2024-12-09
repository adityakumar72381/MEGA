from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters, CallbackQueryHandler
import aiohttp  # For asynchronous HTTP requests
import asyncio
import logging



# Replace with your bot token
BOT_TOKEN = "7764136517:AAHzhFAO7FVHtyz-7fpxBeC0Yir9R5KqMTo"

# API Endpoint to send reactions
API_URL = "https://reactions3.adityakumar72381.workers.dev/"

# Admin Contact Info
ADMIN_CHAT_ID = "6128121762"  # Replace with the actual admin's chat ID

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_reaction_async(chat_id: int, message_id: int):
    """Send reaction asynchronously to the API."""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Reaction sent successfully for message ID {message_id}")
                else:
                    logger.error(f"Failed to send reaction: {response.status} - {await response.text()}")
    except Exception as e:
        logger.error(f"Error sending reaction: {e}")

async def handle_update(update: Update, context: CallbackContext):
    """Handles incoming updates and extracts chat_id and message_id."""
    try:
        # Extract chat_id and message_id
        if update.message:
            chat_id = update.message.chat_id
            message_id = update.message.message_id
        elif update.channel_post:
            chat_id = update.channel_post.chat_id
            message_id = update.channel_post.message_id
        else:
            logger.warning("Update does not contain a message or channel post.")
            return

        logger.info(f"Received chat_id: {chat_id}, message_id: {message_id}")

        # Send reaction in the background
        asyncio.create_task(send_reaction_async(chat_id, message_id))

    except Exception as e:
        logger.error(f"Error handling update: {e}")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def start(update, context):
    """Handle the /start command."""
    user_name = update.message.from_user.first_name  # Get user's first name
    welcome_message = f"""
*👋 Hello there, {user_name}!*

*Welcome to the Auto Reaction Bot 🎉*, ready to sprinkle your conversations with a little extra happiness!

💁‍♂️ *Here's how I spice up your chats:*

🏖 * Channel*: Add me to your channels, and I'll keep the vibe positive by reacting to messages with engaging emojis.

*Note:* _You must add me to the channel before adding cloned bots._
    """
    
    # Inline keyboard buttons
    keyboard = [
        [InlineKeyboardButton("✨ Want more reactions?", callback_data="more_reactions")],
        [InlineKeyboardButton("👥 Join our community", url="https://t.me/automated_world")],
        [InlineKeyboardButton("📞 Contact support", url="https://t.me/Yoursadityaaa")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_message, parse_mode="Markdown", reply_markup=reply_markup
    )
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
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
   """
        keyboard = [
            [InlineKeyboardButton("Contact admin for more reactions", url="https://t.me/Yoursadityaaa")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(bot_list, reply_markup=reply_markup)

    # Add more conditions here for other buttons as needed

def main():
    """Start the bot."""
    # Initialize the bot application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, handle_update))

    # Add handler for button callback
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start the bot
    application.run_polling()
    logger.info("Bot started...")

if __name__ == "__main__":
    main()
