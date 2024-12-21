import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler,
    ChatMemberHandler, filters
)
import aiohttp

# Replace with your bot token
BOT_TOKEN = "7764136517:AAF76pABfIfdc7llWnJ1blRa26Y6uBwDfMg"

# API Endpoint to send reactions
API_URL = "https://reactions3.adityakumar72381.workers.dev/"

# Admin Contact Info
ADMIN_CHAT_ID = "6128121762"  # Replace with the actual admin's chat ID
PRIVATE_CHANNEL_ID = "-1002344830926"  # Your admin channel's chat ID
USER_MESSAGE_ID = 6  # Message ID for storing user IDs
CHANNEL_MESSAGE_ID = 7  # Message ID for storing channel IDs

# Global variables for storing user and channel details
user_message = "User IDs:\n"
channel_message = "Channel IDs:\n"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Helper: Send Reaction
async def send_reaction_async(chat_id: int, message_id: int):
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Reaction sent successfully for message ID {message_id}")
                else:
                    logger.error(f"Failed to send reaction: {response.status} - {await response.text()}")
    except Exception as e:
        logger.error(f"Error sending reaction: {e}")

# Handle Messages and Reactions
async def handle_update(update: Update, context: CallbackContext):
    try:
        if update.message:
            chat_id = update.message.chat_id
            message_id = update.message.message_id
        elif update.channel_post:
            chat_id = update.channel_post.chat_id
            message_id = update.channel_post.message_id
        else:
            return

        logger.info(f"Received chat_id: {chat_id}, message_id: {message_id}")
        asyncio.create_task(send_reaction_async(chat_id, message_id))
    except Exception as e:
        logger.error(f"Error handling update: {e}")

# Handle /start Command
async def start(update: Update, context: CallbackContext):
    global user_message

    user_id = update.effective_user.id
    user_name = update.message.from_user.first_name

    # Check if the user ID is already present
    if str(user_id) not in user_message:
        user_message += f"{user_id}\n"

        # Edit the user message in the admin channel
        await context.bot.edit_message_text(
            chat_id=PRIVATE_CHANNEL_ID,
            message_id=USER_MESSAGE_ID,
            text=user_message,
        )

    # Reply to the user
    welcome_message = f"""
*👋 Hello there, {user_name}!*

*Welcome to the Auto Reaction Bot 🎉*, ready to sprinkle your conversations with a little extra happiness!

💁‍♂️ *Here's how I spice up your chats:*

🏖 * Channel*: Add me to your channels, and I'll keep the vibe positive by reacting to messages with engaging emojis.

*Note:* _You must add me to the channel before adding cloned bots._
    """
    keyboard = [
        [InlineKeyboardButton("✨ More reactions ??", callback_data="more_reactions")],
        [InlineKeyboardButton("👥 Join our community", url="https://t.me/automated_world")],
        [InlineKeyboardButton("📞 Contact support", url="https://t.me/Yoursadityaaa")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, parse_mode="Markdown", reply_markup=reply_markup)

# Handle Inline Button Actions
async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "more_reactions":
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
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(bot_list, reply_markup=reply_markup)

    elif query.data == "back_to_start":
        user_name = query.from_user.first_name
        welcome_message = f"""
*👋 Hello there, {user_name}!*

*Welcome to the Auto Reaction Bot 🎉*, ready to sprinkle your conversations with a little extra happiness!

💁‍♂️ *Here's how I spice up your chats:*

🏖 * Channel*: Add me to your channels, and I'll keep the vibe positive by reacting to messages with engaging emojis.

*Note:* _You must add me to the channel before adding cloned bots._
        """
        keyboard = [
            [InlineKeyboardButton("✨ More reactions", callback_data="more_reactions")],
            [InlineKeyboardButton("👥 Join our community", url="https://t.me/automated_world")],
            [InlineKeyboardButton("📞 Contact support", url="https://t.me/Yoursadityaaa")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(welcome_message, parse_mode="Markdown", reply_markup=reply_markup)

# Track Channels When Added
async def handle_chat_member(update: Update, context: CallbackContext):
    global channel_message

    chat = update.effective_chat
    if update.my_chat_member.new_chat_member.status == "administrator":
        channel_id = chat.id
        channel_name = chat.title
        channel_link = f"https://t.me/{chat.username}" if chat.username else "Private Channel"

        # Add channel to the list
        if str(channel_id) not in channel_message:
            channel_message += f"{channel_id} - {channel_name}\n"

            # Update the channel message in the admin channel
            await context.bot.edit_message_text(
                chat_id=PRIVATE_CHANNEL_ID,
                message_id=CHANNEL_MESSAGE_ID,
                text=channel_message,
            )

            # Notify the admin channel
            await context.bot.send_message(
                chat_id=PRIVATE_CHANNEL_ID,
                text=(
                    f"📢 Bot added to a new channel!\n"
                    f"**Channel Name**: {channel_name}\n"
                    f"**Channel ID**: `{channel_id}`\n"
                    f"**Channel Link**: {channel_link}"
                ),
                parse_mode="Markdown",
            )

# Main Function to Run the Bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, handle_update))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(ChatMemberHandler(handle_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    application.run_polling()

if __name__ == "__main__":
    main()
