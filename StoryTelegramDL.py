import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Telegram Bot Token and Segmind API Key
TELEGRAM_BOT_TOKEN = '8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ'
SEGMIND_API_KEY = 'SG_6dad4e63584a9ea1'
SEGMIND_API_URL = 'https://api.segmind.com/v2/faceswap'

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the Face Swap Bot! Send two photos to swap faces.")

def handle_images(update: Update, context: CallbackContext):
    photos = update.message.photo
    if len(photos) < 2:
        update.message.reply_text("Please send exactly two photos.")
        return

    # Download the photos
    photo1_path = context.bot.get_file(photos[0].file_id).download('photo1.jpg')
    photo2_path = context.bot.get_file(photos[1].file_id).download('photo2.jpg')

    # Call the Segmind API
    try:
        response = requests.post(
            SEGMIND_API_URL,
            headers={'Authorization': f'Bearer {SEGMIND_API_KEY}'},
            files={
                'source1': open(photo1_path, 'rb'),
                'source2': open(photo2_path, 'rb')
            }
        )
        result = response.json()

        # Check for errors
        if "output_url" in result:
            # Download the output image
            output_image = requests.get(result['output_url']).content
            with open('output.jpg', 'wb') as f:
                f.write(output_image)

            # Send back the swapped image
            with open('output.jpg', 'rb') as f:
                update.message.reply_photo(photo=f)
        else:
            update.message.reply_text(f"API Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")
    finally:
        # Cleanup
        os.remove(photo1_path)
        os.remove(photo2_path)
        if os.path.exists('output.jpg'):
            os.remove('output.jpg')

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_images))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
