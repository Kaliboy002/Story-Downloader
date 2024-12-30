from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import PhotoFilter  # Correct import for filters

SLAZZER_API_KEY = '41a14566beef4577b14bba3ac475227c'  # Replace with your Slazzer API key
TELEGRAM_TOKEN = '8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ'  # Replace with your Telegram bot token

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Send me an image to remove the background.')

def remove_background(image_path: str) -> str:
    url = "https://api.slazzer.com/v2/remove-background"
    headers = {
        "Authorization": f"Bearer {SLAZZER_API_KEY}",
    }
    with open(image_path, 'rb') as image_file:
        files = {"image": image_file}
        response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        # Save the resulting image
        output_path = 'output.png'
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return output_path
    return None

def handle_photo(update: Update, context: CallbackContext):
    file = update.message.photo[-1].get_file()
    file.download('received_image.jpg')
    
    # Call Slazzer API to remove background
    output_image_path = remove_background('received_image.jpg')

    if output_image_path:
        update.message.reply_photo(photo=open(output_image_path, 'rb'))
    else:
        update.message.reply_text('Sorry, I couldn\'t process the image.')

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(PhotoFilter(), handle_photo))

    application.run_polling()

if __name__ == '__main__':
    main()
