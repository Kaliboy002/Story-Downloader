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
    SESSION : str = "BQG0lX0Aq1b5Qc5xhfgllDAKHB8GyOvj5bYEauDIAon_8wc4lH85gJRiat1YFysSLpZ7RjMuRnzALAmo-lJwxw03sWbZMO-6v8cyKhRVoT_H2mKukjxLYOudW7jW-7AK7Ca8B6QnnV9OqdHXjYVoWFjzJShp1ep3zpH9ldlRmUUgsYgpG8mlqPEQZ8VRDOnHbljXx23_yM3AzBArkRI0qAu0KO7vNnmuoZgkj8jUfRTDMEQyHRNNf0bNUshsfwVb1OU0w1fMRnji12R_Sp89GsgpCHe_tKcQfjieLKdxqxLVNByrNZOjAJee0dsR0DoMVAXnbYXLoYBYXWF7EtYhL-QXcYeBrgAAAAG6ViRWAA"
    API_KEY : str = "7884364837:AAF4IQw1YshU2O8qwc1IFWl_gR18EPTdnAg"
    API_HASH: str = "e51a3154d2e0c45e5ed70251d68382de"
    API_ID  : int = 15787995 
    SUDO    : int = 7046488481 
    CHANNLS : str = ['Kali_Linux_BOTS'] 

# Check Bot Directory Exists
if not os.path.exists('./.session'):
    os.mkdir('./.session')

# Check data base 
if not os.path.exists('./data.json'):
    json.dump({'users':[]} ,open('./data.json', 'w'), indent=3)

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

# Language messages
messages = {
    'en': {
        'start': "Welcome to the Telegram Story Downloader Bot! Please send a story link to download it.",
        'invalid_link': "❌ The link you provided is invalid. Please send a valid link.",
        'downloading': "⏳ Downloading story... Please wait.",
        'downloaded': "✅ Story downloaded successfully! Sending now...",
        'help': "📘 Bot Help:\n1️⃣ Join our channel first.\n2️⃣ Send the Telegram story link.\n3️⃣ The bot will download the story for you.",
        'language_prompt': "Please select your language:",
        'language_selected': "Language selected: {lang}"
    },
    'fa': {
        'start': "🎉 به ربات دانلود استوری تلگرام خوش آمدید! لطفاً لینک استوری را ارسال کنید تا آن را برایتان دانلود کنم.",
        'invalid_link': "❌ لینک ارسال شده نادرست است. لطفاً یک لینک معتبر ارسال کنید.",
        'downloading': "⏳ در حال دانلود استوری... لطفاً صبر کنید.",
        'downloaded': "✅ استوری با موفقیت دانلود شد! ارسال می‌شود...",
        'help': "📘 راهنمای ربات:\n1️⃣ ابتدا در کانال ما عضو شوید.\n2️⃣ لینک استوری تلگرام را ارسال کنید.\n3️⃣ ربات استوری را برای شما دانلود خواهد کرد.",
        'language_prompt': "لطفاً زبان خود را انتخاب کنید:",
        'language_selected': "زبان انتخاب شده: {lang}"
    }
}

# Helper function to send language selection
async def send_language_selection(message: types.Message):
    markup = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton(text="فارسی", callback_data="lang_fa")],
        [types.InlineKeyboardButton(text="English", callback_data="lang_en")]
    ])
    await message.reply(messages['en']['language_prompt'], reply_markup=markup)

# Handle the '/start' command
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    # Check if the user is new
    datas = json.load(open('./data.json'))
    if message.from_user.id not in datas['users']:
        datas['users'].append(message.from_user.id)
        json.dump(datas, open('./data.json', 'w'), indent=3)

    await send_language_selection(message)

# Language selection
@app.on_callback_query(filters.regex('^lang_'))
async def on_language_select(app: Client, query: types.CallbackQuery):
    lang = query.data.split('_')[1]
    if lang not in messages:
        lang = 'en'  # Default to English if something goes wrong
    
    # Update user language preference
    datas = json.load(open('./data.json'))
    user_id = query.from_user.id
    user_data = next((user for user in datas['users'] if user.get('id') == user_id), None)
    if user_data:
        user_data['language'] = lang
    else:
        datas['users'].append({'id': user_id, 'language': lang})
    json.dump(datas, open('./data.json', 'w'), indent=3)
    
    await query.answer()
    await query.message.edit(messages[lang]['language_selected'].format(lang=lang))
    await query.message.reply(messages[lang]['start'])

# Handle story URL input
@app.on_message(filters.private & filters.text)
async def ON_URL(app: Client, message: types.Message):
    user_lang = 'en'  # Default to English
    datas = json.load(open('./data.json'))
    user_data = next((user for user in datas['users'] if user['id'] == message.from_user.id), None)
    if user_data:
        user_lang = user_data.get('language', 'en')

    url = message.text
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(f"👋 Hello! To use the bot, please join our channel: \n📣 @{channl} and send /start after joining.")
        return

    # Validate URL
    if not url.startswith('https://t.me/'):
        await message.reply(messages[user_lang]['invalid_link'])
        return

    try:
        chat_id = url.split('/')[-3]
        story_id = int(url.split('/')[-1])
    except Exception as e:
        await message.reply(messages[user_lang]['invalid_link'])
        return

    message_data = await message.reply(messages[user_lang]['downloading'])
    
    # Fetch and send story data
    status, story_data = await GET_STORES_DATA(chat_id, story_id)
    if not status:
        await message_data.edit(f"❌ Something went wrong! Please try again later.")
        return

    # Simulate real-time download (based on story data size or any arbitrary logic you prefer)
    download_duration = 30  # Assume it takes 30 seconds to download the story
    for progress in range(0, 101, 5):  # 0 to 100%
        await message_data.edit(f"{messages[user_lang]['downloading']} {progress}%")
        time.sleep(download_duration / 20)  # Simulate real time delay

    await message_data.edit(messages[user_lang]['downloaded'])
    await app.send_video(
        chat_id=message.chat.id, video=story_data, caption=f"{messages[user_lang]['downloaded']}"
    )

# Handle the '/help' command
@app.on_callback_query(filters.regex('help'))
async def on_help_query(app: Client, query: types.CallbackQuery):
    user_lang = 'en'
    datas = json.load(open('./data.json'))
    user_data = next((user for user in datas['users'] if user['id'] == query.from_user.id), None)
    if user_data:
        user_lang = user_data.get('language', 'en')
    
    await query.answer()
    await query.message.edit(messages[user_lang]['help'], reply_markup=types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton(text='🔙 Back', callback_data='back')]
    ]))

@app.on_callback_query(filters.regex('back'))
async def on_back_query(app: Client, query: types.CallbackQuery):
    user_lang = 'en'
    datas = json.load(open('./data.json'))
    user_data = next((user for user in datas['users'] if user['id'] == query.from_user.id), None)
    if user_data:
        user_lang = user_data.get('language', 'en')
    
    await query.answer()
    await query.message.edit(messages[user_lang]['start'], reply_markup=types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton(text='💻 Developer', url='https://t.me/mrkral')],
        [types.InlineKeyboardButton(text='📚 Help', callback_data='help')]
    ]))

# Run the bot
asyncio.run(app.run())
