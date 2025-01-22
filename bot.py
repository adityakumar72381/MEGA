import telebot
from mega import Mega
import os
import requests

# Bot token
BOT_TOKEN = "7833206147:AAH17nVkgDhJ5UvzfJly7OJ_za0g4PIt9_U"
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize Mega API
mega = Mega()
m = mega.login()  # Anonymous login

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to the Mega Downloader Bot! Send me a Mega.nz link to download.")

# Handle Mega links
@bot.message_handler(func=lambda message: message.text.startswith("https://mega.nz/"))
def handle_mega_link(message):
    chat_id = message.chat.id
    mega_link = message.text

    try:
        # Download the file from Mega
        bot.send_message(chat_id, "Downloading file, please wait...")
        file = m.download_url(mega_link)
        file_path = str(file)

        # Send the file to the user
        send_file(chat_id, file_path)
        bot.send_message(chat_id, "File sent successfully!")
    except Exception as e:
        bot.send_message(chat_id, f"Failed to download the file. Error: {e}")

# Function to send the file
def send_file(chat_id, file_path):
    file_type = get_file_type(file_path)
    with open(file_path, 'rb') as file:
        if file_type == "photo":
            bot.send_photo(chat_id, file)
        elif file_type == "video":
            bot.send_video(chat_id, file)
        else:
            bot.send_document(chat_id, file)

    # Clean up by removing the file after sending
    os.remove(file_path)

# Function to determine file type
def get_file_type(file_path):
    file_path = file_path.lower()
    if file_path.endswith((".png", ".jpg", ".jpeg")):
        return "photo"
    elif file_path.endswith((".mp4", ".mkv", ".avi")):
        return "video"
    else:
        return "document"

# Polling the bot
print("Bot is running...")
bot.polling()
