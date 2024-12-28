import logging
import cv2
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from io import BytesIO

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle /start command
async def start(update: Update, context):
    await update.message.reply_text('Welcome! Send me two pictures, and I will swap their faces.')

# Function to swap faces using OpenCV
def swap_faces(image1, image2):
    # Convert images to gray scale
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Use OpenCV's face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Detect faces in both images
    faces1 = face_cascade.detectMultiScale(gray1, 1.1, 4)
    faces2 = face_cascade.detectMultiScale(gray2, 1.1, 4)

    if len(faces1) == 0 or len(faces2) == 0:
        raise Exception("No faces detected in one or both images!")

    # Extract faces
    x1, y1, w1, h1 = faces1[0]
    face1 = image1[y1:y1+h1, x1:x1+w1]
    x2, y2, w2, h2 = faces2[0]
    face2 = image2[y2:y2+h2, x2:x2+w2]

    # Resize faces to swap
    face1_resized = cv2.resize(face1, (w2, h2))
    face2_resized = cv2.resize(face2, (w1, h1))

    # Swap faces
    image1[y1:y1+h1, x1:x1+w1] = face2_resized
    image2[y2:y2+h2, x2:x2+w2] = face1_resized

    return image1, image2

# Function to handle images
async def handle_images(update: Update, context):
    photos = update.message.photo
    if len(photos) < 2:
        await update.message.reply_text('Please send at least two photos to swap faces.')
        return

    # Download the first two images
    photo_1 = await photos[-2].get_file()
    photo_2 = await photos[-1].get_file()

    # Fetch the image data
    image_1_data = BytesIO(await photo_1.download_as_bytearray())
    image_2_data = BytesIO(await photo_2.download_as_bytearray())

    # Convert byte data to OpenCV images
    image_1 = cv2.imdecode(np.frombuffer(image_1_data.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    image_2 = cv2.imdecode(np.frombuffer(image_2_data.getvalue(), np.uint8), cv2.IMREAD_COLOR)

    try:
        swapped_image_1, swapped_image_2 = swap_faces(image_1, image_2)

        # Convert images back to byte format
        _, buffer_1 = cv2.imencode('.jpg', swapped_image_1)
        _, buffer_2 = cv2.imencode('.jpg', swapped_image_2)

        # Send the swapped images to the user
        await update.message.reply_photo(buffer_1.tobytes())
        await update.message.reply_photo(buffer_2.tobytes())

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Main function to run the bot
async def main():
    TELEGRAM_TOKEN = '8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ'

    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Command handler for /start
    application.add_handler(CommandHandler("start", start))

    # Message handler for photos
    application.add_handler(MessageHandler(filters.PHOTO, handle_images))

    # Start polling for updates
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
