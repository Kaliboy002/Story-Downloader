from pyrogram import Client, types, filters, enums
import asyncio
import os
import requests
import json

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
    json.dump({'users': {}}, open('./data.json', 'w'), indent=3)

# Load translations
LANGUAGES = {
    "en": {
        "welcome": "Welcome to the Telegram story downloader bot. Send me a story link to download it for you within seconds.",
        "join_prompt": "Please join our channels to use this bot:\n\n📣 ❲ @{} ❳\nAfter joining, verify your membership by sending the command (/start).",
        "invalid_link": "The link you sent is invalid.",
        "downloading": "Downloading, please wait...",
        "download_complete": "Download completed successfully.",
        "download_error": "Sorry, there was an issue while downloading.",
        "programmer": "Programmer",
        "language_prompt": "Please select your preferred language:",
        "english": "English",
        "persian": "فارسی",
    },
    "fa": {
        "welcome": "به ربات دانلود استوری تلگرام خوش آمدید. لینک استوری را برای من ارسال کنید تا در عرض چند ثانیه دانلود کنم برات.",
        "join_prompt": "سلام برای استفاده از ربات اول در کانال های ما عضو شوید\n\n📣 ❲ @{} ❳\n و بعد از عضو شدن با ارسال دستور ( /start ) عضویت خود را تایید کنید.",
        "invalid_link": "لینک ارسال شده نادرست هست.",
        "downloading": "درحال ارسال لطفاً صبر کنید.",
        "download_complete": "دانلود با موفقیت انجام شد.",
        "download_error": "متأسفیم، هنگام دانلود مشکلی پیش آمد.",
        "programmer": "برنامه نویس",
        "language_prompt": "لطفاً زبان مورد نظر خود را انتخاب کنید:",
        "english": "English",
        "persian": "فارسی",
    },
}

# Pyrogram Apps
app = Client(
    "./.session/kral",
    bot_token=Config.API_KEY,
    api_hash=Config.API_HASH,
    api_id=Config.API_ID,
    parse_mode=enums.ParseMode.DEFAULT,
)

def get_user_language(user_id):
    datas = json.load(open('./data.json'))
    return datas['users'].get(str(user_id), {}).get('language', 'fa')

def set_user_language(user_id, language):
    datas = json.load(open('./data.json'))
    if str(user_id) not in datas['users']:
        datas['users'][str(user_id)] = {}
    datas['users'][str(user_id)]['language'] = language
    json.dump(datas, open('./data.json', 'w'), indent=3)

async def CHECK_JOIN_MEMBER(user_id, channls, API_KEY):
    states = ['administrator', 'creator', 'member', 'restricted']
    for channl in channls:
        try:
            api = f"https://api.telegram.org/bot{API_KEY}/getChatMember?chat_id=@{channl}&user_id={user_id}"
            response = requests.get(api).json()
            if response['result']['status'] not in states:
                return (False, channl)
        except Exception:
            return (False, channl)
    return (True, None)

@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    user_id = message.from_user.id
    status, channl = await CHECK_JOIN_MEMBER(user_id, Config.CHANNLS, Config.API_KEY)
    lang = get_user_language(user_id)
    t = LANGUAGES[lang]

    if not status:
        await message.reply(t['join_prompt'].format(channl))
        return

    # Language selection buttons
    await message.reply(
        text=t["language_prompt"],
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(text=t["english"], callback_data="lang_en")],
            [types.InlineKeyboardButton(text=t["persian"], callback_data="lang_fa")],
        ])
    )

@app.on_callback_query(filters.regex("^lang_(en|fa)$"))
async def CHANGE_LANGUAGE(app: Client, callback_query: types.CallbackQuery):
    lang_code = callback_query.data.split("_")[1]
    set_user_language(callback_query.from_user.id, lang_code)
    t = LANGUAGES[lang_code]

    await callback_query.message.edit_text(
        text=t["welcome"],
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(text=t["programmer"], url='t.me/mrkral')],
        ])
    )

@app.on_message(filters.private & filters.text)
async def ON_URL(app: Client, message: types.Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    t = LANGUAGES[lang]

    url = message.text
    status, channl = await CHECK_JOIN_MEMBER(user_id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(t['join_prompt'].format(channl))
        return

    message_data = await message.reply(t["downloading"])

    if not url.startswith('https://t.me/'):
        await message_data.edit(t["invalid_link"])
        return

    try:
        chats_id = url.split('/')[-3]
        story_id = int(url.split('/')[-1])
    except Exception:
        await message_data.edit(t["invalid_link"])
        return

    status, story_data = await GET_STORES_DATA(chats_id, story_id)
    if not status:
        await message_data.edit(t["download_error"])
        return

    await message_data.edit(t["download_complete"])
    await app.send_video(chat_id=message.chat.id, video=story_data)

asyncio.run(app.run())
