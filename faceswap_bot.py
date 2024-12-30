import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace with your Pixo API key
PIX_API_KEY = '2zo8cdjibyg0'
# Replace with your Telegram Bot token
TELEGRAM_BOT_TOKEN = '8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ'

# Pixo API endpoint
PIX_API_URL = 'https://pixoeditor.com/api/image'

# Command handler to start the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Please send an image to edit.")

# Function to handle image editing
async def handle_image(update: Update, context: CallbackContext):
    # Get the image file from the user's message
    if update.message.photo:
        # Download the image
        photo = update.message.photo[-1]
        file = await photo.get_file()
        image_path = 'user_image.jpg'
        await file.download(image_path)

        # Prepare the image for editing
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            data = {
                'apikey': PIX_API_KEY,
                'filter': 'Sepia',  # Example filter; adjust as needed
                # Add other parameters as needed
            }

            # Send the image to Pixo API for editing
            response = requests.post(PIX_API_URL, files=files, data=data)

            if response.status_code == 200:
                # Save the edited image
                with open('edited_image.jpg', 'wb') as edited_image:
                    edited_image.write(response.content)

                # Send the edited image back to the user
                with open('edited_image.jpg', 'rb') as edited_image:
                    await update.message.reply_photo(photo=edited_image)
            else:
                await update.message.reply_text("An error occurred while processing your image.")
    else:
        await update.message.reply_text("Please send an image to edit.")

# Main function to run the bot
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command to start the bot
    application.add_handler(CommandHandler('start', start))

    # Handle images sent to the bot
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    application.run_polling()

if __name__ == '__main__':
    main()
