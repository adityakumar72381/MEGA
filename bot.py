import random
import asyncio
import aiohttp
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Main Bot Token
BOT_TOKEN = "7764136517:AAFkibW4uouPcRGlH-9n4FJ4uorz6IURhns"
API_URL_TEMPLATE = "https://api.telegram.org/bot{}/setMessageReaction"

# List to store tokens of all bots (main and cloned)
bot_tokens = [BOT_TOKEN]

# Expanded Emoji List
EMOJIS = [
    "❤️", "🥰", "😍", "😊", "😘", "🔥", "🎉", "😂", "🤣", "👍", "👏", 
    "😎", "🤩", "💯", "🙌", "🥳", "🎊", "✨", "🌟", "💖", "😄", "😜", 
    "😇", "🤗", "🤔", "😅", "😉", "🧡", "💛", "😃", "💚"]
# Global dictionary to track reactions for each message
message_reactions = {}

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Start Command
async def start(update: Update, context):
    user = update.effective_user
    first_name = user.first_name if user else "User"

    # Start Message
    start_text = f"""
👋 Hello there, {first_name}!

Welcome to the **Auto Reaction Bot**  🎉, ready to sprinkle your conversations with a little extra happiness!

💁‍♂️ Here's how I spice up your chats:

✨ **DM Magic**: Message me and receive a surprise emoji in return. Expect the unexpected and enjoy the fun!  
🏖 **Group & Channel**: Add me to your groups or channels, and I'll keep the vibe positive by reacting to messages with engaging emojis.  

**Note**: You must add me to the group/channel *before* adding cloned bots.
    """

    # Inline Keyboard
    keyboard = [
        [InlineKeyboardButton("🤖 Clone Me", callback_data="clone_me")],
        [InlineKeyboardButton("🌐 Join Our Community", url="https://t.me/+wq_Afl2eS94zMWQ1")],
        [InlineKeyboardButton("📞 Customer Support", url="https://t.me/Yoursadityaaa")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(start_text, reply_markup=reply_markup, parse_mode="Markdown")

# Callback Query Handler
async def handle_callback_query(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "clone_me":
        await query.message.reply_text(
            "To clone me, use the command:\n\n`/clone <bot_token>`",
            parse_mode="Markdown"
        )

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
                logger.info(f"Cloned new bot: {bot_info} ")
                await update.message.reply_text(
                    f"Cloned bot: @{bot_info.get('username')} (ID: {bot_info.get('id')} Note : These bot did not response just only react )"
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


# React with Emoji (Private chat and Channel Messages)
async def react_to_message(update: Update, context):
    try:
        # Check if the message is from a private chat or a channel
        message = update.message or update.channel_post  # Either from private or channel
        
        if message:
            # Extract chat_id and message_id
            chat_id = message.chat.id
            message_id = message.message_id
            
            # Initialize the reactions for the message if not already done
            if message_id not in message_reactions:
                message_reactions[message_id] = []

            # Filter available emojis once for this message
            available_emojis = [emoji for emoji in EMOJIS if emoji not in message_reactions[message_id]]
            if not available_emojis:
                logger.warning(f"No more unique emojis available for message {message_id}")
                return

            # Choose a random emoji
            random_emoji = random.choice(available_emojis)
            message_reactions[message_id].append(random_emoji)

            # Prepare API payloads
            tasks = []
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
                tasks.append(send_reaction(api_url, payload, token))

            # Execute all reactions concurrently
            results = await asyncio.gather(*tasks)

            # Log results
            for result in results:
                if result["success"]:
                    logger.info(f"Reaction sent successfully by bot {result['token'][:10]}")
                else:
                    logger.error(f"Failed to send reaction by bot {result['token'][:10]}: {result['error']}")
    except Exception as e:
        logger.error(f"Error in react_to_message: {e}")


# Helper Function to Send Reaction with Retry
async def send_reaction(api_url, payload, token, retries=3, delay=1):
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    if response.status == 200:
                        return {"success": True, "token": token}
                    else:
                        error_text = await response.text()
                        logger.error(f"Attempt {attempt + 1}: {response.status} - {error_text}")
                        if response.status in {400, 401, 403}:  # Unrecoverable errors
                            return {"success": False, "token": token, "error": error_text}
        except aiohttp.ClientError as e:
            logger.error(f"Attempt {attempt + 1}: Network error - {e}")
        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff

    # If all attempts fail
    return {"success": False, "token": token, "error": "Max retries exceeded"}


# Bot Setup
app = Application.builder().token(BOT_TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback_query))
app.add_handler(CommandHandler("clone", clone_bot))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, react_to_message))  # Private chats
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, react_to_message))  # Channels

# Start Bot
logger.info("Bot is running...")
app.run_polling()
