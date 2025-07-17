import os
import logging
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your own bot token
BOT_TOKEN = '8058115281:AAGwpQCHGYeRd1wryKfKrAQPtt6Z75HdVeU'

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Welcome! Send me a YouTube link to download audio or video.")

# Handle YouTube links
def handle_message(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    if "youtube.com" in url or "youtu.be" in url:
        keyboard = [
            [InlineKeyboardButton("🎥 Download Video", callback_data=f"video|{url}")],
            [InlineKeyboardButton("🎧 Download Audio", callback_data=f"audio|{url}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("🔽 Choose what you want to download:", reply_markup=reply_markup)
    else:
        update.message.reply_text("❌ Please send a valid YouTube link.")

# Handle button press
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    choice, url = query.data.split("|")

    msg = query.message.reply_text("⏳ Downloading, please wait...")

    try:
        if choice == "video":
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/video.%(ext)s',
            }
        elif choice == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if choice == "audio":
                filename = os.path.splitext(filename)[0] + ".mp3"

        with open(filename, 'rb') as f:
            if choice == "video":
                query.message.reply_video(f)
            else:
                query.message.reply_audio(f)

        msg.edit_text("✅ Download complete!")
        os.remove(filename)

    except Exception as e:
        logger.error(str(e))
        msg.edit_text("❌ Failed to download. Please try again.")

# Main function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(button_callback))

    print("✅ Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
