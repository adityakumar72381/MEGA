import os
import json
import asyncio
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BASIC_VIDEO_DIR = 'basic_video_dir'
PREMIUM_VIDEO_DIR = 'premium_video_dir'
LIMIT_FILE = 'limits.json'
UNLIMITED_USERS_FILE = 'unlimited_users.json'
BROADCAST_USERS_FILE = 'user_id_forbroadcast.json'
ADMIN_ID = 6128121762  # Admin's ID
ADMIN_CONTACT_BOT = "https://t.me/Ddose_membership_contactbot"

def create_directories_and_files():
    if not os.path.exists(BASIC_VIDEO_DIR):
        os.makedirs(BASIC_VIDEO_DIR)
    if not os.path.exists(PREMIUM_VIDEO_DIR):
        os.makedirs(PREMIUM_VIDEO_DIR)
    if not os.path.exists(LIMIT_FILE):
        with open(LIMIT_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(UNLIMITED_USERS_FILE):
        with open(UNLIMITED_USERS_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(BROADCAST_USERS_FILE):
        with open(BROADCAST_USERS_FILE, 'w') as f:
            json.dump([], f)

create_directories_and_files()

def create_video_keyboard():
    keyboard = [
        [KeyboardButton("Basic Videos"), KeyboardButton("Premium Videos")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def create_save_video_keyboard():
    keyboard = [
        [InlineKeyboardButton("Save in Basic Videos", callback_data='save_basic')],
        [InlineKeyboardButton("Save in Premium Videos", callback_data='save_premium')]
    ]
    return InlineKeyboardMarkup(keyboard)



STICKER_ID = "CAACAgUAAxkBAAKFZGcbti0amQABJBstAAHv6t5QtIL-gd0AAgQAA8EkMTGJ5R1uC7PIEDYE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id
    add_user_for_broadcast(user_id)

    # Send the sticker and store the message object to get the message_id
    sticker_message = await context.bot.send_sticker(chat_id=user_id, sticker=STICKER_ID)

    # Wait for 1 second
    await asyncio.sleep(1)

    # Delete the sticker message
    await context.bot.delete_message(chat_id=user_id, message_id=sticker_message.message_id)
    # Send the first message with the join link
    await update.message.reply_text(
        "Must Joinâ¬‡ï¸\nhttps://t.me/+adhSk-n9lXY5NzM1\n\nThis bot was made using @LivegramBot"
    )

    # Wait for 5 seconds
    await asyncio.sleep(5)

    # Send the final message asking for video type selection
    await update.message.reply_text(
        "Please choose which type of video you want:",
        reply_markup=create_video_keyboard()
    )
def add_user_for_broadcast(user_id):
    with open(BROADCAST_USERS_FILE, 'r') as f:
        broadcast_users = json.load(f)

    if user_id not in broadcast_users:
        broadcast_users.append(user_id)
        with open(BROADCAST_USERS_FILE, 'w') as f:
            json.dump(broadcast_users, f)

def has_unlimited_access(user_id):
    with open(UNLIMITED_USERS_FILE, 'r') as f:
        unlimited_users = json.load(f)
    return user_id in unlimited_users

async def handle_video_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id
    video_type = update.message.text.strip()

    with open(LIMIT_FILE, 'r') as f:
        limits = json.load(f)

    current_date = datetime.now().date().isoformat()
    user_limits = limits.get(str(user_id), {"date": current_date, "basic": 0, "premium": 0, "sent_videos": []})

    if user_limits["date"] != current_date:
        user_limits = {"date": current_date, "basic": 0, "premium": 0, "sent_videos": []}

    unlimited_access = has_unlimited_access(user_id)

    if video_type.lower() == 'basic videos':
        if not unlimited_access and user_limits['basic'] >= 10:
            await update.message.reply_text(
                "Your daily limit for basic videos has been exceeded. Please contact [Admin](https://t.me/Ddose_membership_contactbot) or try again tomorrow.",
                parse_mode='Markdown'
            )
            return
        directory = BASIC_VIDEO_DIR
    elif video_type.lower() == 'premium videos':
        if not unlimited_access and user_limits['premium'] >= 1:
            await update.message.reply_text(
                "Your daily limit for premium videos has been exceeded. Please contact [Admin](https://t.me/Ddose_membership_contactbot) or try again tomorrow.",
                parse_mode='Markdown'
            )
            return
        directory = PREMIUM_VIDEO_DIR
    else:
        await update.message.reply_text("Invalid selection. Please select 'Basic Videos' or 'Premium Videos'.", reply_markup=create_video_keyboard())
        return

    video_files = os.listdir(directory)

    if video_files:
        available_videos = [file for file in video_files if file not in user_limits['sent_videos']]

        if not available_videos:
            await update.message.reply_text("All videos have been sent today. Please try again tomorrow.", reply_markup=create_video_keyboard())
            return

        selected_video_file = random.choice(available_videos)

        with open(os.path.join(directory, selected_video_file), 'r') as f:
            video_data = json.load(f)

        video_id = video_data['video_id']
        await context.bot.send_video(chat_id=user_id, video=video_id)

        if not unlimited_access:
            if video_type.lower() == 'basic videos':
                user_limits['basic'] += 1
            else:
                user_limits['premium'] += 1

        user_limits['sent_videos'].append(selected_video_file)

        limits[str(user_id)] = user_limits

        with open(LIMIT_FILE, 'w') as f:
            json.dump(limits, f)
    else:
        await update.message.reply_text("No videos available in the selected category.", reply_markup=create_video_keyboard())

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == ADMIN_ID:
        video_file = update.message.video.file_id
        context.user_data['last_video_file'] = video_file

        await update.message.reply_text(
            "Which directory would you like to save the video in?",
            reply_markup=create_save_video_keyboard()
        )
    else:
        await update.message.reply_text("You are not authorized to send videos.")

async def handle_video_saving(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    video_id = context.user_data.get('last_video_file')
    if video_id is None:
        await query.message.reply_text("No video file to save.")
        return

    if query.data == 'save_basic':
        directory = BASIC_VIDEO_DIR
    elif query.data == 'save_premium':
        directory = PREMIUM_VIDEO_DIR
    else:
        await query.message.reply_text("Invalid selection. Please select 'Save in Basic Videos' or 'Save in Premium Videos'.")
        return

    video_path = os.path.join(directory, f"{video_id}.json")

    with open(video_path, 'w') as f:
        json.dump({'video_id': video_id}, f)

    await query.message.reply_text("Video ID saved successfully!")

async def add_unlimited_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to add users to the unlimited access list.")
        return

    if context.args:
        user_id = int(context.args[0])
        with open(UNLIMITED_USERS_FILE, 'r') as f:
            unlimited_users = json.load(f)

        if user_id not in unlimited_users:
            unlimited_users.append(user_id)
            with open(UNLIMITED_USERS_FILE, 'w') as f:
                json.dump(unlimited_users, f)
            await update.message.reply_text(f"User {user_id} has been granted unlimited access.")
        else:
            await update.message.reply_text(f"User {user_id} already has unlimited access.")
    else:
        await update.message.reply_text("Please provide a user ID.")

async def clear_unlimited_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == ADMIN_ID:
        with open(UNLIMITED_USERS_FILE, 'w') as f:
            json.dump([], f)
        await update.message.reply_text("The unlimited users list has been cleared.")
    else:
        await update.message.reply_text("You are not authorized to perform this action.")

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to perform this action.")
        return

    context.user_data['broadcast_pending'] = True
    await update.message.reply_text("Please send the video, photo, or text message you wish to broadcast. Use /cancelled to abort.")

async def handle_broadcast_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('broadcast_pending'):
        description = update.message.caption if update.message.caption else None
        with open(BROADCAST_USERS_FILE, 'r') as f:
            broadcast_users = json.load(f)

        # Check if the message contains a photo
        if update.message.photo:
            photo_file = update.message.photo[-1].file_id

            for user_id in broadcast_users:
                try:
                    await context.bot.send_photo(chat_id=user_id, photo=photo_file, caption=description)
                except Exception as e:
                    print(f"Failed to send photo to {user_id}: {e}")

            await update.message.reply_text("Broadcast photo sent successfully!")

        # Check if the message contains a video
        elif update.message.video:
            video_file = update.message.video.file_id

            for user_id in broadcast_users:
                try:
                    await context.bot.send_video(chat_id=user_id, video=video_file, caption=description)
                except Exception as e:
                    print(f"Failed to send video to {user_id}: {e}")

            await update.message.reply_text("Broadcast video sent successfully!")

        # Handle text broadcasting if only a description is provided without media
        elif description:
            for user_id in broadcast_users:
                try:
                    await context.bot.send_message(chat_id=user_id, text=description)
                except Exception as e:
                    print(f"Failed to send message to {user_id}: {e}")

            await update.message.reply_text("Broadcast message sent successfully!")

        else:
            await update.message.reply_text("Please provide a message, video, or photo to broadcast.")

        # Reset the broadcast pending state
        context.user_data['broadcast_pending'] = False

async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('broadcast_pending'):
        context.user_data['broadcast_pending'] = False
        await update.message.reply_text("Broadcast has been cancelled.")
    else:
        await update.message.reply_text("No broadcast is currently in progress.")

def main() -> None:
    application = Application.builder().token("8118599107:AAFeLN26fLJrIWBFmzg3XdusIXg46Qchb30").build()  # Insert your token here

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_type_selection))
    application.add_handler(CallbackQueryHandler(handle_video_saving, pattern='save_basic|save_premium'))
    application.add_handler(CommandHandler("add", add_unlimited_user))
    application.add_handler(CommandHandler("clear", clear_unlimited_users))
    application.add_handler(CommandHandler("broadcast", broadcast_message))
    application.add_handler(MessageHandler(filters.TEXT | filters.VIDEO | filters.PHOTO, handle_broadcast_content))
    application.add_handler(CommandHandler("cancelled", cancel_broadcast))

    application.run_polling()

if __name__ == '__main__':
    main()
