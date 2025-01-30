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
ADMIN_ID = 861435888  # Replace with your Telegram user ID

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
        shortcode_match = re.findall(r'instagram.com/(?:p|reel)/([a-zA-Z0-9-_]+)', instagram_url)
        if not shortcode_match:
            return None
        shortcode = shortcode_match[0]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        return post.video_url if post.is_video else None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

# Function to check if user has joined the channel
async def is_user_in_channel(user_id: int, context: CallbackContext) -> bool:
    try:
        chat_member = await context.bot.get_chat_member('@collagecampus', user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        return False

# Function to store user data
def store_user_data(user_id, username, mobile_number=None):
    # Here you can define how to store the data (e.g., save to a database or file)
    logger.info(f"Storing data for User ID: {user_id}, Username: {username}, Mobile: {mobile_number}")
    # Example: Save the data to a text file (you can modify this based on your requirements)
    with open("user_data.txt", "a") as file:
        file.write(f"User ID: {user_id}, Username: {username}, Mobile: {mobile_number}\n")

async def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Join Our Telegram Channel", url=CHANNEL_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Join our channel to use the bot.", reply_markup=reply_markup)

async def contact(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Contact Support", url="https://t.me/Send_UPI_ID_here_bot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("For help, click below:", reply_markup=reply_markup)

async def process_request(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    message_text = update.message.text
    mobile_number = update.message.contact.phone_number if update.message.contact else None

    # Store user data
    store_user_data(user_id, username, mobile_number)
    
    if not await is_user_in_channel(user_id, context):
        keyboard = [[InlineKeyboardButton("Join Our Telegram Channel", url=CHANNEL_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Join our channel to continue.", reply_markup=reply_markup)
        return

    if "instagram.com" not in message_text:
        await update.message.reply_text("Send a valid Instagram video link.")
        return

    video_url = download_instagram_video(message_text)
    
    if video_url:
        processing_message = await update.message.reply_text("Processing your video...")
        await update.message.reply_video(video_url)
        await processing_message.delete()
    else:
        await update.message.reply_text("This is not a valid Instagram video or reel.")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ Error for user {username} ({user_id}) - Invalid Instagram link: {message_text}")

async def broadcast(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    
    message = " ".join(context.args)
    # Assuming you have a list of user IDs to send the broadcast
    user_ids = [123456789, 987654321]  # Example user IDs
    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except:
            continue

# Main function
def main():
    if not BOT_TOKEN:
        logger.error("Bot token missing!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("contact", contact))
    application.add_handler(CommandHandler("broadcast", broadcast, filters=filters.User(ADMIN_ID)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_request))
    
    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
