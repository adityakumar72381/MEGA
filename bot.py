import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context):
    temp_file_path = "/path/to/temp/video.mp4"  # Example path
    
    try:
        if is_valid_link(update.message.text):  # Assuming is_valid_link is defined elsewhere
            downloaded = download_video(update.message.text, temp_file_path)  # Assuming download_video is defined elsewhere
            if downloaded:
                try:
                    with open(temp_file_path, 'rb') as file:
                        await update.message.reply_video(file)
                    await update.message.reply_text("✅ Your video has been downloaded and sent! Enjoy! 🎉")
                except Exception as e:
                    logger.error(f"Failed to send video: {e}")
                    await update.message.reply_text("⚠️ There was an error sending your video. Please try again.")
                finally:
                    try:
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)  # Clean up the temporary video file
                            logger.info("Temporary file cleaned up.")
                    except Exception as e:
                        logger.error(f"Error deleting temporary file: {e}")
            else:
                await update.message.reply_text("⚠️ Failed to download the video. Please try again later.")
        else:
            await update.message.reply_text("⚠️ Invalid TeraBox link format. Please send a valid link.")
    
    except Exception as e:
        logger.error(f"An error occurred in handle_message: {e}")
        await update.message.reply_text("⚠️ An unexpected error occurred. Please try again later.")

async def start(update: Update, context):
    try:
        await update.message.reply_text("Welcome! Send me a TeraBox link to download your video.")
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")

def main():
    try:
        application = ApplicationBuilder().token("8128737803:AAHIbZkvw2c1nd4RysiMw0k9u1C1M7dCwWY").build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.run_polling()
    except Exception as e:
        logger.error(f"Error initializing the bot: {e}")

if __name__ == "__main__":
    main()
