import os
import requests
import m3u8
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re

app = Flask(__name__)

# Function to convert TeraBox link to downloadable .m3u8 link
def convert_link(link: str) -> str:
    match = re.search(r's/([\w-]+)', link)
    if match:
        video_id = match.group(1)
        return f"https://apis.forn.fun/tera/m3u8.php?id={video_id}"
    return None

# Function to download video segments and merge them into a single file
def download_video(m3u8_url: str, file_path: str) -> bool:
    try:
        m3u8_obj = m3u8.load(m3u8_url)
        segment_urls = [seg.absolute_uri for seg in m3u8_obj.segments]

        # Open the target file for writing in binary mode
        with open(file_path, 'wb') as video_file:
            for segment_url in segment_urls:
                response = requests.get(segment_url, stream=True)
                if response.status_code == 200:
                    video_file.write(response.content)
                else:
                    print(f"Failed to download segment: {segment_url}")
                    return False

        return True
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False

# Function to download a fixed thumbnail image
def download_thumbnail() -> str:
    thumbnail_url = "https://envs.sh/nkz.jpg"
    thumbnail_path = os.path.join(os.getcwd(), 'thumbnail.jpg')
    response = requests.get(thumbnail_url)
    if response.status_code == 200:
        with open(thumbnail_path, 'wb') as thumbnail_file:
            thumbnail_file.write(response.content)
        return thumbnail_path
    return None

# Define a command handler for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a TeraBox link and I'll download the video for you.")

# Define a message handler for text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    downloadable_link = convert_link(user_message)

    if downloadable_link:
        temp_file_path = os.path.join(os.getcwd(), 'downloaded_video.mp4')

        # Download the video from the .m3u8 link
        if download_video(downloadable_link, temp_file_path):
            # Download the fixed thumbnail
            thumbnail_path = download_thumbnail()
            
            # Send the video with the thumbnail
            with open(temp_file_path, 'rb') as video_file:
                await update.message.reply_video(video_file, thumb=open(thumbnail_path, 'rb'), caption="Here’s your video!")
            
            # Clean up
            os.remove(temp_file_path)
            if thumbnail_path:
                os.remove(thumbnail_path)
        else:
            await update.message.reply_text("Failed to download the video.")
    else:
        await update.message.reply_text("Invalid TeraBox link format.")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True))
    application = ApplicationBuilder().token(os.getenv("8128737803:AAGa3Dat8M5irxGzA7is0gs_Rf0wbS6p9V0")).build()
    application.process_update(update)
    return '', 200

if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))  # Listen on the specified port
