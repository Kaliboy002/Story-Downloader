import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackContext
from io import BytesIO

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram Bot API key
TELEGRAM_API_KEY = "8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ"

# Segmind API configuration for face swapping
FACE_SWAP_API_URL = "https://api.segmind.com/v1/faceswap"
SEGMENTATION_API_KEY = "SG_d8d1ccf061609472"

# Command handler for the start command
async def start(update: Update, context: CallbackContext):
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text("Hello! Send me two photos for face swapping.")

# Function to handle photo messages and perform face swap
async def handle_photo(update: Update, context: CallbackContext):
    """Handle the photo and perform face swap."""
    user = update.message.from_user
    file = await update.message.photo[-1].get_file()
    file_path = f"{user.id}_photo.jpg"
    await file.download(file_path)

    # Logic for face swap (Replace this with the actual face swap logic)
    with open(file_path, "rb") as image_file:
        response = requests.post(
            FACE_SWAP_API_URL,
            headers={"Authorization": f"Bearer {SEGMENTATION_API_KEY}"},
            files={"image": image_file}
        )

    if response.status_code == 200:
        swapped_image_path = "swapped_" + file_path
        
        # Save the swapped image
        with open(swapped_image_path, "wb") as f:
            f.write(response.content)

        # Send the swapped photo back to the user
        with open(swapped_image_path, "rb") as f:
            await update.message.reply_photo(photo=f)
    else:
        await update.message.reply_text("Sorry, an error occurred while processing the face swap.")

# Main function to start the bot and set up the handlers
async def main():
    """Start the bot and set up command and message handlers."""
    # Create the Application and pass the Telegram bot token
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    # Command handler for starting the bot
    start_handler = CommandHandler("start", start)
    
    # Message handler for photos
    photo_handler = MessageHandler(filters.PHOTO, handle_photo)

    # Add the handlers to the application
    application.add_handler(start_handler)
    application.add_handler(photo_handler)

    # Run the bot with polling
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
