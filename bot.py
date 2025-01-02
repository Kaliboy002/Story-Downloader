import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    CallbackQueryHandler
)

# Replace these with your tokens
TELEGRAM_BOT_TOKEN = "8179647576:AAGPGp13Pp-qF32KqDivMTEn-4LHOLcpRpI"
APYHUB_TOKEN = "APY0QoajCYZOytNXkLncO1v5XIBoSDYqyLWkhwtZZJF58Tyd42nf8p5KmwL30pMAbHs"

# Fetch app reviews from ApyHub API
def fetch_app_reviews(platform, app_id, country=None, language=None, sort_by="mostrecent"):
    url = "https://api.apyhub.com/recensia/analyse_reviews"
    headers = {
        "Content-Type": "application/json",
        "apy-token": APYHUB_TOKEN
    }
    data = {
        "platform": platform,
        "app_id": app_id,
        "sort_by": sort_by,
    }
    if country:
        data["country"] = country
    if language:
        data["language"] = language

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

# Command to fetch reviews
async def get_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args  # Get arguments from the command
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: /reviews <platform> <app_id> [country/language] [sort_by]\n"
            "Example: /reviews app_store 368677368 us mostrecent\n\n"
            "Supported platforms: app_store, google_play"
        )
        return

    platform = args[0].lower()
    app_id = args[1]
    country_or_language = args[2] if len(args) > 2 else None
    sort_by = args[3] if len(args) > 3 else "mostrecent"

    # Validate platform input
    if platform not in ["app_store", "google_play"]:
        await update.message.reply_text("Invalid platform. Use 'app_store' or 'google_play'.")
        return

    # Fetch reviews
    reviews = fetch_app_reviews(platform, app_id, country=country_or_language, sort_by=sort_by)

    if "error" in reviews:
        await update.message.reply_text(f"Error fetching reviews: {reviews['error']}")
    else:
        message = reviews["message"]
        summary = (
            f"**App Reviews Summary**\n"
            f"Reviews Analyzed: {message['review_count']}\n"
            f"Rating: {message['rating']}/5\n\n"
            f"**Summary**:\n{message['content'][:4000]}..."  # Telegram messages have a 4096-character limit
        )
        keyboard = [
            [
                InlineKeyboardButton("More Details", callback_data="details"),
                InlineKeyboardButton("Set Filters", callback_data="filters"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(summary, reply_markup=reply_markup, parse_mode="Markdown")

# Callback handler for inline buttons
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "details":
        await query.edit_message_text("Detailed information coming soon!")
    elif query.data == "filters":
        await query.edit_message_text("Filter setting feature will be added soon.")

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 **App Review Bot Help**\n\n"
        "This bot allows you to fetch app reviews from the Apple App Store or Google Play Store.\n\n"
        "**Commands:**\n"
        "/reviews - Fetch app reviews\n"
        "Usage: /reviews <platform> <app_id> [country/language] [sort_by]\n\n"
        "**Examples:**\n"
        "/reviews app_store 368677368 us mostrecent\n"
        "/reviews google_play com.example.app en newest\n\n"
        "Supported platforms: app_store, google_play"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Main function to run the bot
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("reviews", get_reviews))
    app.add_handler(CommandHandler("help", help_command))

    # Callback query handler for inline buttons
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    await app.run_polling()

# Run the bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
