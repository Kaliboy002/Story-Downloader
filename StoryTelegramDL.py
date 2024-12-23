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

# Handle the '/start' command
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(f"""👋 سلام! برای استفاده از ربات ابتدا در کانال ما عضو شوید: 
        📣  ❲ @{channl} ❳
        و پس از عضویت با ارسال دستور /start عضویت خود را تایید کنید.""")
        return

    # Load data and check if the user is new
    datas = json.load(open('./data.json'))
    if not message.from_user.id in datas['users']:
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
    await message.reply(
        "🎉 به ربات دانلود استوری تلگرام خوش آمدید! \nلطفاً لینک استوری را ارسال کنید تا آن را برایتان دانلود کنم.",
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(text='💻 Developer', url='https://t.me/mrkral')],
            [types.InlineKeyboardButton(text='📚 Help', callback_data='help')]
        ])
    )

# Handle story URL input
@app.on_message(filters.private & filters.text)
async def ON_URL(app: Client, message: types.Message):
    url = message.text
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(f"""👋 سلام! برای استفاده از ربات ابتدا در کانال ما عضو شوید: 
        📣  ❲ @{channl} ❳
        و پس از عضویت با ارسال دستور /start عضویت خود را تایید کنید.""")
        return

    # Validate URL
    if not url.startswith('https://t.me/'):
        await message.reply("❌ لینک ارسال شده نادرست است. لطفاً یک لینک معتبر ارسال کنید.")
        return

    try:
        chat_id = url.split('/')[-3]
        story_id = int(url.split('/')[-1])
    except Exception as e:
        await message.reply("❌ لینک ارسال شده نادرست است.")
        return

    message_data = await message.reply("⏳ در حال دانلود استوری... لطفاً صبر کنید.")
    
    # Fetch and send story data
    status, story_data = await GET_STORES_DATA(chat_id, story_id)
    if not status:
        await message_data.edit("❌ متاسفانه خطایی رخ داده است. لطفاً دوباره تلاش کنید.")
        return

    # Get the total size of the story
    total_size = len(story_data.getbuffer())  # Get the size of the story (in bytes)

    # Simulate the progress
    progress = 0
    chunk_size = total_size // 10  # You can adjust this if needed for finer progress updates

    loading_message = await message.reply("🔄 در حال بارگذاری استوری...")
    while progress < total_size:
        progress += chunk_size
        progress_percentage = (progress / total_size) * 100
        # Create the tube-shaped progress bar
        progress_bar = '▰' * (progress_percentage // 10) + '▱' * (10 - progress_percentage // 10)
        await loading_message.edit(f"📤 در حال دانلود استوری... {progress_percentage:.0f}% {progress_bar}")
        await asyncio.sleep(0.5)  # Simulate the time delay for downloading

    await message_data.edit("✅ استوری با موفقیت دانلود شد! ارسال می‌شود...")
    user_details = f"🎥 استوری از {message.from_user.first_name} (@{message.from_user.username})"
    await app.send_video(
        chat_id=message.chat.id, video=story_data, caption=f"{user_details}\n📹 استوری دانلود شده:"
    )

# Handle the '/help' command
@app.on_callback_query(filters.regex('help'))
async def on_help_query(app: Client, query: types.CallbackQuery):
    await query.answer()
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

@app.on_callback_query(filters.regex('back'))
async def on_back_query(app: Client, query: types.CallbackQuery):
    await query.answer()
    await query.message.edit(
        "🎉 به ربات دانلود استوری تلگرام خوش آمدید! \nلطفاً لینک استوری را ارسال کنید تا آن را برایتان دانلود کنم.",
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(text='💻 Developer', url='https://t.me/mrkral')],
            [types.InlineKeyboardButton(text='📚 Help', callback_data='help')]
        ])
    )

# Run the bot
asyncio.run(app.run())
