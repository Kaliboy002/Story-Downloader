# Required Modules
from pyrogram import Client, types, filters, enums
import asyncio
import os
import requests
import json

# Bot Config Object
class Config:
    SESSION = "BQG0lX0Aq1b5Qc5xhfgllDAKHB8GyOvj5bYEauDIAon_8wc4lH85gJRiat1YFysSLpZ7RjMuRnzALAmo-lJwxw03sWbZMO-6v8cyKhRVoT_H2mKukjxLYOudW7jW-7AK7Ca8B6QnnV9OqdHXjYVoWFjzJShp1ep3zpH9ldlRmUUgsYgpG8mlqPEQZ8VRDOnHbljXx23_yM3AzBArkRI0qAu0KO7vNnmuoZgkj8jUfRTDMEQyHRNNf0bNUshsfwVb1OU0w1fMRnji12R_Sp89GsgpCHe_tKcQfjieLKdxqxLVNByrNZOjAJee0dsR0DoMVAXnbYXLoYBYXWF7EtYhL-QXcYeBrgAAAAG6ViRWAA"
    API_KEY = "7884364837:AAF4IQw1YshU2O8qwc1IFWl_gR18EPTdnAg"
    API_HASH = "e51a3154d2e0c45e5ed70251d68382de"
    API_ID = 15787995
    SUDO = 7046488481
    CHANNLS = ['Kali_Linux_BOTS']

# Ensure required directories and files exist
if not os.path.exists('./.session'):
    os.mkdir('./.session')

if not os.path.exists('./data.json'):
    json.dump({'users': []}, open('./data.json', 'w'), indent=3)

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
        "join_channel": "To use this bot, you must join our channel first:\n\n📣 @{}\nAfter joining, please send '/start' again.",
        "incorrect_link": "The link you provided is incorrect.",
        "downloading": "Downloading, please wait...",
        "download_successful": "Download completed successfully!",
        "error": "Sorry, there was an issue while downloading.",
    },
    "fa": {
        "welcome": "به ربات دانلود استوری تلگرام خوش آمدید! لینک استوری را برای دانلود ارسال کنید.",
        "join_channel": "برای استفاده از این ربات ابتدا باید به کانال ما بپیوندید:\n\n📣 @{}\nپس از عضویت، دستور '/start' را دوباره ارسال کنید.",
        "incorrect_link": "لینک ارسالی شما نادرست است.",
        "downloading": "در حال دانلود، لطفاً صبر کنید...",
        "download_successful": "دانلود با موفقیت انجام شد!",
        "error": "متاسفانه مشکلی در دانلود پیش آمده است.",
    }
}

# get Story Methods 
async def GET_STORES_DATA(chat_id: str, story_id: int):
    app = Client(':memory:', api_hash=Config.API_HASH, api_id=Config.API_ID, session_string=Config.SESSION, workers=2, no_updates=True)
    try:
        await app.connect()
    except Exception as e:
        print(e)
        return (False, None)
    try:
        data = await app.download_media(await app.get_stories(chat_id=chat_id, story_ids=story_id), in_memory=True)
    except Exception as e:
        print(e)
        return (False, None)
    await app.disconnect()
    return (True, data)

# Check Join Methods
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

# On Start Bot and Language Selection
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(f"سلام برای استفاده از ربات اول در کانال های ما عضو شوید\n\n📣  ❲ @{channl} ❳\n و بعد از عضو شدن با ارسال دستور ( /start ) عضویت خود را تایید کنید")
        return

    # Show language selection buttons
    keyboard = [
        [types.InlineKeyboardButton("فارسی", callback_data="lang_fa")],
        [types.InlineKeyboardButton("English", callback_data="lang_en")]
    ]
    await message.reply("Please choose a language / لطفاً یک زبان انتخاب کنید.", reply_markup=types.InlineKeyboardMarkup(keyboard))

# Handle Language Selection
@app.on_callback_query(filters.regex('^lang_'))
async def language_selection(app: Client, callback_query: types.CallbackQuery):
    language = callback_query.data.split('_')[1]  # "fa" or "en"
    user_id = callback_query.from_user.id

    # Load data
    datas = json.load(open('./data.json'))
    if user_id not in datas['users']:
        datas['users'].append(user_id)
        json.dump(datas, open('./data.json', 'w'), indent=3)

    # Send welcome message in selected language
    await callback_query.answer()
    await callback_query.message.edit(text=LANGUAGE_TEXTS[language]["welcome"])
    
    # Save language choice for later use
    datas['users'][user_id] = language
    json.dump(datas, open('./data.json', 'w'), indent=3)

# On Send Story URL
@app.on_message(filters.private & filters.text)
async def ON_URL(app: Client, message: types.Message):
    # Load user's language preference
    datas = json.load(open('./data.json'))
    language = datas.get(str(message.from_user.id), 'en')

    url = message.text
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(LANGUAGE_TEXTS[language]["join_channel"].format(channl))
        return

    message_data = await message.reply(text=LANGUAGE_TEXTS[language]["downloading"])

    # Check Url
    if not url.startswith('https://t.me/'):
        await message_data.edit(text=LANGUAGE_TEXTS[language]["incorrect_link"])
        return

    try:
        chats_id = url.split('/')[-3]
        story_id = int(url.split('/')[-1])
    except Exception as e:
        await message_data.edit(text=LANGUAGE_TEXTS[language]["incorrect_link"])
        return

    # Get Story and Download
    status, story_data = await GET_STORES_DATA(chats_id, story_id)
    if not status:
        await message_data.edit(text=LANGUAGE_TEXTS[language]["error"])
        return

    await message_data.edit(text=LANGUAGE_TEXTS[language]["download_successful"])
    await app.send_video(chat_id=message.chat.id, video=story_data)

asyncio.run(app.run())
