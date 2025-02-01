import logging
import instaloader
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
logger = logging.getLogger(__name__)

# Telegram channel link
CHANNEL_LINK = "https://t.me/collagecampus"

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
async def is_user_in_channel(user_id: int, context: CallbackContext) -> bool:
    try:
        chat_member = await context.bot.get_chat_member('@collagecampus', user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
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

# Function to handle contact command
async def contact(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("contact", url="https://t.me/Send_UPI_ID_here_bot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("For CONTACT\ERROR\HELP", reply_markup=reply_markup)

# Function to clean the Instagram URL
def clean_instagram_url(url: str) -> str:
    clean_url = url.split('?')[0]
    clean_url = clean_url.split('#')[0]
    return clean_url

# Function to process Instagram media requests
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

    clean_url = clean_instagram_url(message_text)

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

# Main function
def main():
    if not BOT_TOKEN:
        logger.error("❌ Bot token not found. Please check your .env file.")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("contact", contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_request))

    logger.info("✅ Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
