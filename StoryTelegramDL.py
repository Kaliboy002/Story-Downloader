# Required Modules
from pyrogram import Client, types, filters, enums
import asyncio
import os
import requests
import json

# Bot Config Object
class Config:
    SESSION = "BQG0lX0Aq1b5Qc5xhfgllDAKHB8GyOvj5bYEauDIAon_8wc4lH85gJRiat1YFysSLpZ7RjMuRnzALAmo-lJwxw03sWbZMO-6v8cyKhRVoT_H2mKukjxLYOudW7jW-7AK7Ca8B6QnnV9OqdHXjYVoWFjzJShp1ep3zpH9ldlRmUUgsYgpG8mlqPEQZ8VRDOnHbljXx23_yM3AzBArkRI0qAu0KO7vNnmuoZgkj8jUfRTDMEQyHRNNf0bNUshsfwVb1OU0w1fMRnji12R_Sp89GsgpCHe_tKcQfjieLKdxqxLVNByrNZOjAJee0dsR0DoMVAXnbYXLoYBYXWF7EtYhL-QXcYeBrgAAAAG6ViRWAA"  # Pyrogram Sessions
    API_KEY = "7884364837:AAF4IQw1YshU2O8qwc1IFWl_gR18EPTdnAg"  # Bot API Key
    API_HASH = "e51a3154d2e0c45e5ed70251d68382de"  # API Hash
    API_ID = 15787995  # API ID
    SUDO = 7046488481  # Sudo ID
    CHANNLS = ['Kali_Linux_BOTS']  # Channel List

# Ensure required directories and files exist
if not os.path.exists('./.session'):
    os.mkdir('./.session')

if not os.path.exists('./data.json'):
    json.dump({'users': {}, 'languages': {}}, open('./data.json', 'w'), indent=3)

# Initialize Pyrogram Client
app = Client(
    "./.session/kral",
    bot_token=Config.API_KEY,
    api_hash=Config.API_HASH,
    api_id=Config.API_ID,
    parse_mode=enums.ParseMode.DEFAULT
)

# Language Texts
LANGUAGE_TEXTS = {
    "en": {
        "welcome": "Welcome to the Telegram Story Downloader bot! Send me the story link to download.",
        "join_channel": "To use this bot, you must join our channel first:\n\n📣 @{}\nClick the button below to verify your membership.",
        "verify_join": "Check Join",
        "not_joined": "You are not a member of our channel. Please join and try again.",
        "downloading": "Downloading, please wait...",
        "download_successful": "Download completed successfully!",
        "error": "Sorry, there was an issue while downloading.",
    },
    "fa": {
        "welcome": "به ربات دانلود استوری تلگرام خوش آمدید! لینک استوری را برای دانلود ارسال کنید.",
        "join_channel": "برای استفاده از این ربات ابتدا باید به کانال ما بپیوندید:\n\n📣 @{}\nدکمه زیر را برای تایید عضویت کلیک کنید.",
        "verify_join": "بررسی عضویت",
        "not_joined": "شما عضو کانال ما نیستید. لطفاً عضو شوید و دوباره امتحان کنید.",
        "downloading": "در حال دانلود، لطفاً صبر کنید...",
        "download_successful": "دانلود با موفقیت انجام شد!",
        "error": "متاسفانه مشکلی در دانلود پیش آمده است.",
    }
}

# Check Join Method
async def CHECK_JOIN_MEMBER(user_id: int, channels: list, api_key: str):
    states = ['administrator', 'creator', 'member', 'restricted']
    for channel in channels:
        try:
            api = f"https://api.telegram.org/bot{api_key}/getChatMember?chat_id=@{channel}&user_id={user_id}"
            response = requests.get(api).json()
            if response.get('result', {}).get('status') not in states:
                return False, channel
        except:
            return False, channel
    return True, None

# Story Downloader Method
async def GET_STORES_DATA(chat_id: str, story_id: int):
    client = Client(":memory:", api_hash=Config.API_HASH, api_id=Config.API_ID, session_string=Config.SESSION, workers=2, no_updates=True)
    try:
        await client.connect()
        story = await client.get_stories(chat_id=chat_id, story_ids=[story_id])
        if not story:
            return False, None
        data = await client.download_media(story[0], in_memory=True)
    except Exception as e:
        print(e)
        return False, None
    finally:
        await client.disconnect()
    return True, data

# On Start and Language Selection
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    keyboard = [
        [types.InlineKeyboardButton("فارسی", callback_data="lang_fa")],
        [types.InlineKeyboardButton("English", callback_data="lang_en")]
    ]
    await message.reply("Please choose a language / لطفاً یک زبان انتخاب کنید.", reply_markup=types.InlineKeyboardMarkup(keyboard))

# Handle Language Selection
@app.on_callback_query(filters.regex('^lang_'))
async def language_selection(app: Client, callback_query: types.CallbackQuery):
    language = callback_query.data.split('_')[1]
    user_id = str(callback_query.from_user.id)

    # Save user language
    data = json.load(open('./data.json'))
    data['languages'][user_id] = language
    json.dump(data, open('./data.json', 'w'), indent=3)

    # Send join message with button
    join_message = LANGUAGE_TEXTS[language]["join_channel"].format(Config.CHANNLS[0])
    button = types.InlineKeyboardButton(LANGUAGE_TEXTS[language]["verify_join"], callback_data="check_join")
    await callback_query.message.edit(text=join_message, reply_markup=types.InlineKeyboardMarkup([[button]]))

# Verify Channel Join
@app.on_callback_query(filters.regex('^check_join$'))
async def check_join(app: Client, callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = json.load(open('./data.json'))
    language = data['languages'].get(str(user_id), 'en')

    # Check membership
    status, channel = await CHECK_JOIN_MEMBER(user_id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await callback_query.answer(LANGUAGE_TEXTS[language]["not_joined"], show_alert=True)
        return

    # Send welcome message
    await callback_query.message.edit(text=LANGUAGE_TEXTS[language]["welcome"])

# On Send Story URL
@app.on_message(filters.private & filters.text)
async def ON_URL(app: Client, message: types.Message):
    user_id = str(message.from_user.id)
    data = json.load(open('./data.json'))
    language = data['languages'].get(user_id, 'en')

    # Check membership
    status, channel = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        join_message = LANGUAGE_TEXTS[language]["join_channel"].format(channel)
        button = types.InlineKeyboardButton(LANGUAGE_TEXTS[language]["verify_join"], callback_data="check_join")
        await message.reply(join_message, reply_markup=types.InlineKeyboardMarkup([[button]]))
        return

    downloading_message = await message.reply(LANGUAGE_TEXTS[language]["downloading"])

    # Process URL
    url = message.text
    if not url.startswith('https://t.me/'):
        await downloading_message.edit(LANGUAGE_TEXTS[language]["error"])
        return

    try:
        chat_id = url.split('/')[-3]
        story_id = int(url.split('/')[-1])
    except:
        await downloading_message.edit(LANGUAGE_TEXTS[language]["error"])
        return

    # Download Story
    status, story_data = await GET_STORES_DATA(chat_id, story_id)
    if not status:
        await downloading_message.edit(LANGUAGE_TEXTS[language]["error"])
        return

    await downloading_message.edit(LANGUAGE_TEXTS[language]["download_successful"])
    await app.send_video(chat_id=message.chat.id, video=story_data)

asyncio.run(app.run())
