import os
import requests
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext

# Bot token and Segmind API configuration
TELEGRAM_BOT_TOKEN = '8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ'
SEGMIND_API_KEY = 'SG_6dad4e63584a9ea1'
SEGMIND_API_URL = 'https://api.segmind.com/v2/faceswap'


async def start(update: Update, context: CallbackContext):
    """Sends a welcome message when the bot is started."""
    await update.message.reply_text(
        "Welcome to the Face Swap Bot! Send me two photos in the same message to swap faces."
    )


async def handle_images(update: Update, context: CallbackContext):
    """Handles the face swapping process when the user sends two photos."""
    photos = update.message.photo
    if len(photos) < 2:
        await update.message.reply_text(
            "Please send exactly two photos in one message to perform the face swap."
        )
        return

    try:
        # Download the photos
        photo1_path = await context.bot.get_file(photos[0].file_id).download_to_drive('photo1.jpg')
        photo2_path = await context.bot.get_file(photos[1].file_id).download_to_drive('photo2.jpg')

        # Call the Segmind API for face swapping
        response = requests.post(
            SEGMIND_API_URL,
            headers={'Authorization': f'Bearer {SEGMIND_API_KEY}'},
            files={
                'source1': open(photo1_path, 'rb'),
                'source2': open(photo2_path, 'rb'),
            }
        )

        # Handle API response
        if response.status_code == 200:
            result = response.json()
            if "output_url" in result:
                # Download the swapped face image
                output_image = requests.get(result["output_url"]).content
                with open('output.jpg', 'wb') as f:
                    f.write(output_image)

                # Send the swapped image back to the user
                with open('output.jpg', 'rb') as f:
                    await update.message.reply_photo(photo=f)
            else:
                error_message = result.get("error", "Unknown error occurred.")
                await update.message.reply_text(f"API Error: {error_message}")
        else:
            await update.message.reply_text(
                f"Face swap failed! API returned status code {response.status_code}."
            )
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")
    finally:
        # Clean up temporary files
        if os.path.exists('photo1.jpg'):
            os.remove('photo1.jpg')
        if os.path.exists('photo2.jpg'):
            os.remove('photo2.jpg')
        if os.path.exists('output.jpg'):
            os.remove('output.jpg')


async def main():
    """Main function to start the bot."""
    # Create the application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(telegram.filters.PHOTO, handle_images))

    # Start the bot
    await application.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
