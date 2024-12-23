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
    json.dump({'users':[], 'user_languages':{}} ,open('./data.json', 'w'), indent=3)

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

# Handle the '/start' command
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    datas = json.load(open('./data.json'))
    
    # Check if the user has selected a language before
    if message.from_user.id not in datas['user_languages']:
        # Send message to ask for language selection
        await message.reply(
            "🎉 Welcome to the Telegram Story Downloader bot! \nPlease select your preferred language.",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text="فارسی", callback_data="lang_fa")],
                [types.InlineKeyboardButton(text="English", callback_data="lang_en")]
            ])
        )
        return
    
    # Check if user has joined the channel
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(f"""👋 سلام! برای استفاده از ربات ابتدا در کانال ما عضو شوید: 
        📣  ❲ @{channl} ❳
        و پس از عضویت با ارسال دستور /start عضویت خود را تایید کنید.""")
        return

    # Check if the user is new
    if message.from_user.id not in datas['users']:
        datas['users'].append(message.from_user.id)
        json.dump(datas, open('./data.json', 'w'), indent=3)
        await app.send_message(
            chat_id=Config.SUDO, 
            text=f"""↫︙New User Joined The Bot:
            ↫ id :  ❲ {message.from_user.id} ❳
            ↫ username :  ❲ @{message.from_user.username} ❳
            ↫ firstname :  ❲ {message.from_user.first_name} ❳
            ↫ Total Members: ❲ {len(datas['users'])} ❳"""
        )
    
    # Load the user's language
    language = datas['user_languages'].get(message.from_user.id, 'en')
    
    if language == 'fa':
        await message.reply(
            "🎉 به ربات دانلود استوری تلگرام خوش آمدید! \nلطفاً لینک استوری را ارسال کنید تا آن را برایتان دانلود کنم.",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='💻 Developer', url='https://t.me/mrkral')],
                [types.InlineKeyboardButton(text='📚 Help', callback_data='help')]
            ])
        )
    else:
        await message.reply(
            "🎉 Welcome to the Telegram Story Downloader bot! \nPlease send the story link to download it.",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='💻 Developer', url='https://t.me/mrkral')],
                [types.InlineKeyboardButton(text='📚 Help', callback_data='help')]
            ])
        )

# Language Selection Callback
@app.on_callback_query(filters.regex('^lang_'))
async def on_language_select(app: Client, query: types.CallbackQuery):
    datas = json.load(open('./data.json'))
    language = query.data.split('_')[1]
    
    # Store the selected language
    datas['user_languages'][query.from_user.id] = language
    json.dump(datas, open('./data.json', 'w'), indent=3)

    # Send response in selected language
    if language == 'fa':
        await query.message.edit(
            "🎉 به ربات دانلود استوری تلگرام خوش آمدید! \nلطفاً لینک استوری را ارسال کنید تا آن را برایتان دانلود کنم.",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='💻 Developer', url='https://t.me/mrkral')],
                [types.InlineKeyboardButton(text='📚 Help', callback_data='help')]
            ])
        )
    else:
        await query.message.edit(
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
    datas = json.load(open('./data.json'))
    
    # Check if user has set a language
    if message.from_user.id not in datas['user_languages']:
        await message.reply("❌ Language not set. Please restart the bot using /start.")
        return
    
    # Validate URL
    if not url.startswith('https://t.me/'):
        await message.reply("❌ Invalid link. Please send a valid link.")
        return

    try:
        chat_id = url.split('/')[-3]
        story_id = int(url.split('/')[-1])
    except Exception as e:
        await message.reply("❌ Invalid link.")
        return

    # Proceed with story download
    await message.reply("⏳ Downloading story... Please wait.")
    status, story_data = await GET_STORES_DATA(chat_id, story_id)
    
    if not status:
        await message.reply("❌ Error occurred. Please try again.")
        return

    await message.reply("✅ Story downloaded successfully!")
    await app.send_video(chat_id=message.chat.id, video=story_data)

# Handle the '/help' command
@app.on_callback_query(filters.regex('help'))
async def on_help_query(app: Client, query: types.CallbackQuery):
    datas = json.load(open('./data.json'))
    language = datas['user_languages'].get(query.from_user.id, 'en')
    
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

# Handle the 'back' button press to return to the main menu
@app.on_callback_query(filters.regex('back'))
async def on_back_query(app: Client, query: types.CallbackQuery):
    datas = json.load(open('./data.json'))
    language = datas['user_languages'].get(query.from_user.id, 'en')
    
    if language == 'fa':
        await query.message.edit(
            "🎉 به ربات دانلود استوری تلگرام خوش آمدید! \nلطفاً لینک استوری را ارسال کنید تا آن را برایتان دانلود کنم.",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='💻 Developer', url='https://t.me/mrkral')],
                [types.InlineKeyboardButton(text='📚 Help', callback_data='help')]
            ])
        )
    else:
        await query.message.edit(
            "🎉 Welcome to the Telegram Story Downloader bot! \nPlease send the story link to download it.",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='💻 Developer', url='https://t.me/mrkral')],
                [types.InlineKeyboardButton(text='📚 Help', callback_data='help')]
            ])
        )

# Run the bot
asyncio.run(app.run())
