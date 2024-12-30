from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests

# Your API keys and URLs
TELEGRAM_API_KEY = "8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ"
FACE_SWAP_API_URL = "https://api.segmind.com/v1/face_swap"
FACE_SWAP_API_KEY = "SG_d8d1ccf061609472"

# Command handler for starting the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Send me two photos to swap faces.")

# Function to handle photo messages and perform face swap
async def handle_photo(update: Update, context: CallbackContext):
    if len(update.message.photo) < 2:
        await update.message.reply_text("Please send two photos for face swapping.")
        return

    photo1 = update.message.photo[-1].file_id  # Get the highest resolution photo
    photo2 = update.message.photo[-2].file_id  # Get the second photo

    # Download the photos
    file1 = await update.message.bot.get_file(photo1)
    file2 = await update.message.bot.get_file(photo2)

    file1_path = "/tmp/photo1.jpg"
    file2_path = "/tmp/photo2.jpg"

    await file1.download_to_drive(file1_path)
    await file2.download_to_drive(file2_path)

    # Perform face swap using Segmind API
    with open(file1_path, "rb") as f1, open(file2_path, "rb") as f2:
        response = requests.post(
            FACE_SWAP_API_URL,
            headers={"Authorization": f"Bearer {FACE_SWAP_API_KEY}"},
            files={"image1": f1, "image2": f2},
        )

    # If the API returns a successful response
    if response.status_code == 200:
        swapped_image_url = response.json().get("swapped_image_url")
        await update.message.reply_photo(photo=swapped_image_url)
    else:
        await update.message.reply_text("Sorry, something went wrong with the face swap.")

# Main function to set up the bot
async def main():
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    # Registering command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start the bot
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
