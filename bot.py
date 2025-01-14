from mega import Mega
from pyrogram import Client, filters
import os

# MEGA credentials
MEGA_EMAIL = "adityakumar72381@gmail.com"
MEGA_PASSWORD = "a1d2i3t4y5a6"

# Telegram bot credentials
API_ID = "25396020"
API_HASH = "228ea638bed51dd4ae3cc9e4e51e198c"
BOT_TOKEN = "7508849360:AAFmc5bxm5rgHTkocv9iFOgHWap6tX-ZIrg"

# Initialize MEGA client
mega = Mega()
mega_client = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

# Initialize Telegram bot
app = Client("mega_download_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary download folder
DOWNLOAD_FOLDER = "downloads/"

# Ensure the download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.on_message(filters.command("start"))
def start(_, message):
    message.reply_text("Send me a MEGA folder link, and I'll download the files one by one for you!")

@app.on_message(filters.regex(r"https://mega.nz/folder/.*"))
def download_mega_folder(_, message):
    folder_link = message.text.strip()
    message.reply_text("Processing your MEGA folder link...")

    try:
        # Get the folder details
        folder = mega_client.get_public_folder(folder_link)
        files = folder["folder"]["files"]

        if not files:
            message.reply_text("The folder is empty.")
            return

        # Loop through files and send them
        for file in files:
            file_name = file["a"]["n"]
            file_size = file["s"]
            message.reply_text(f"Downloading: {file_name} ({file_size} bytes)")

            # Download file
            file_path = mega_client.download_url(file["g"], dest_filename=os.path.join(DOWNLOAD_FOLDER, file_name))

            # Send file
            message.reply_document(file_path)
            
            # Remove file after sending
            os.remove(file_path)

        message.reply_text("All files have been sent!")

    except Exception as e:
        message.reply_text(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
