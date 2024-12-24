# Required Modules
# Designer and programmer @mrkral
# https://github.com/ParsaPanahi
from pyrogram import Client, types, filters, enums
import asyncio 
import os
import requests
import json

# Bot Config Obj
class Config:
    SESSION : str = "BQG0lX0Aq1b5Qc5xhfgllDAKHB8GyOvj5bYEauDIAon_8wc4lH85gJRiat1YFysSLpZ7RjMuRnzALAmo-lJwxw03sWbZMO-6v8cyKhRVoT_H2mKukjxLYOudW7jW-7AK7Ca8B6QnnV9OqdHXjYVoWFjzJShp1ep3zpH9ldlRmUUgsYgpG8mlqPEQZ8VRDOnHbljXx23_yM3AzBArkRI0qAu0KO7vNnmuoZgkj8jUfRTDMEQyHRNNf0bNUshsfwVb1OU0w1fMRnji12R_Sp89GsgpCHe_tKcQfjieLKdxqxLVNByrNZOjAJee0dsR0DoMVAXnbYXLoYBYXWF7EtYhL-QXcYeBrgAAAAG6ViRWAA"
    API_KEY : str = "7884364837:AAF4IQw1YshU2O8qwc1IFWl_gR18EPTdnAg"
    API_HASH: str = "e51a3154d2e0c45e5ed70251d68382de"
    API_ID  : int = 15787995
    SUDO    : int = 7046488481
    CHANNLS : str = ['Kali_Linux_BOTS']

# Check Bot Directory Exists
if not os.path.exists('./.session'):
    os.mkdir('./.session')

# Check Data Base
if not os.path.exists('./data.json'):
    json.dump({'users': []}, open('./data.json', 'w'), indent=3)

# Pyrogram Apps
app = Client(
    "./.session/kral", 
    bot_token=Config.API_KEY, 
    api_hash=Config.API_HASH, 
    api_id=Config.API_ID, 
    parse_mode=enums.ParseMode.DEFAULT
)

# Get Stories Methods 
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
            response = requests.get(api).json()
            if response['result']['status'] not in states:
                return (False, channl)
        except:
            return (False, channl)
    return (True, None)

# Language Dictionary
LANGUAGE_TEXTS = {
    "en": {
        "welcome": "Welcome to the Telegram Story Downloader bot! Please send me the story link to download.",
        "join_channel": "To use this bot, please join our channels first:\n\n📣 @{}\nAfter joining, resend the /start command to confirm your membership.",
        "invalid_link": "The link you provided is invalid.",
        "downloading": "Downloading, please wait...",
        "download_success": "Download successful!",
        "download_failed": "Sorry, an error occurred while downloading.",
    },
    "fa": {
        "welcome": "به ربات دانلود استوری تلگرام خوش آمدید! لینک استوری را ارسال کنید تا دانلود کنم.",
        "join_channel": "برای استفاده از ربات ابتدا در کانال‌های ما عضو شوید:\n\n📣 @{}\nسپس دستور /start را ارسال کنید.",
        "invalid_link": "لینک ارسال شده نادرست است.",
        "downloading": "در حال دانلود، لطفاً صبر کنید...",
        "download_success": "دانلود با موفقیت انجام شد!",
        "download_failed": "متأسفیم، هنگام دانلود مشکلی پیش آمد.",
    }
}

user_language = {}

# Start Bot with Language Selection
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    if message.from_user.id not in user_language:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("English", "فارسی")
        await message.reply("Please choose your language:\nلطفاً زبان خود را انتخاب کنید:", reply_markup=markup)
        return

    lang = user_language[message.from_user.id]
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(LANGUAGE_TEXTS[lang]["join_channel"].format(channl))
        return

    datas = json.load(open('./data.json'))
    if message.from_user.id not in datas['users']:
        datas['users'].append(message.from_user.id)
        json.dump(datas, open('./data.json', 'w'), indent=3)
    await message.reply(text=LANGUAGE_TEXTS[lang]["welcome"])

@app.on_message(filters.private & filters.text & ~filters.command)
async def ON_LANGUAGE_SELECT(app: Client, message: types.Message):
    if message.text in ["English", "فارسی"]:
        user_language[message.from_user.id] = "en" if message.text == "English" else "fa"
        await message.reply("Language set successfully! Please send the /start command again.")
        return

    lang = user_language.get(message.from_user.id, "fa")
    url = message.text
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(LANGUAGE_TEXTS[lang]["join_channel"].format(channl))
        return

    message_data = await message.reply(LANGUAGE_TEXTS[lang]["downloading"])
    if not url.startswith('https://t.me/'):
        await message_data.edit(LANGUAGE_TEXTS[lang]["invalid_link"])
        return

    try:
        chats_id = url.split('/')[-3]
        story_id = int(url.split('/')[-1])
    except:
        await message_data.edit(LANGUAGE_TEXTS[lang]["invalid_link"])
        return

    status, story_data = await GET_STORES_DATA(chats_id, story_id)
    if not status:
        await message_data.edit(LANGUAGE_TEXTS[lang]["download_failed"])
        return

    await message_data.edit(LANGUAGE_TEXTS[lang]["download_success"])
    await app.send_video(chat_id=message.chat.id, video=story_data)

asyncio.run(app.run())
