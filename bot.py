import os
import aiohttp
import aiofiles
import m3u8
import tempfile
import asyncio
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re

# File path for saving video IDs
VIDEO_RECORD_FILE = 'video_bot.json'

# Function to convert TeraBox link to downloadable .m3u8 link
def convert_link(link: str) -> str:
    match = re.search(r's/([\w-]+)', link)
    if match:
        video_id = match.group(1)
        return f"https://apis.forn.fun/tera/m3u8.php?id={video_id}", video_id
    return None, None

# Function to download video segments and merge them into a single file with progress updates
async def download_video(m3u8_url: str, file_path: str, update: Update) -> bool:
    try:
        m3u8_obj = m3u8.load(m3u8_url)
        segment_urls = [seg.absolute_uri for seg in m3u8_obj.segments]
        total_segments = len(segment_urls)
        
        async with aiohttp.ClientSession() as session:
            async with aiofiles.open(file_path, 'wb') as video_file:
                # Download all segments concurrently
                tasks = [
                    download_segment(session, segment_url, video_file, idx, total_segments, update)
                    for idx, segment_url in enumerate(segment_urls)
                ]
                await asyncio.gather(*tasks)

        return True
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error downloading video: {e}")
        return False

# Function to download a single segment with retry logic
async def download_segment(session, segment_url, video_file, idx, total_segments, update, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(segment_url) as response:
                if response.status == 200:
                    await video_file.write(await response.read())
                    if idx % 10 == 0 or idx == total_segments - 1:  # Send progress every 10 segments
                        progress = (idx + 1) / total_segments * 100
                        await update.message.reply_text(f"⬇️ Download progress: {progress:.2f}%")
                    return
        except Exception as e:
            print(f"Error downloading segment {segment_url} on attempt {attempt + 1}: {e}")
            await asyncio.sleep(2)  # Wait before retrying
    print(f"Failed to download segment after {retries} attempts: {segment_url}")
    raise Exception(f"Failed to download segment: {segment_url}")

# Function to save the video ID to a JSON file
def save_video_id(video_id: str):
    if os.path.exists(VIDEO_RECORD_FILE):
        with open(VIDEO_RECORD_FILE, 'r') as file:
            video_data = json.load(file)
    else:
        video_data = {}

    video_data[video_id] = {"downloaded": True}

    with open(VIDEO_RECORD_FILE, 'w') as file:
        json.dump(video_data, file, indent=4)

# Define a command handler for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the TeraBox Video Downloader Bot!\n"
        "🔗 Send me a TeraBox link, and I'll download the video for you! 🎥"
    )

# Define a message handler for text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    downloadable_link, video_id = convert_link(user_message)
    
    if downloadable_link and video_id:
        await update.message.reply_text("🚀 Downloading your video, please wait... ⏳")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_file_path = temp_video_file.name
        
        if await download_video(downloadable_link, temp_file_path, update):
            with open(temp_file_path, 'rb') as file:
                await update.message.reply_video(file)
            
            os.remove(temp_file_path)  # Clean up the temporary video file
            await update.message.reply_text("✅ Your video has been downloaded and sent! Enjoy! 🎉")
            
            # Save the video ID after successful download
            save_video_id(video_id)
        else:
            await update.message.reply_text("⚠️ Failed to download the video. Please try again later.")
    else:
        await update.message.reply_text("⚠️ Invalid TeraBox link format. Please send a valid link.")

def main():
    bot_token = os.getenv("8128737803:AAGTqn4OGufZYhByWTVGmFgITL-v0cy3D1g")  # Store the token as an environment variable
    application = ApplicationBuilder().token(bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
