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
    json.dump({'users': [], 'languages': {}}, open('./data.json', 'w'), indent=3)

# Initialize Pyrogram Client
app = Client(
    "./.session/bot",
    bot_token=Config.API_KEY,
    api_hash=Config.API_HASH,
    api_id=Config.API_ID,
    parse_mode=enums.ParseMode.DEFAULT
)

# Language Texts
LANGUAGE_TEXTS = {
    "en": {
        "welcome": "Welcome to hell our services and about to break up ☝️ for sale your password 🔑 remember that when you can use of undefined variable index of this website uses the same the Telegram Story Downloader bot! Send me the story link to download.",
        "join_channel": "⚠️<b> To use this bot, you must first join our Telegram channels</b>\n\nAfter successfully joining, click the 🔐𝗝𝗼𝗶𝗻𝗲𝗱 button to confirm your bot membership.",
        "verify_join": "Check Join",
        "join_channel_btn": "Join Channel",
        "not_joined": "You are not a member of our channel. Please join and try again.",
        "downloading": "Downloading, please wait...",
        "download_successful": "Download completed successfully!",
        "error": "Sorry, there was an issue while downloading.",
        "image_url": "https://AnonyDL.tlspro.space/AgACAgUAAxkBAAJBpmdrjKemUvIM73wpC9aTUphJe1RBAAJavjEbrDphVyhrE5AaRcrCAQADAgADeQADNgQ/65357649.jpg"
    },
    "fa": {
        "welcome": "به ربات دانلود استوری تلگرام خوش آمدید! لینک استوری را برای دانلود ارسال کنید.",
        "join_channel": "<b>⚠️ برای استفاده از این ربات، نخست شما باید به کانال‌ های زیر عضو گردید</b>.\n\nدر غیر اینصورت این ربات برای شما کار نخواهد کرد. سپس روی دکمه | </b>عضـو شـدم 🔐<b> | کلیک کنید تا عضویت ربات خود را تأیید کنید",
        "verify_join": "بررسی عضویت",
        "join_channel_btn": "عضویت در کانال",
        "not_joined": "شما عضو کانال ما نیستید. لطفاً عضو شوید و دوباره امتحان کنید.",
        "downloading": "در حال دانلود، لطفاً صبر کنید...",
        "download_successful": "دانلود با موفقیت انجام شد!",
        "error": "متاسفانه مشکلی در دانلود پیش آمده است.",
        "image_url": "https://AnonyDL.tlspro.space/AgACAgUAAxkBAAJBpmdrjKemUvIM73wpC9aTUphJe1RBAAJavjEbrDphVyhrE5AaRcrCAQADAgADeQADNgQ/65357649.jpg"
    }
}

# Check Join Method
async def CHECK_JOIN_MEMBER(user_id: int, channels: list, api_key: str):
    states = ['administrator', 'creator', 'member', 'restricted']
    for channel in channels:
        try:
            api_url = f"https://api.telegram.org/bot{api_key}/getChatMember?chat_id=@{channel}&user_id={user_id}"
            response = requests.get(api_url).json()
            if response.get('ok') and response['result']['status'] in states:
                continue
            else:
                return False, channel
        except Exception as e:
            print(f"Error checking membership: {e}")
            return False, channel
    return True, None

# Story Downloader Method
async def GET_STORES_DATA(chat_id: str, story_id: int):
    client = Client(":memory:", api_hash=Config.API_HASH, api_id=Config.API_ID, session_string=Config.SESSION, workers=2, no_updates=True)
    try:
        await client.connect()
        story = await client.get_stories(chat_id=chat_id, story_ids=[story_id])
        if not story:
            return False, None, None
        media = await client.download_media(story[0], in_memory=True)
        description = story[0].caption if story[0].caption else "No description available."
    except Exception as e:
        print(f"Error in GET_STORES_DATA: {e}")
        return False, None, None
    finally:
        await client.disconnect()
    return True, media, description

# On Start and Language Selection
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    data = json.load(open('./data.json'))
    if message.from_user.id not in data['users']:
        data['users'].append(message.from_user.id)
        json.dump(data, open('./data.json', 'w'), indent=3)
        await app.send_message(
            chat_id=Config.SUDO,
            text=f"↫︙New User Joined The Bot.\n\n  ↫ ID: ❲ {message.from_user.id} ❳\n  ↫ Username: ❲ @{message.from_user.username or 'None'} ❳\n  ↫ Firstname: ❲ {message.from_user.first_name} ❳\n\n↫︙Total Members: ❲ {len(data['users'])} ❳"
        )

    keyboard = [
        [types.InlineKeyboardButton("فارســی 🇮🇷", callback_data="lang_fa"), types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    await message.reply("🇺🇸 <b>Select the language of your preference from below to continue</b>\n"
            "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
            "🇦🇫 <b>برای ادامه، لطفا نخست زبان مورد نظر خود را از گزینه زیر انتخاب کنید</b>", reply_markup=types.InlineKeyboardMarkup(keyboard))

# Handle Language Selection
@app.on_callback_query(filters.regex('^lang_'))
async def language_selection(app: Client, callback_query: types.CallbackQuery):
    language = callback_query.data.split('_')[1]
    user_id = str(callback_query.from_user.id)

    data = json.load(open('./data.json'))
    data['languages'][user_id] = language
    json.dump(data, open('./data.json', 'w'), indent=3)

    join_message = LANGUAGE_TEXTS[language]["join_channel"].format(Config.CHANNLS[0])
    join_button = types.InlineKeyboardButton(LANGUAGE_TEXTS[language]["join_channel_btn"], url=f"https://t.me/{Config.CHANNLS[0]}")
    verify_button = types.InlineKeyboardButton(LANGUAGE_TEXTS[language]["verify_join"], callback_data="check_join")

    await callback_query.message.edit(
        text=join_message,
        reply_markup=types.InlineKeyboardMarkup([[join_button], [verify_button]])
    )

# Verify Channel Join
@app.on_callback_query(filters.regex('^check_join$'))
async def check_join(app: Client, callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = json.load(open('./data.json'))
    language = data['languages'].get(str(user_id), 'en')

    status, channel = await CHECK_JOIN_MEMBER(user_id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await callback_query.answer(LANGUAGE_TEXTS[language]["not_joined"], show_alert=True)
        return

    image_url = LANGUAGE_TEXTS[language]["image_url"]
    await callback_query.message.edit(text=LANGUAGE_TEXTS[language]["welcome"])
    await app.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=image_url,
        caption=LANGUAGE_TEXTS[language]["welcome"]
    )

# On Send Story URL
@app.on_message(filters.private & filters.text)
async def ON_URL(app: Client, message: types.Message):
    user_id = str(message.from_user.id)
    data = json.load(open('./data.json'))
    language = data['languages'].get(user_id, 'en')

    status, channel = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        join_message = LANGUAGE_TEXTS[language]["join_channel"].format(channel)
        join_button = types.InlineKeyboardButton(LANGUAGE_TEXTS[language]["join_channel_btn"], url=f"https://t.me/{channel}")
        verify_button = types.InlineKeyboardButton(LANGUAGE_TEXTS[language]["verify_join"], callback_data="check_join")
        await message.reply(join_message, reply_markup=types.InlineKeyboardMarkup([[join_button], [verify_button]]))
        return

    downloading_message = await message.reply(LANGUAGE_TEXTS[language]["downloading"])

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

    status, story_data, description = await GET_STORES_DATA(chat_id, story_id)
    if not status:
        await downloading_message.edit(LANGUAGE_TEXTS[language]["error"])
        return

    await downloading_message.edit(LANGUAGE_TEXTS[language]["download_successful"])
    await app.send_video(chat_id=message.chat.id, video=story_data, caption=description)

# Run the bot
asyncio.run(app.run())
