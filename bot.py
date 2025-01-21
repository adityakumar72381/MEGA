import logging
import os
import requests
from mega import Mega
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext

# Bot token (replace with your bot's token)
BOT_TOKEN = '7508849360:AAFCJKq3qtwwLOBK--uVCjA1ivcsHub7qX4'

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Mega API
mega = Mega()
m = mega.login()  # Log in anonymously

# Function to download the file
def download_file(url, user_id):
    try:
        file = m.download_url(url)  # Downloads the file from Mega
        file_path = str(file)  # Convert PosixPath to string
        return file_path
    except Exception as e:
        logger.error(f"Error downloading the file: {e}")
        return None

# Function to get file type
def get_file_type(file_path):
    file_path_str = str(file_path)  # Convert PosixPath to string
    if file_path_str.lower().endswith((".png", ".jpg", ".jpeg")):
        return "photo"
    elif file_path_str.lower().endswith((".mp4", ".mkv", ".avi")):
        return "video"
    else:
        return "document"

# Function to send the file to user
async def send_file(update: Update, file_path, file_type):
    user_id = update.message.chat.id
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'
    
    if file_type == "photo":
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
    elif file_type == "video":
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendVideo'

    with open(file_path, 'rb') as f:
        files = {file_type: f}
        data = {'chat_id': user_id}
        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            await update.message.reply_text(f"File sent to {user_id}!")
        else:
            await update.message.reply_text(f"Error: {response.text}")

    # Remove the file after sending it
    os.remove(file_path)

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Send me a Mega link to download.")

# Handle Mega link
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.chat.id
    text = update.message.text
    
    if text.startswith("https://mega.nz/"):
        await update.message.reply_text(f"Received Mega link: {text}")

        # Download file from Mega
        file_path = download_file(text, user_id)
        if file_path:
            file_type = get_file_type(file_path)
            await send_file(update, file_path, file_type)
        else:
            await update.message.reply_text("Error downloading the file.")
    else:
        await update.message.reply_text("Please send a valid Mega link.")

# Cancel download
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Download canceled.")

# Main function to start the bot
def main():
    # Create the Application and pass it your bot's token.
    app = Application.builder().token(BOT_TOKEN).build()

    # Register command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register cancel button
    app.add_handler(CommandHandler("cancel", cancel))

    # Start the Bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
