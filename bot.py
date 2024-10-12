import os
import requests
import m3u8
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re

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
                    # Write each segment's content to the video file
                    video_file.write(response.content)
                else:
                    print(f"Failed to download segment: {segment_url}")
                    return False
        
        return True
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False

# Define a command handler for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the TeraBox Video Downloader Bot!\n"
        "🔗 Send me a TeraBox link, and I'll download the video for you! 🎥"
    )

# Define a message handler for text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    downloadable_link = convert_link(user_message)
    
    if downloadable_link:
        temp_file_path = os.path.join(os.getcwd(), 'downloaded_video.mp4')
        
        await update.message.reply_text("🚀 Downloading your video, please wait... ⏳")
        
        # Download the video from the .m3u8 link
        if download_video(downloadable_link, temp_file_path):
            with open(temp_file_path, 'rb') as file:
                # Use the thumbnail image
                thumbnail_url = "https://envs.sh/nkz.jpg"
                thumbnail_path = os.path.join(os.getcwd(), 'thumbnail.jpg')
                
                # Download the thumbnail image
                response = requests.get(thumbnail_url)
                with open(thumbnail_path, 'wb') as thumb_file:
                    thumb_file.write(response.content)

                await update.message.reply_video(
                    video=file,
                    thumb=InputFile(thumbnail_path)  # Add the thumbnail
                )
                
                # Clean up the temporary files
                os.remove(temp_file_path)
                os.remove(thumbnail_path)
                
                await update.message.reply_text("✅ Your video has been downloaded and sent! Enjoy! 🎉")
        else:
            await update.message.reply_text("❌ Failed to download the video. Please try again.")
    else:
        await update.message.reply_text("⚠️ Invalid TeraBox link format. Please send a valid link.")

def main():
    # Directly use the token here
    application = ApplicationBuilder().token("8128737803:AAEFMV57HxE5AKiW_Clu5j_VQ0omFS3a1m0").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
