import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import instaloader

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHANNEL_ID = '@yourchannelid'

async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    # Check if user is a member of the channel
    member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
    if member.status in ('creator', 'administrator', 'member'):
        await update.message.reply_text('Send the Instagram video URL.')
    else:
        await update.message.reply_text('You must join the channel first.')

async def download_video(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    if 'instagram.com' in url:
        loader = instaloader.Instaloader()
        try:
            loader.download_profile(url)
            await update.message.reply_text('Video downloaded.')
        except Exception as e:
            await update.message.reply_text('Failed to download video.')

async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("download_video", download_video))

    await application.start()
    await application.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
