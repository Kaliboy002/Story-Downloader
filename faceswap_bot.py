from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests

# Your API key for face swap service
API_KEY = 'SG_6dad4e63584a9ea1'

# Function to handle photo messages
async def handle_images(update: Update, context):
    photo_file = await update.message.photo[-1].get_file()
    photo_url = photo_file.file_path
    response = requests.post(
        'https://api.segmind.com/v1/face-swap',
        headers={'Authorization': f'Bearer {API_KEY}'},
        files={'image': requests.get(photo_url).content},
    )
    if response.status_code == 200:
        with open("swapped_face.jpg", "wb") as f:
            f.write(response.content)
        await update.message.reply_photo(photo=open("swapped_face.jpg", 'rb'))
    else:
        await update.message.reply_text("Error with face swap API.")

async def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    application = Application.builder().token('8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ').build()

    # Add a message handler for photos
    application.add_handler(MessageHandler(filters.PHOTO, handle_images))

    # Run the bot without using asyncio.run() directly
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    # Use the existing event loop, do not call asyncio.run() directly.
    loop = asyncio.get_event_loop()
    loop.create_task(main())  # Create the task
    loop.run_forever()  # Keep the event loop running
