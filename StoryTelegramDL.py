# Required Modules
# Designer and programmer @mrkral
# https://github.com/ParsaPanahi
from pyrogram import Client, types, filters, enums
import asyncio
import os
import requests
import json
import time

# Bot Config Obj
class Config:
    SESSION: str = "BQG0lX0Aq1b5Qc5xhfgllDAKHB8GyOvj5bYEauDIAon_8wc4lH85gJRiat1YFysSLpZ7RjMuRnzALAmo-lJwxw03sWbZMO-6v8cyKhRVoT_H2mKukjxLYOudW7jW-7AK7Ca8B6QnnV9OqdHXjYVoWFjzJShp1ep3zpH9ldlRmUUgsYgpG8mlqPEQZ8VRDOnHbljXx23_yM3AzBArkRI0qAu0KO7vNnmuoZgkj8jUfRTDMEQyHRNNf0bNUshsfwVb1OU0w1fMRnji12R_Sp89GsgpCHe_tKcQfjieLKdxqxLVNByrNZOjAJee0dsR0DoMVAXnbYXLoYBYXWF7EtYhL-QXcYeBrgAAAAG6ViRWAA"
    API_KEY: str = "7884364837:AAF4IQw1YshU2O8qwc1IFWl_gR18EPTdnAg"
    API_HASH: str = "e51a3154d2e0c45e5ed70251d68382de"
    API_ID: int = 15787995
    SUDO: int = 7046488481
    CHANNLS: str = ['Kali_Linux_BOTS']

# Check Bot Directory Exists
if not os.path.exists('./.session'):
    os.mkdir('./.session')

# Check database
if not os.path.exists('./data.json'):
    json.dump({'users': [], 'user_languages': {}} , open('./data.json', 'w'), indent=3)

# Pyrogram Apps
app = Client(
    "./.session/kral",
    bot_token=Config.API_KEY,
    api_hash=Config.API_HASH,
    api_id=Config.API_ID,
    parse_mode=enums.ParseMode.DEFAULT
)

# Helper function to check if user joined channel
async def CHECK_JOIN_MEMBER(user_id: int, channls: list, API_KEY: str):
    states = ['administrator', 'creator', 'member', 'restricted']
    for channl in channls:
        try:
            api = f"https://api.telegram.org/bot{API_KEY}/getChatMember?chat_id=@{channl}&user_id={user_id}"
            respons = requests.get(api).json()
            if respons['result']['status'] not in states:
                return (False, channl)
        except:
            return (False, channl)
    return (True, None)

# Helper function to get story data
async def GET_STORES_DATA(chat_id: str, story_id: int):
    app = Client(':memory:', api_hash=Config.API_HASH, api_id=Config.API_ID, session_string=Config.SESSION, workers=2, no_updates=True)
    try:
        await app.connect()
    except Exception as e:
        return (False, None)
    try:
        data = await app.download_media(await app.get_stories(chat_id=chat_id, story_ids=story_id), in_memory=True)
    except Exception as e:
        return (False, None)
    await app.disconnect()
    return (True, data)

# Language selection handler
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    # Check if the user is already registered
    datas = json.load(open('./data.json'))
    user_id = message.from_user.id
    if user_id in datas['user_languages']:
        language = datas['user_languages'][user_id]
    else:
        # Ask for language selection if it's the first time using the bot
        language = None

    # Send language choice buttons
    language_text = "🎉 Welcome! Please select your preferred language:"
    language_buttons = [
        [types.InlineKeyboardButton("فارسی", callback_data="language_fa")],
        [types.InlineKeyboardButton("English", callback_data="language_en")]
    ]

    if language is None:
        await message.reply(language_text, reply_markup=types.InlineKeyboardMarkup(language_buttons))
    else:
        await send_welcome_message(app, message, language)

# Handle language selection
@app.on_callback_query(filters.regex('^language_'))
async def on_language_selection(app: Client, query: types.CallbackQuery):
    user_id = query.from_user.id
    datas = json.load(open('./data.json'))

    # Update language in the database
    if query.data == 'language_fa':
        datas['user_languages'][user_id] = 'fa'
        json.dump(datas, open('./data.json', 'w'), indent=3)
        language = 'fa'
    elif query.data == 'language_en':
        datas['user_languages'][user_id] = 'en'
        json.dump(datas, open('./data.json', 'w'), indent=3)
        language = 'en'

    await query.answer()
    await send_welcome_message(app, query.message, language)

# Send welcome message based on language
async def send_welcome_message(app: Client, message: types.Message, language: str):
    if language == 'fa':
        await message.reply(
            "🎉 به ربات دانلود استوری تلگرام خوش آمدید! \nلطفاً لینک استوری را ارسال کنید تا آن را برایتان دانلود کنم.",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='💻 Developer', url='https://t.me/mrkral')],
                [types.InlineKeyboardButton(text='📚 Help', callback_data='help')]
            ])
        )
    elif language == 'en':
        await message.reply(
            "🎉 Welcome to the Telegram Story Downloader bot! \nPlease send the story link to download it.",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='💻 Developer', url='https://t.me/mrkral')],
                [types.InlineKeyboardButton(text='📚 Help', callback_data='help')]
            ])
        )

# Handle story URL input
@app.on_message(filters.private & filters.text)
async def ON_URL(app: Client, message: types.Message):
    url = message.text
    user_id = message.from_user.id
    datas = json.load(open('./data.json'))

    if user_id not in datas['user_languages']:
        await message.reply("❌ Language not set. Please restart the bot using /start.")
        return

    language = datas['user_languages'][user_id]

    # Check if the user has joined the channel
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        if language == 'fa':
            await message.reply(f"👋 سلام! برای استفاده از ربات ابتدا در کانال ما عضو شوید: 📣  ❲ @{channl} ❳ و پس از عضویت با ارسال دستور /start عضویت خود را تایید کنید.")
        else:
            await message.reply(f"👋 Hello! To use the bot, please join our channel: 📣  ❲ @{channl} ❳ and then confirm your membership by sending /start.")
        return

    # Validate URL
    if not url.startswith('https://t.me/'):
        if language == 'fa':
            await message.reply("❌ لینک ارسال شده نادرست است. لطفاً یک لینک معتبر ارسال کنید.")
        else:
            await message.reply("❌ The link you sent is invalid. Please send a valid link.")
        return

    try:
        chat_id = url.split('/')[-3]
        story_id = int(url.split('/')[-1])
    except Exception as e:
        if language == 'fa':
            await message.reply("❌ لینک ارسال شده نادرست است.")
        else:
            await message.reply("❌ The link you sent is incorrect.")
        return

    # Download the story and show progress
    message_data = await message.reply("⏳ در حال دانلود استوری... لطفاً صبر کنید." if language == 'fa' else "⏳ Downloading story... Please wait.")

    status, story_data = await GET_STORES_DATA(chat_id, story_id)
    if not status:
        if language == 'fa':
            await message_data.edit("❌ متاسفانه خطایی رخ داده است. لطفاً دوباره تلاش کنید.")
        else:
            await message_data.edit("❌ An error occurred. Please try again.")
        return

    if language == 'fa':
        await message_data.edit("✅ استوری با موفقیت دانلود شد! ارسال می‌شود...")
    else:
        await message_data.edit("✅ Story downloaded successfully! Sending...")

    await app.send_video(
        chat_id=message.chat.id, video=story_data, caption="📹 استوری دانلود شده:" if language == 'fa' else "📹 Downloaded story:"
    )

# Handle the '/help' command
@app.on_callback_query(filters.regex('help'))
async def on_help_query(app: Client, query: types.CallbackQuery):
    user_id = query.from_user.id
    datas = json.load(open('./data.json'))
    language = datas['user_languages'].get(user_id, 'en')

    if language == 'fa':
        await query.message.edit(
            "📘 راهنمای ربات:\n\n"
            "1️⃣ ابتدا در کانال ما عضو شوید.\n"
            "2️⃣ لینک استوری تلگرام را ارسال کنید.\n"
            "3️⃣ ربات استوری را برای شما دانلود خواهد کرد.\n\n"
            "اگر سوالی دارید، با من در تماس باشید. 😊",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='🔙 بازگشت', callback_data='back')]
            ])
        )
    else:
        await query.message.edit(
            "📘 Bot Guide:\n\n"
            "1️⃣ First, join our channel.\n"
            "2️⃣ Send the Telegram story link.\n"
            "3️⃣ The bot will download the story for you.\n\n"
            "If you have any questions, feel free to contact me. 😊",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='🔙 Back', callback_data='back')]
            ])
        )

@app.on_callback_query(filters.regex('back'))
async def on_back_query(app: Client, query: types.CallbackQuery):
    user_id = query.from_user.id
    datas = json.load(open('./data.json'))
    language = datas['user_languages'].get(user_id, 'en')
    await send_welcome_message(app, query.message, language)

# Run the bot
asyncio.run(app.run())
