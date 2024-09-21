from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
import os

# Function to download video
def download_video(video_url, filename):
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(filename,'downloaded_file.bin') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filename
    return None

# Function to get download links
def get_download_links(video_url):
    api_endpoint = f'https://ashlynn.serv00.net/Ashlynnterabox.php/?url={video_url}'
    
    response = requests.get(api_endpoint)
    
    if response.status_code == 200:
        json_response = response.json()
        if 'response' in json_response:
            fast_download_link = json_response['response'][0]['resolutions']['Fast Download']
            return fast_download_link
        else:
            return None
    return None

# Function to create the Watch Online URL
def get_watch_online_url(video_url):
    return f'https://watch-terabox.ashlynn.workers.dev/?url={video_url}'

# Command to start the bot
async def start(update: Update, context) -> None:
    await update.message.reply_text('Welcome! Send me a video URL to get the video.')

# Function to handle messages
async def handle_message(update: Update, context) -> None:
    video_url = update.message.text
    fast_download_link = get_download_links(video_url)
    
    # Prepare the buttons for "Watch Online" and "Fast Download"
    watch_online_url = get_watch_online_url(video_url)
    keyboard = [
        # Web App button for Watch Online
        [InlineKeyboardButton("Watch Online", web_app=WebAppInfo(url=watch_online_url))],
        [InlineKeyboardButton("Fast Download", url=fast_download_link)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if fast_download_link:
        filename = 'video.mp4'  # Temporary filename
        downloaded_file = download_video(fast_download_link, filename)
        
        if downloaded_file:
            # If the bot successfully downloads the video, send the video file
            await update.message.reply_video(video=open(downloaded_file, 'rb'))
            os.remove(downloaded_file)  # Clean up the downloaded file
        else:
            # If download fails, send the buttons for manual download
            await update.message.reply_text("Failed to download the video. You can watch or download it manually:", reply_markup=reply_markup)
    else:
        # If no valid link found, send the buttons for manual watch/download
        await update.message.reply_text("No valid link found. You can watch or download the video online:", reply_markup=reply_markup)

def main():
    app = Application.builder().token("8128737803:AAG4mXx7mvdvZXESouv8DtIrQYmxZTpHIto").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()
