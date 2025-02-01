import logging
import instaloader
<<<<<<< HEAD
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 861435888  # Replace with your Telegram admin ID

# Initialize Instaloader
L = instaloader.Instaloader()

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
=======
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
>>>>>>> 63d00f4872f960a03d2ed7a9b0e3f706ff48b298
logger = logging.getLogger(__name__)

# Telegram channel link
CHANNEL_LINK = "https://t.me/collagecampus"

<<<<<<< HEAD
# Function to notify admin about errors
async def notify_admin(error_msg, user_id, username, context: CallbackContext):
    admin_message = (
        f"🚨 *Error Alert*\n"
        f"👤 User ID: `{user_id}`\n"
        f"📛 Username: `{username}`\n"
        f"❌ Error: `{error_msg}`"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

# Function to check if the user is in the channel
=======
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
>>>>>>> 63d00f4872f960a03d2ed7a9b0e3f706ff48b298
async def is_user_in_channel(user_id: int, context: CallbackContext) -> bool:
    try:
        chat_member = await context.bot.get_chat_member('@collagecampus', user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
<<<<<<< HEAD
        logger.warning(f"Error checking user channel membership: {e}")
        return False

# Function to start the bot
async def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Join Our Telegram Channel", url=CHANNEL_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome! To use this bot, please join our Telegram channel first.",
        reply_markup=reply_markup
    )

# Function to clean the URL by removing query parameters like `==`
def clean_instagram_url(url: str) -> str:
    # Remove query parameters after '?' and '#' to ensure URL is clean
    clean_url = url.split('?')[0]
    clean_url = clean_url.split('#')[0]
    return clean_url

# Function to process Instagram media requests directly
async def process_request(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "N/A"
    message_text = update.message.text

    if not await is_user_in_channel(user_id, context):
        keyboard = [[InlineKeyboardButton("Join Our Telegram Channel", url=CHANNEL_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚠️ You need to join our Telegram channel to download videos!\n"
            "Please join the channel and send the link again.",
            reply_markup=reply_markup
        )
        return

    # Clean the URL by removing any query parameters like "=="
    clean_url = clean_instagram_url(message_text)

    # Check for Instagram URL
    if "instagram.com" in clean_url:
        try:
            # Process Instagram Post, Reel, or TV (Video Post)
            if "/p/" in clean_url or "/reel/" in clean_url or "/tv/" in clean_url:
                shortcode = clean_url.split("/")[-2]
                logger.info(f"Processing Instagram Post/Reel/TV with shortcode: {shortcode}")
                
                try:
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                except instaloader.exceptions.InstaloaderException as e:
                    logger.error(f"Failed to fetch post metadata: {str(e)}")
                    await update.message.reply_text("❌ Failed to fetch post metadata. The post may be private or deleted.")
                    await notify_admin(f"Failed to fetch post metadata for URL: {clean_url}", user_id, username, context)
                    return

                processing_message = await update.message.reply_text("⏳ Processing your video... Please wait.")
                if post.is_video:
                    await update.message.reply_video(post.video_url)
                else:
                    for img_url in post.get_sidecar_nodes():
                        await update.message.reply_photo(img_url.display_url)

                await processing_message.delete()

            # Process Instagram Profile (Profile Picture)
            elif "/profile" in clean_url:
                username = clean_url.split("/")[-1]
                logger.info(f"Processing Instagram Profile with username: {username}")

                try:
                    profile = instaloader.Profile.from_username(L.context, username)
                    processing_message = await update.message.reply_text("⏳ Fetching profile picture... Please wait.")
                    await update.message.reply_photo(profile.profile_pic_url)
                    await processing_message.delete()
                except instaloader.exceptions.InstaloaderException as e:
                    logger.error(f"Failed to fetch profile: {str(e)}")
                    await update.message.reply_text("❌ Failed to fetch profile picture. The user may be private or banned.")
                    await notify_admin(f"Failed to fetch profile picture for URL: {clean_url}", user_id, username, context)
                    return

            # Process Instagram Story
            elif "/stories/" in clean_url:
                username = clean_url.split("/")[-2]
                logger.info(f"Processing Instagram Story for username: {username}")

                try:
                    profile = instaloader.Profile.from_username(L.context, username)
                    stories = profile.get_stories()
                    for story in stories:
                        for item in story.get_items():
                            await update.message.reply_video(item.video_url)
                except instaloader.exceptions.InstaloaderException as e:
                    logger.error(f"Failed to fetch stories: {str(e)}")
                    await update.message.reply_text("❌ Failed to fetch stories. The user may be private or banned.")
                    await notify_admin(f"Failed to fetch stories for URL: {clean_url}", user_id, username, context)
                    return

            else:
                await update.message.reply_text("⚠️ Invalid Instagram URL. Please send a valid link.")
        except Exception as e:
            logger.error(f"Error processing Instagram URL: {str(e)}")
            await update.message.reply_text("❌ Failed to process the Instagram link. Please try again.")
            await notify_admin(f"Error processing Instagram URL: {clean_url}", user_id, username, context)
    else:
        await update.message.reply_text("⚠️ Please send a valid Instagram link.")
=======
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
>>>>>>> 63d00f4872f960a03d2ed7a9b0e3f706ff48b298

# Main function
def main():
    if not BOT_TOKEN:
<<<<<<< HEAD
        logger.error("❌ Bot token not found. Please check your .env file.")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_request))

    logger.info("✅ Bot is starting...")
=======
        logger.error("Bot token missing!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("contact", contact))
    application.add_handler(CommandHandler("broadcast", broadcast, filters=filters.User(ADMIN_ID)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_request))
    
    logger.info("Bot is running...")
>>>>>>> 63d00f4872f960a03d2ed7a9b0e3f706ff48b298
    application.run_polling()

if __name__ == "__main__":
    main()
