import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext

TELEGRAM_BOT_TOKEN = '8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ'
SEGMIND_API_KEY = 'SG_6dad4e63584a9ea1'
SEGMIND_API_URL = 'https://api.segmind.com/v2/faceswap'


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the Face Swap Bot! Send two photos to swap faces.")


async def handle_images(update: Update, context: CallbackContext):
    photos = update.message.photo
    if len(photos) < 2:
        await update.message.reply_text("Please send exactly two photos.")
        return

    # Download the photos
    photo1_path = await context.bot.get_file(photos[0].file_id).download_to_drive('photo1.jpg')
    photo2_path = await context.bot.get_file(photos[1].file_id).download_to_drive('photo2.jpg')

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
                await update.message.reply_photo(photo=f)
        else:
            await update.message.reply_text(f"API Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")
    finally:
        # Cleanup
        os.remove('photo1.jpg')
        os.remove('photo2.jpg')
        if os.path.exists('output.jpg'):
            os.remove('output.jpg')


async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(telegram.filters.PHOTO, handle_images))

    await application.run_polling()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
