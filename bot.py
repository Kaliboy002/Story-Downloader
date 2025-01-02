from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import requests
import os

# Your Telegram Bot Token and ApyHub Token
TELEGRAM_BOT_TOKEN = "8179647576:AAGPGp13Pp-qF32KqDivMTEn-4LHOLcpRpI"
APYHUB_TOKEN = "APY0Kdke1u6OKpJTUTb4DTHPl8Kx8xC70dt1C3u4bATd9b2WjeQO2rjNnhAQpVLe9xafMbF82"

async def start(update: Update, context):
    await update.message.reply_text(
        "Welcome to the Photo Filter Bot! Send me an image, and I'll apply a filter for you. Use /filterlist to see available filters."
    )

async def filter_list(update: Update, context):
    filters = [
        "rotate_45", "rotate_90", "rotate_135", "rotate_180", "brightness_increase",
        "brightness_decrease", "gaussian_blur", "flip_horizontal", "flip_vertical", 
        "gamma_0.5"
    ]
    await update.message.reply_text(
        "Available Filters:\n" + "\n".join(filters) + "\n\nUse /filter <filter_name> to select a filter."
    )

async def set_filter(update: Update, context):
    if len(context.args) != 1:
        await update.message.reply_text("Please specify a valid filter. Example: /filter gaussian_blur")
        return
    
    selected_filter = context.args[0]
    context.chat_data["filter"] = selected_filter
    await update.message.reply_text(f"Filter set to: {selected_filter}. Now send me an image!")

async def apply_filter(update: Update, context):
    if "filter" not in context.chat_data:
        await update.message.reply_text("Please set a filter first using /filter <filter_name>.")
        return
    
    selected_filter = context.chat_data["filter"]
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    photo_path = await photo_file.download()

    await update.message.reply_text("Processing your photo...")

    # Call ApyHub API
    api_url = f"https://api.apyhub.com/processor/image/filter/file?filter={selected_filter}&preserve_format=true"
    headers = {"apy-token": APYHUB_TOKEN}
    files = {"image": open(photo_path, "rb")}

    response = requests.post(api_url, headers=headers, files=files)
    if response.status_code == 200:
        output_file = "output.jpg"
        with open(output_file, "wb") as f:
            f.write(response.content)

        # Send processed photo back to user
        await update.message.reply_photo(photo=open(output_file, "rb"))

        # Clean up
        os.remove(photo_path)
        os.remove(output_file)
    else:
        await update.message.reply_text("Failed to process the image. Try again later.")

# Set up bot
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("filterlist", filter_list))
app.add_handler(CommandHandler("filter", set_filter))
app.add_handler(MessageHandler(filters.PHOTO, apply_filter))
app.run_polling()
