import time
import json
from pathlib import Path
from urllib.request import urlretrieve
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Deep-Image.ai API key
API_KEY = "21dcba40-c6c7-11ef-a77c-bf148b3dcb18"

# Define headers for the API requests
HEADERS = {
    'x-api-key': API_KEY,
}

# Define the enhancements and width for image processing
ENHANCEMENTS = {
    "enhancements": ["denoise", "deblur", "light"],
    "width": 2000  # Desired width for upscaling
}

# Function to enhance an image using Deep-Image.ai
def enhance_image(image_path):
    try:
        with open(image_path, 'rb') as f:
            # Prepare the API request
            response = requests.post(
                'https://deep-image.ai/rest_api/process_result',
                headers=HEADERS,
                files={'image': f},
                data={"parameters": json.dumps(ENHANCEMENTS)}
            )

            # Check if the request was successful
            if response.status_code == 200:
                response_json = response.json()
                # Wait for processing to complete
                while response_json.get('status') == 'in_progress':
                    time.sleep(1)
                    response = requests.get(
                        f'https://deep-image.ai/rest_api/result/{response_json["job"]}',
                        headers=HEADERS
                    )
                    response_json = response.json()

                # If the processing is complete, download the enhanced image
                if response_json.get('status') == 'complete':
                    result_url = response_json['result_url']
                    output_path = Path(result_url).name
                    urlretrieve(result_url, output_path)
                    return output_path
                else:
                    print(f"Error: {response_json}")
            else:
                print(f"API Request Failed: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error enhancing image: {e}")
    return None

# Function to handle received photos
def handle_photo(update: Update, context):
    # Get the photo file from the user
    photo_file = update.message.photo[-1].get_file()
    photo_path = "user_image.jpg"
    photo_file.download(photo_path)

    # Enhance the photo
    enhanced_photo_path = enhance_image(photo_path)

    if enhanced_photo_path:
        # Send the enhanced photo back to the user
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open(enhanced_photo_path, 'rb'))
    else:
        update.message.reply_text("Sorry, I couldn't enhance your photo. Please try again later.")

# Function to handle the /start command
def start(update: Update, context):
    update.message.reply_text("Welcome! Send me a photo, and I'll enhance it for you!")

# Main function to run the bot
def main():
    # Replace with your Telegram bot token
    TELEGRAM_BOT_TOKEN = "8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ"

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
