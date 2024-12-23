# Requier Modules 
# designer and programmer @mrkral
# https://github.com/ParsaPanahi
from pyrogram import Client, types, filters, enums
import asyncio 
import os
import requests
import json

# Bot Config Obj
class Config:
    API_KEY : str = "7884364837:AAF4IQw1YshU2O8qwc1IFWl_gR18EPTdnAg"  # ApiKey Bot
    API_HASH: str = "e51a3154d2e0c45e5ed70251d68382de"  # APi_Hash
    API_ID  : int = 15787995  # Api id
    SUDO    : int = 7046488481  # Sudo id 
    CHANNLS : list = ['Kali_Linux_BOTS']  # Channel List

# Check Bot Dirct Exists
if not os.path.exists('./.session'):
    os.mkdir('./.session')

# Check data base 
if not os.path.exists('./data.json'):
    json.dump({'users': []}, open('./data.json', 'w'), indent=3)

# Pyrogram App
app = Client(
    "./.session/kral", 
    bot_token=Config.API_KEY, 
    api_hash=Config.API_HASH, 
    api_id=Config.API_ID, 
    parse_mode=enums.ParseMode.DEFAULT
)

# Get Story Method 
async def GET_STORES_DATA(chat_id: str, story_id: int):
    app = Client(":memory:", api_hash=Config.API_HASH, api_id=Config.API_ID, workers=2, no_updates=True)
    try:
        await app.start()
        data = await app.download_media(await app.get_stories(chat_id=chat_id, story_ids=story_id), in_memory=True)
    except Exception as e:
        print(e)
        return (False, None)
    finally:
        await app.stop()

    return (True, data)

# Check Join Methods
async def CHECK_JOIN_MEMBER(user_id: int, channls: list, API_KEY: str):
    """
    user_id : The member telegram id 
    channls : list channls 
    API_KEY : Bot Token
    """
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

# On Start Bot 
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(
            f"سلام برای استفاده از ربات اول در کانال های ما عضو شوید\n\n📣  ❲ @{channl} ❳\n"
            "و بعد از عضو شدن با ارسال دستور ( /start ) عضویت خود را تایید کنید"
        )
        return

    # Load data
    datas = json.load(open('./data.json'))
    if message.from_user.id not in datas['users']:
        datas['users'].append(message.from_user.id)
        json.dump(datas, open('./data.json', 'w'), indent=3)
        await app.send_message(
            chat_id=Config.SUDO, 
            text=(
                f"↫︙NEw User Join The Bot.\n\n"
                f"↫ id : ❲ {message.from_user.id} ❳\n"
                f"↫ username : ❲ @{message.from_user.username} ❳\n"
                f"↫ firstname : ❲ {message.from_user.first_name} ❳\n\n"
                f"↫︙members Count NEw : ❲ {len(datas['users'])} ❳"
            )
        )
    await message.reply(
        text="به ربات دانلود استوری تلگرام خوش آمدید، لینک استوری را برای من ارسال کنید تا در عرض چند ثانیه دانلود کنم برات.",
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(text='programer', url='t.me/mrkral')]
        ])
    )

# On Send Story Url 
@app.on_message(filters.private & filters.text)
async def ON_URL(app: Client, message: types.Message):
    url = message.text
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply(
            f"سلام برای استفاده از ربات اول در کانال های ما عضو شوید\n\n📣  ❲ @{channl} ❳\n"
            "و بعد از عضو شدن با ارسال دستور ( /start ) عضویت خود را تایید کنید"
        )
        return

    message_data = await message.reply(text="درحال ارسال لطفاً صبر کنید")
    if not url.startswith('https://t.me/'):
        await message_data.edit(text="لینک ارسال شده نادرست هست")
        return

    try:
        chats_id = url.split('/')[-3]
        story_id = int(url.split('/')[-1])
    except Exception:
        await message_data.edit(text="لینک ارسال شده نادرست هست")
        return
        
    status, story_data = await GET_STORES_DATA(chats_id, story_id)
    if not status:
        await message_data.edit(text="متأسفیم، هنگام دانلود مشکلی پیش آمد")
        return

    await message_data.edit(text="دانلود با موفقیت انجام شد")
    await app.send_video(chat_id=message.chat.id, video=story_data)

# Run the Bot
app.run()
