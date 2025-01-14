from mega import Mega
from pyrogram import Client, filters
import os

# MEGA credentials
MEGA_EMAIL = "adityakumar72381@gmail.com"
MEGA_PASSWORD = "a1d2i3t4y5a6"

# Telegram bot credentials
API_ID = 25396020
API_HASH = "228ea638bed51dd4ae3cc9e4e51e198c"
BOT_TOKEN = "7508849360:AAFmc5bxm5rgHTkocv9iFOgHWap6tX-ZIrg"

# Initialize MEGA client
mega = Mega()
mega_client = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

# Initialize Telegram bot
app = Client("mega_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary download folder
DOWNLOAD_FOLDER = "downloads/"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Hi! Send me a MEGA file or folder link, and I'll download it for you.")

@app.on_message(filters.regex(r"https://mega.nz/.*"))
def download_mega_link(client, message):
    link = message.text.strip()
    message.reply_text("Processing your MEGA link...")

    try:
        if "/file/" in link:
            # Download a single file
            file = mega_client.get_public_url(link)
            file_name = file["name"]
            file_size = file["size"]
            message.reply_text(f"Downloading file: {file_name} ({file_size} bytes)")

            file_path = mega_client.download_url(link, dest_filename=os.path.join(DOWNLOAD_FOLDER, file_name))
            message.reply_document(file_path)
            os.remove(file_path)  # Clean up

        elif "/folder/" in link:
            # Download a folder
            folder = mega_client.get_public_folder(link)
            files = folder["folder"]["files"]

            if not files:
                message.reply_text("The folder is empty.")
                return

            for file in files:
                file_name = file["a"]["n"]
                file_size = file["s"]
                message.reply_text(f"Downloading file: {file_name} ({file_size} bytes)")

                file_path = mega_client.download(file, dest_filename=os.path.join(DOWNLOAD_FOLDER, file_name))
                message.reply_document(file_path)
                os.remove(file_path)  # Clean up

            message.reply_text("All files have been sent!")

    except Exception as e:
        message.reply_text(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
