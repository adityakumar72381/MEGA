import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler,
    ChatMemberHandler, filters
)
import aiohttp

# Replace with your bot token
BOT_TOKEN = "7764136517:AAFlAEhA7NvX5zz41imUbEPCI_lnvushgLw"

# API Endpoint to send reactions
API_URL = "https://reactions3.adityakumar72381.workers.dev/"

# Admin Contact Info
PRIVATE_CHANNEL_ID = "-1002344830926"  # Your admin channel's chat ID

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Helper: Send Reaction
async def send_reaction_async(chat_id: int, message_id: int, context: CallbackContext):
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    status = "✅ Successful"
                else:
                    status = f"❌ Failed: {response.status} - {await response.text()}"

                # Message Link for Admin Notification
                message_link = f"https://t.me/c/{str(chat_id)[4:]}/{message_id}" if str(chat_id).startswith("-100") else "Private Message"

                # Send update to admin channel
                await context.bot.send_message(
                    chat_id=PRIVATE_CHANNEL_ID,
                    text=(
                        f"📩 **Reaction Update**\n\n"
                        f"**Channel ID**: `{chat_id}`\n"
                        f"**Message Link**: [View Message]({message_link})\n"
                        f"**Message ID**: `{message_id}`\n"
                        f"**Status**: {status}"
                    ),
                    parse_mode="Markdown",
                )
    except Exception as e:
        logger.error(f"Error sending reaction: {e}")
        await context.bot.send_message(
            chat_id=PRIVATE_CHANNEL_ID,
            text=f"❌ **Error Sending Reaction**: {e}",
        )

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
        asyncio.create_task(send_reaction_async(chat_id, message_id, context))
    except Exception as e:
        logger.error(f"Error handling update: {e}")

# Handle /start Command
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_name = update.message.from_user.first_name

    # Notify the admin channel
    await context.bot.send_message(
        chat_id=PRIVATE_CHANNEL_ID,
        text=(
            f"👤 **New User Alert**\n\n"
            f"**User Name**: [Click Here](tg://user?id={user_id})\n"
            f"**User ID**: `{user_id}`"
        ),
        parse_mode="Markdown",
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
        [InlineKeyboardButton("✨ More reactions", callback_data="more_reactions")],
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
10. Bot 10 - @Reactiongiver10bot
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
    chat = update.effective_chat
    if update.my_chat_member.new_chat_member.status == "administrator":
        channel_id = chat.id
        channel_name = chat.title

        # Notify the admin channel
        await context.bot.send_message(
            chat_id=PRIVATE_CHANNEL_ID,
            text=(
                f"📢 Bot added to a new channel!\n"
                f"**Channel Name**: {channel_name}\n"
                f"**Channel ID**: `{channel_id}`"
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
