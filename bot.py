from telethon import TelegramClient, events
from mega import Mega
import os

# Bot configuration
api_id = '25396020'  # Get from https://my.telegram.org/auth
api_hash = '228ea638bed51dd4ae3cc9e4e51e198c'  # Get from https://my.telegram.org/auth
bot_token = '7508849360:AAEl4izVzT9uZa2kvYUFnWD7U3TDlDLMVtU'

# Initialize Mega API
mega = Mega()
m = mega.login()  # Anonymous login

# Initialize Telethon bot
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Start command
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Welcome to the Mega Downloader Bot! Send me a Mega.nz link to download.")

# Handle Mega links
@client.on(events.NewMessage(pattern=r'https://mega.nz/'))
async def handle_mega_link(event):
    chat_id = event.chat.id
    mega_link = event.text

    try:
        # Download the file from Mega
        await event.reply("Downloading file, please wait...")
        file = m.download_url(mega_link)
        file_path = str(file)

        # Send the file to the user
        await send_file(chat_id, file_path)
        await event.reply("File sent successfully!")
    except Exception as e:
        await event.reply(f"Failed to download the file. Error: {e}")

# Function to send the file
async def send_file(chat_id, file_path):
    file_type = get_file_type(file_path)
    with open(file_path, 'rb') as file:
        if file_type == "photo":
            await client.send_file(chat_id, file, caption="Here's your photo!", file_name=os.path.basename(file_path))
        elif file_type == "video":
            await client.send_file(chat_id, file, caption="Here's your video!", file_name=os.path.basename(file_path))
        else:
            await client.send_file(chat_id, file, caption="Here's your document!", file_name=os.path.basename(file_path))

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

# Start the bot
client.start()
client.run_until_disconnected()
