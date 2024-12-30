import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests

# Replace with your Telegram Bot API token from BotFather
TELEGRAM_API_KEY = '8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ'

# Replace with your RapidAPI key
RAPIDAPI_KEY = 'f80d19213msh481 ef01 a986fc9fp19765djsn5d3ac8b3360f'

# Function to download video from Social Media Video Downloader API
def download_video(url: str):
    api_url = f"https://social-media-video-downloader.p.rapidapi.com/smvd/get/youtube?url={url}"
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': 'social-media-video-downloader.p.rapidapi.com'
    }
    
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'video_url' in data:
            return data['video_url']
        else:
            return "Sorry, I couldn't find a video at that URL."
    else:
        return "Error: Unable to fetch video. Please try again later."

# Command handler to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Welcome! Send me a YouTube video link, and I'll give you the download link.")

# Function to handle incoming messages and download videos
async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if "youtube.com" in text or "youtu.be" in text:
        await update.message.reply_text("Downloading video... Please wait a moment.")
        video_url = download_video(text)
        await update.message.reply_text(f"Here is your video download link: {video_url}")
    else:
        await update.message.reply_text("Please send a valid YouTube link.")

# Error handler for the bot
def error(update: Update, context: CallbackContext):
    logger.warning(f"Update {update} caused error {context.error}")

# Main function to start the bot
def main():
    # Create the application
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    # Add command handler and message handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
