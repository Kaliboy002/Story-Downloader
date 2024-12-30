import os
import ffmpeg
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Fetch the bot token from environment variables (set in Railway)
BOT_TOKEN = os.getenv("8179647576:AAFQ1xNRSVTlA_fzfJ2m8Hz6g-d5a8TVnUQ")

def start(update: Update, context: CallbackContext):
    """Handles the /start command."""
    update.message.reply_text("Send me a video, and I will compress it for you!")

def compress_video(update: Update, context: CallbackContext):
    """Handles video compression."""
    try:
        # Download the video sent by the user
        video_file = update.message.video.get_file()
        video_path = '/app/input_video.mp4'  # Make sure path is writable in the Docker container
        video_file.download(video_path)

        # Define output file path
        output_path = '/app/output_video.mp4'

        # Compress the video using FFmpeg
        ffmpeg.input(video_path).output(output_path, vcodec='libx264', crf=28).run()

        # Send back the compressed video
        with open(output_path, 'rb') as video:
            update.message.reply_video(video=video)

        # Clean up files
        os.remove(video_path)
        os.remove(output_path)

    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def main():
    """Start the bot."""
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Register command and message handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.video, compress_video))

    # Start polling for new updates
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
