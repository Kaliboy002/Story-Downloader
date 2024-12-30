import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackContext

# Replace with your Remaker API key
API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTU4NDU2NTYsInByb2R1Y3RfY29kZSI6IjA2NzAwMyIsInRpbWUiOjE3MzU1ODEwNzJ9.YRKzXpAFhgMaeBMUaDfi266TNEGYtkvyik8ERzfNDEM'
TELEGRAM_API_KEY = '8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ'

# Define the Remaker API URLs
FACE_SWAP_URL = 'https://developer.remaker.ai/api/remaker/v1/face-swap/create-job'
FETCH_JOB_URL = 'https://developer.remaker.ai/api/remaker/v1/face-swap/'

# Command handler to start the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Please send two images: one for the target face and one for the face to swap.")

# Function to handle face swap job creation
async def face_swap(update: Update, context: CallbackContext):
    # Get the two images from the user
    if len(update.message.photo) < 2:
        await update.message.reply_text("Please send two images: one for the target face and one for the face to swap.")
        return

    # Fetch the file objects from Telegram
    target_image_file = await update.message.photo[-2].get_file()
    swap_image_file = await update.message.photo[-1].get_file()

    # Define file paths
    target_image_path = "target_image.jpg"
    swap_image_path = "swap_image.jpg"

    # Download the images to the local server
    await target_image_file.download_to_drive(target_image_path)
    await swap_image_file.download_to_drive(swap_image_path)

    # Prepare the API request to create the face swap job
    headers = {
        'accept': 'application/json',
        'Authorization': f'{API_KEY}',
    }
    files = {
        'target_image': open(target_image_path, 'rb'),
        'swap_image': open(swap_image_path, 'rb')
    }

    response = requests.post(FACE_SWAP_URL, headers=headers, files=files)
    if response.status_code == 200:
        job_id = response.json().get("result", {}).get("job_id")
        await update.message.reply_text(f"Face swap job created successfully! Job ID: {job_id}. Please wait while we process the images.")
        
        # Now fetch the result of the job
        fetch_response = await fetch_result(job_id)
        if fetch_response:
            # Send the output image URL to the user
            output_image_url = fetch_response.get("result", {}).get("output_image_url", [None])[0]
            if output_image_url:
                await update.message.reply_text(f"Here is your face-swapped image: {output_image_url}")
            else:
                await update.message.reply_text("Sorry, there was an error generating the face swap.")
        else:
            await update.message.reply_text("Error occurred while fetching the result.")
    else:
        await update.message.reply_text("Error creating face swap job.")

# Function to fetch job result
async def fetch_result(job_id):
    headers = {
        'accept': 'application/json',
        'Authorization': f'{API_KEY}',
    }
    response = requests.get(f"{FETCH_JOB_URL}{job_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Main function to run the bot
def main():
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    # Command to start the bot
    application.add_handler(CommandHandler('start', start))

    # Handle images sent to the bot
    application.add_handler(MessageHandler(filters.PHOTO, face_swap))

    application.run_polling()

if __name__ == '__main__':
    main()
