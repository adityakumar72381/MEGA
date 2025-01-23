from telethon import TelegramClient, events
from mega import Mega
import os
import re
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

# Bot configuration
api_id = '25396020'  # Get from https://my.telegram.org/auth
api_hash = '228ea638bed51dd4ae3cc9e4e51e198c'  # Get from https://my.telegram.org/auth
bot_token = "8001013935:AAHClukQGpt6AZbwvr-2gPgh0g5NPTgG4Eo"

logging.info("Initializing Mega API")
# Initialize Mega API
try:
    mega = Mega()
    m = mega.login()  # Anonymous login
    logging.info("Successfully logged into Mega API")
except Exception as e:
    logging.error(f"Failed to log into Mega API: {e}")
    raise

logging.info("Initializing Telethon bot")
# Initialize Telethon bot
try:
    client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
    logging.info("Bot started successfully")
except Exception as e:
    logging.error(f"Failed to start the bot: {e}")
    raise

# Start command
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    logging.info(f"Received /start command from chat ID {event.chat_id}")
    await event.reply("Welcome to the Mega Downloader Bot! Send me one or more Mega.nz links to download.")

# Handle Mega links
@client.on(events.NewMessage(pattern=r'https://mega.nz/'))
async def handle_mega_links(event):
    chat_id = event.chat_id
    text = event.text
    logging.info(f"Received Mega.nz links from chat ID {chat_id}: {text}")

    # Extract all Mega.nz links from the message
    mega_links = re.findall(r'https://mega.nz/[^\s]+', text)
    total_links = len(mega_links)
    logging.info(f"Found {total_links} Mega.nz link(s)")

    if total_links == 0:
        await event.reply("No valid Mega.nz links found in your message.")
        return

    # Inform the user about the total links found
    await event.reply(f"Detected {total_links} Mega.nz link(s). Downloading files one by one. Please wait...")

    # Process each link
    for i, mega_link in enumerate(mega_links, 1):
        try:
            logging.info(f"Downloading file {i} of {total_links}: {mega_link}")
            await event.reply(f"Downloading file {i} of {total_links}...")
            # Download the file from Mega.nz
            file = m.download_url(mega_link)
            file_path = str(file)

            # Send the file to the user
            await send_file(chat_id, file_path)
            logging.info(f"File {i} downloaded and sent successfully: {file_path}")
            await event.reply(f"File {i} of {total_links} sent successfully!")
        except Exception as e:
            logging.error(f"Error downloading file {i} of {total_links}: {e}")
            await event.reply(f"Failed to download file {i} of {total_links}. Error: {e}")

    await event.reply("All files have been processed.")

# Function to send the file
async def send_file(chat_id, file_path):
    file_type = get_file_type(file_path)
    logging.info(f"Sending file {file_path} as {file_type} to chat ID {chat_id}")
    with open(file_path, 'rb') as file:
        if file_type == "photo":
            await client.send_file(chat_id, file, caption="Here's your photo!", file_name=os.path.basename(file_path))
        elif file_type == "video":
            await client.send_file(chat_id, file, caption="Here's your video!", file_name=os.path.basename(file_path))
        else:
            await client.send_file(chat_id, file, caption="Here's your document!", file_name=os.path.basename(file_path))

    # Clean up by removing the file after sending
    os.remove(file_path)
    logging.info(f"File {file_path} removed after sending")

# Function to determine file type
def get_file_type(file_path):
    file_path = file_path.lower()
    if file_path.endswith((".png", ".jpg", ".jpeg")):
        return "photo"
    elif file_path.endswith((".mp4", ".mkv", ".avi")):
        return "video"
    else:
        return "document"

# Start the bot
try:
    logging.info("Starting the bot")
    client.start()
    client.run_until_disconnected()
except Exception as e:
    logging.error(f"Bot encountered an error: {e}")
    raise
