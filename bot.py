import os
import json
import asyncio
import random
import secrets
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import requests

# Constants
BASIC_VIDEO_DIR = 'basic_videoes_dir'
LIMIT_FILE = 'limitses.json'
UNLIMITED_USERS_FILE = 'unlimited_user.json'
BROADCAST_USERS_FILE = 'user_id_forbroadcasts.json'
TOKENS_FILE = 'tokens.json'
PRIVATE_CHANNEL_ID = -1002412363758  # Replace with your private channel ID
PRIVATE_CHANNEL_INVITE_LINK = "https://t.me/+AejfSbyPvZdjY2E1"  # Replace with your channel invite link
ADMIN_ID = 6128121762  # Your admin ID
BOT_TOKEN = "7888078084:AAHTXqISPudFqKspHQQUOGGRSyBVQ6lWJNw"  # Replace with your bot token
STICKER_ID = "CAACAgUAAxkBAAKFZGcbti0amQABJBstAAHv6t5QtIL-gd0AAgQAA8EkMTGJ5R1uC7PIEDYE"

# Create necessary directories and files
def create_directories_and_files():
    for file_path in [BASIC_VIDEO_DIR, LIMIT_FILE, UNLIMITED_USERS_FILE, BROADCAST_USERS_FILE, TOKENS_FILE]:
        if not os.path.exists(file_path):
            if file_path.endswith('.json'):
                with open(file_path, 'w') as f:
                    json.dump({} if "limits" in file_path or "tokens" in file_path else [], f)
            else:
                os.makedirs(file_path)

create_directories_and_files()

def create_video_keyboard():
    keyboard = [[KeyboardButton("𝗚𝗘𝗧 𝗩𝗜𝗗𝗘𝗢 🍒 ")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id
    args = context.args

    # Check for token in /start command
    if args:
        token = args[0]
        with open(TOKENS_FILE, 'r') as f:
            tokens = json.load(f)

        if token in tokens and tokens[token]["user_id"] == user_id:
            await update.message.reply_text("Token verified! You now have access to 30 more videos.\n\nटोकन वेरिफाई  हो गया है! अब आपको 30 और वीडियो देखने का एक्सेस मिल गया है।")
            # Update limits for the user
            with open(LIMIT_FILE, 'r') as f:
                limits = json.load(f)
            user_limits = limits.get(str(user_id), {"date": datetime.now().date().isoformat(), "basic": 0, "sent_videos": []})
            user_limits['basic'] -= 30  # Reset limit
            limits[str(user_id)] = user_limits
            with open(LIMIT_FILE, 'w') as f:
                json.dump(limits, f)
            del tokens[token]
            with open(TOKENS_FILE, 'w') as f:
                json.dump(tokens, f)
            return
        else:
            await update.message.reply_text("Invalid or expired token.")
            return

    add_user_for_broadcast(user_id)
    sticker_message = await context.bot.send_sticker(chat_id=user_id, sticker=STICKER_ID)
    await asyncio.sleep(1)
    await context.bot.delete_message(chat_id=user_id, message_id=sticker_message.message_id)

    keyboard = [
        [InlineKeyboardButton("Ddose main [official]", url=PRIVATE_CHANNEL_INVITE_LINK)],
        [InlineKeyboardButton("Verify Now", callback_data="verify_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ꜱᴜʙꜱᴄʀɪʙᴇᴅ ᴛᴏ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ. ᴘʟᴇᴀꜱᴇ ꜱᴜʙꜱᴄʀɪʙᴇ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ!\n\nशायद आप चैनल को सब्सक्राइब नहीं किए हैं। कृपया सब्सक्राइब करें और फिर से प्रयास करें!", reply_markup=reply_markup)

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

async def handle_video_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id
    chat_member = await context.bot.get_chat_member(PRIVATE_CHANNEL_ID, user_id)
    if chat_member.status not in ["member", "administrator", "creator"]:
        await update.message.reply_text("Subscribe to the channel first!\nपहले चैनल को सब्सक्राइब करें!", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Ddose main [official]", url=PRIVATE_CHANNEL_INVITE_LINK)],
            [InlineKeyboardButton("Verify Now", callback_data="verify_membership")]
        ]))
        return

    with open(LIMIT_FILE, 'r') as f:
        limits = json.load(f)
    current_date = datetime.now().date().isoformat()
    user_limits = limits.get(str(user_id), {"date": current_date, "basic": 0, "sent_videos": []})
    if user_limits["date"] != current_date:
        user_limits = {"date": current_date, "basic": 0, "sent_videos": []}

    unlimited_access = has_unlimited_access(user_id)
    if not unlimited_access and user_limits['basic'] >= 10:
        token = secrets.token_urlsafe(16)
        with open(TOKENS_FILE, 'r') as f:
            tokens = json.load(f)
        tokens[token] = {"user_id": user_id, "expires": datetime.now().isoformat()}
        with open(TOKENS_FILE, 'w') as f:
            json.dump(tokens, f)

        long_url = f"https://telegram.dog/{context.bot.username}?start={token}"
        api_key = "5aeefe88b73cb53413d33bd6532adebe17c9c970"
        shorten_url = f"https://teraboxlinks.com/api?api={api_key}&url={long_url}&format=text"
        response = requests.get(shorten_url)
        short_link = response.text.strip()
        await update.message.reply_text(
    "𝗬𝗼𝘂𝗿 𝗔𝗱𝘀 𝘁𝗼𝗸𝗲𝗻 𝗶𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱, 𝗿𝗲𝗳𝗿𝗲𝘀𝗵 𝘆𝗼𝘂𝗿 𝘁𝗼𝗸𝗲𝗻 𝗮𝗻𝗱 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻.\n\n𝗧𝗼𝗸𝗲𝗻 𝘁𝗶𝗺𝗲𝗼𝘂𝘁: 𝗙𝗼𝗿 𝟯𝟬 𝘃𝗶𝗱𝗲𝗼 (𝗼𝗻𝗹𝘆 𝗧𝗼𝗱𝗮𝘆)\n\n𝗪𝗵𝗮𝘁 𝗶𝘀 𝘁𝗼𝗸𝗲𝗻?\n\n𝗜𝘁 𝗶𝘀 𝘃𝗲𝗿𝘆 𝗲𝗮𝘀𝘆 𝗷𝘂𝘀𝘁 𝘁𝗮𝗽 𝗼𝗻 𝗹𝗶𝗻𝗸 𝘄𝗮𝗶𝘁 𝟭𝟱 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝘁𝗵𝗲𝗻 𝗴𝗼 𝘁𝗼 𝘁𝗵𝗲 𝗹𝗮𝘀𝘁 𝗼𝗳 𝗽𝗮𝗴𝗲 𝗮𝗻𝗱 𝘁𝗮𝗽 𝗰𝗼𝗻𝘁𝗶𝗻𝘂𝗲 𝘁𝗵𝗮𝘁𝘀 𝗶𝘁\n\n"
     f"<a href='{short_link}'>CLICK HERE</a>",
    parse_mode='HTML')
        return

    video_files = os.listdir(BASIC_VIDEO_DIR)
    if video_files:
        available_videos = [file for file in video_files if file not in user_limits['sent_videos']]
        if not available_videos:
            await update.message.reply_text("All videos sent. Try again tomorrow or purchase membership. Contact [admin](https://t.me/Ddose_membership_contactbot) now" ,
              parse_mode='Markdown' )
            return

        selected_video_file = random.choice(available_videos)
        with open(os.path.join(BASIC_VIDEO_DIR, selected_video_file), 'r') as f:
            video_data = json.load(f)
        video_id = video_data['video_id']
        await context.bot.send_video(chat_id=user_id, video=video_id)
        if not unlimited_access:
            user_limits['basic'] += 1
        user_limits['sent_videos'].append(selected_video_file)
        limits[str(user_id)] = user_limits
        with open(LIMIT_FILE, 'w') as f:
            json.dump(limits, f)
    else:
        await update.message.reply_text("No videos available.")

async def verify_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    chat_member = await context.bot.get_chat_member(PRIVATE_CHANNEL_ID, user_id)
    if chat_member.status in ["member", "administrator", "creator"]:
        await query.answer("𝗖𝗢𝗡𝗚𝗥𝗔𝗧𝗨𝗟𝗔𝗧𝗜𝗢𝗡𝗦!! 𝗠𝗘𝗠𝗕𝗘𝗥𝗦𝗛𝗜𝗣 𝗩𝗘𝗥𝗜𝗙𝗜𝗘𝗗 ✓", show_alert=True)
        await query.message.reply_text("Tap on 𝗚𝗘𝗧 𝗩𝗜𝗗𝗘𝗢 \n𝗚𝗘𝗧 𝗩𝗜𝗗𝗘𝗢 पर टैप करें", reply_markup=create_video_keyboard())
    else:
        await query.answer("You are not a member. Join first.", show_alert=True)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == ADMIN_ID:
        video_file = update.message.video.file_id
        video_path = os.path.join(BASIC_VIDEO_DIR, f"{video_file}.json")
        with open(video_path, 'w') as f:
            json.dump({'video_id': video_file}, f)
        await update.message.reply_text("Video saved!")
    else:
        await update.message.reply_text("You are not authorized.")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(verify_membership, pattern="^verify_membership$"))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_request))
    application.run_polling()

if __name__ == '__main__':
    main()
