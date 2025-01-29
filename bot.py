import logging
import instaloader
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import os

# Load bot token from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = ADMIN_ID = 861435888  # Replace this with your Telegram ID

# Initialize Instaloader object
L = instaloader.Instaloader()

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram channel link
CHANNEL_LINK = "https://t.me/collagecampus"

# Function to extract Instagram video URL
def download_instagram_video(instagram_url):
    try:
        shortcode = re.findall(r'\/(p|reel)\/([a-zA-Z0-9-_]+)', instagram_url)[0][1]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        if post.is_video:
            return post.video_url
        return None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

# Function to check if user has joined the channel
async def is_user_in_channel(user_id: int, context: CallbackContext) -> bool:
    try:
        chat_member = await context.bot.get_chat_member('@collagecampus', user_id)
        logger.info(f"User {user_id} status in channel: {chat_member.status}")
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.warning(f"Error checking user channel membership: {e}")
        return False

# Start command
async def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Join Our Telegram Channel", url=CHANNEL_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to the Instagram Video Downloader Bot!\n"
        "To use the bot, please join our Telegram channel.\n"
        "Once you join, you can send the Instagram video link for processing!",
        reply_markup=reply_markup
    )

# Help/Contact command
async def contact(update: Update, context: CallbackContext):
    await update.message.reply_text("For any support, contact @Send_UPI_ID_here_bot")

# Process user requests
async def process_request(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message_text = update.message.text

    if not await is_user_in_channel(user_id, context):
        keyboard = [[InlineKeyboardButton("Join Our Telegram Channel", url=CHANNEL_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "You need to join our Telegram channel to download videos!\n"
            "Please join the channel and send the link again.",
            reply_markup=reply_markup
        )
        return

    instagram_url_regex = r"(https?://(?:www\.)?instagram\.com/(?:p|reel)/[\w-]+)/"
    match = re.match(instagram_url_regex, message_text)

    if match:
        instagram_url = match.group(0)
        video_url = download_instagram_video(instagram_url)

        if video_url:
            processing_message = await update.message.reply_text("Processing your video... Please wait.")
            await update.message.reply_video(video_url)
            await processing_message.delete()
        else:
            await update.message.reply_text("This is not a valid Instagram video or reel.")
    else:
        await update.message.reply_text("Please send a valid Instagram video link.")

# Broadcast message (only for admin)
async def broadcast(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message here")
        return
    
    message = " ".join(context.args)
    for chat_id in context.bot_data.get("subscribers", []):
        try:
            await context.bot.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
    await update.message.reply_text("Broadcast sent successfully!")

# Main function
def main():
    if not BOT_TOKEN:
        logger.error("Bot token not found. Please make sure the .env file is set up correctly.")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("contact", contact))
    application.add_handler(CommandHandler("broadcast", broadcast, filters.User(ADMIN_ID)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_request))
    
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
