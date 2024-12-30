import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode  # Updated import

# Your Remove.bg API key
REMOVE_BG_API_KEY = "DjJxJpLtmBcvaU2FoR2PfcxN"

# Function to remove background using Remove.bg API
def remove_bg(image_path):
    url = "https://api.remove.bg/v1.0/removebg"
    headers = {'X-Api-Key': REMOVE_BG_API_KEY}

    with open(image_path, 'rb') as image_file:
        files = {'image_file': image_file}
        data = {'size': 'auto'}  # Optional, specify the size of the image
        response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        output_path = f"no_bg_{os.path.basename(image_path)}"
        with open(output_path, 'wb') as out_file:
            out_file.write(response.content)
        return output_path
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Function to handle received photos
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the photo file from the user
    photo_file = await update.message.photo[-1].get_file()
    photo_path = "user_image.jpg"
    await photo_file.download_to_drive(photo_path)

    # Remove background from the photo
    enhanced_photo_path = remove_bg(photo_path)

    if enhanced_photo_path:
        # Send the enhanced photo back to the user
        await context.bot.send_photo(chat_id=update.message.chat_id, photo=open(enhanced_photo_path, 'rb'))
    else:
        await update.message.reply_text("Sorry, I couldn't remove the background. Please try again later.")

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Send me a photo, and I'll remove its background for you!\n"
        "The background removal is powered by Remove.bg API."
    )

# Main function to run the bot
def main():
    # Replace with your Telegram bot token
    TELEGRAM_BOT_TOKEN = "8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ"

    # Create the Application instance
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
