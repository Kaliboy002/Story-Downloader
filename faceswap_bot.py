import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Replace with your actual API key
MAGIC_HOUR_API_KEY = 'mhk_live_P3mQzxBTERedmDtI7rUFfUAljgGbClAGuWA3fQCyFhFRQEBaCfROKHuGUaFGTcnvMo0NRNGoN4jAvD2h'
TELEGRAM_BOT_TOKEN = '8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Send me a photo to swap faces.')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = file.file_path

    # Download the photo
    response = requests.get(file_path)
    if response.status_code != 200:
        await update.message.reply_text('Failed to download the photo.')
        return

    # Save the photo locally
    with open('user_photo.jpg', 'wb') as f:
        f.write(response.content)

    # Prepare the data for Magic Hour API
    files = {'image': open('user_photo.jpg', 'rb')}
    headers = {'Authorization': f'Bearer {MAGIC_HOUR_API_KEY}'}
    api_url = 'https://api.magichour.ai/v1/face-swap'

    # Make the API request
    api_response = requests.post(api_url, files=files, headers=headers)
    if api_response.status_code != 200:
        await update.message.reply_text('Failed to process the face swap.')
        return

    # Save the swapped image
    with open('swapped_image.jpg', 'wb') as f:
        f.write(api_response.content)

    # Send the swapped image back to the user
    with open('swapped_image.jpg', 'rb') as f:
        await update.message.reply_photo(photo=f)

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()

if __name__ == '__main__':
    main()
