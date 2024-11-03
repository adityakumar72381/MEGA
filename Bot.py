import random
import requests
import json
import os
from datetime import datetime, timedelta
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your bot token, Droplink API token, and the channel ID
BOT_TOKEN = "8118599107:AAFeLN26fLJrIWBFmzg3XdusIXg46Qchb30"
DROPLINK_API_TOKEN = "7d52615e08da763a299c3ed0fbc70f17cf29ebb"
WORKER_URL = "https://masterworker.awadheshkumar7537.workers.dev/"
VIDEO_MAPPING_FILE = 'video_mapping.json'
CHANNEL_ID = "@hdhdhdhdhdjdjdjrhrhrhrh"

# Dictionary to store user access details
user_access = {}

# Function to load video mappings
def load_video_mapping():
    if os.path.exists(VIDEO_MAPPING_FILE):
        with open(VIDEO_MAPPING_FILE, "r") as f:
            return json.load(f)
    return {}

# Function to save video mappings
def save_video_mapping(video_mapping):
    with open(VIDEO_MAPPING_FILE, "w") as f:
        json.dump(video_mapping, f)

# Function to generate a random number and create a shortened link
def create_shortened_link():
    random_number = random.randint(1000, 9999)
    worker_link = f"{WORKER_URL}{random_number}"

    # Shorten the link using Droplink API
    shorten_url = f"https://droplink.co/api?api={DROPLINK_API_TOKEN}&url={worker_link}&format=text"
    try:
        response = requests.get(shorten_url, timeout=5)
        response.raise_for_status()
        return random_number, response.text.strip()
    except requests.RequestException as e:
        print(f"Error generating shortened link: {e}")
        return random_number, None

# Function to check channel membership and admin status
async def check_membership_and_admin(user_id: int, context) -> (bool, bool):
    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        is_member = chat_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
        is_admin = chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
        return is_member, is_admin
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False, False

# Start command handler with video ID check
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    args = context.args  # Retrieve arguments passed with the command

    # Check if the user is a member and admin of the required channel
    is_member, is_admin = await check_membership_and_admin(user_id, context)
    if not is_member:
        await update.message.reply_text(
            f"Please join our channel {CHANNEL_ID} to use this bot."
        )
        return

    # Check if the user already has access
    if user_id in user_access and user_access[user_id]["expires_at"] > datetime.utcnow():
        if args:
            video_id = args[0]
            video_mapping = load_video_mapping()
            if video_id in video_mapping:
                await context.bot.send_video(chat_id=user_id, video=video_mapping[video_id])
                return
        else:
            await update.message.reply_text("You already have access to the bot. No new link needed.")
            return

    # Generate a random number link and shorten it
    random_number, short_link = create_shortened_link()
    if short_link:
        user_access[user_id] = {"number": random_number, "expires_at": datetime.utcnow() + timedelta(hours=24)}

        # Message to be sent with the shortened link
        message = f"Welcome! Please click the link below and send the number you see:\n{short_link}\n\n"

        # If the user is an admin, include the code in the message
        if is_admin:
            message += f"As an admin, here’s your code directly: {random_number}\n\n"

        message += "After sending the correct number, you'll get access for 24 hours."

        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Error: Could not generate link. Please try again later.")

# Handler to check the user response for the correct number
async def check_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_response = update.message.text.strip()

    if user_id in user_access:
        access_info = user_access[user_id]
        if user_response == str(access_info["number"]):
            access_info["expires_at"] = datetime.utcnow() + timedelta(hours=24)
            await update.message.reply_text("Correct! You now have access to the bot for 24 hours.")
        else:
            await update.message.reply_text("Incorrect number. Please try again.")
    else:
        await update.message.reply_text("Please use /start to begin the process.")

# Function to handle video uploads and generate referral link if the user has access
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_access and user_access[user_id]["expires_at"] > datetime.utcnow():
        video_file_id = update.message.video.file_id
        unique_id = str(random.randint(1000, 9999))
        video_link = f"https://t.me/{context.bot.username}?start={unique_id}"

        video_mapping = load_video_mapping()
        video_mapping[unique_id] = video_file_id
        save_video_mapping(video_mapping)

        await update.message.reply_text(f"Here is your video link:\n\n{video_link}")
    else:
        await update.message.reply_text("Access expired. Please use /start to get a new link.")

# Main function to run the bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_number))

    app.run_polling()

if __name__ == "__main__":
    main()
