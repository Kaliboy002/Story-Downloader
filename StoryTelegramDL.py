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
    SESSION : str = "BQG0lX0Aq1b5Qc5xhfgllDAKHB8GyOvj5bYEauDIAon_8wc4lH85gJRiat1YFysSLpZ7RjMuRnzALAmo-lJwxw03sWbZMO-6v8cyKhRVoT_H2mKukjxLYOudW7jW-7AK7Ca8B6QnnV9OqdHXjYVoWFjzJShp1ep3zpH9ldlRmUUgsYgpG8mlqPEQZ8VRDOnHbljXx23_yM3AzBArkRI0qAu0KO7vNnmuoZgkj8jUfRTDMEQyHRNNf0bNUshsfwVb1OU0w1fMRnji12R_Sp89GsgpCHe_tKcQfjieLKdxqxLVNByrNZOjAJee0dsR0DoMVAXnbYXLoYBYXWF7EtYhL-QXcYeBrgAAAAG6ViRWAA" # Pyrogram Sessions
    API_KEY : str = "7884364837:AAF4IQw1YshU2O8qwc1IFWl_gR18EPTdnAg" # ApiKey Bot
    API_HASH: str = "e51a3154d2e0c45e5ed70251d68382de" # APi_Hash
    API_ID  : int = 15787995 # Api id
    SUDO    : int = 7046488481 # Sudo id 
    CHANNLS : str = ['Kali_Linux_BOTS'] # channel List
 

# Check Bot Dirct Exists
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

# get Sotrye Methods 
async def GET_STORES_DATA(chat_id: str, story_id: int):
    # Start Pyro Client
    app = Client(':memory:', api_hash=Config.API_HASH, api_id=Config.API_ID, session_string=Config.SESSION, workers=2, no_updates=True)
    try:
        await app.connect()
    except Exception as e:
        print(e)
        return (False, None)
    # Get Storys
    try:
        data = await app.download_media(await app.get_stories(chat_id=chat_id, story_ids=story_id) , in_memory=True,)
    except Exception as e:
        print(e)
        return (False, None)

    await app.disconnect()
    return (True, data)

# Check Join Medthodes
async def CHECK_JOIN_MEMBER(user_id: int, channls: list, API_KEY: str):
    """
    user_id : The member telegram id 
    channls : list channls 
    API_KEY : Bot Token
    """
    states = ['administrator','creator','member','restricted']
    # Start Loop
    for channl in channls:
        try:
            api =f"https://api.telegram.org/bot{API_KEY}/getChatMember?chat_id=@{channl}&user_id={user_id}"
            respons = requests.get(api).json()
            # Check Status 
            if respons['result']['status'] not in states:
                return (False, channl)
        except:
                return (False, channl)

    return (True, None)

# on Start Bot 
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply("""سلام برای استفاده از ربات اول در کانال های ما عضو شوید\n\n📣  ❲ @{} ❳\n و بعد از عضو شدن با ارسال دستور ( /start ) عضویت خود را تایید کنید
        """.format(channl))
        return

    # Load data
    datas = json.load(open('./data.json'))
    if not message.from_user.id in datas['users']:
        datas['users'].append(message.from_user.id)
        json.dump(datas ,open('./data.json', 'w'), indent=3)
        await app.send_message(
            chat_id=Config.SUDO, text="""↫︙NEw User Join The Bot .\n\n  ↫ id :  ❲ {} ❳\n  ↫ username :  ❲ @{} ❳\n  ↫ firstname :  ❲ {} ❳\n\n↫︙members Count NEw : ❲ {} ❳"""
            .format(message.from_user.id, message.from_user.username, message.from_user.first_name,len(datas['users']))
        )
    await message.reply(text="به ربات دانلود استوری تلگرام خوش آمدید، لینک استوری را برای من ارسال کنید تا در عرض چند ثانیه دانلود کنم برات.", reply_markup=types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton(text='programer', url='t.me/mrkral')]
    ]))



# On Send Story Url https://t.me/MrKRAL/s/63
@app.on_message(filters.private & filters.text)
async def ON_URL(app: Client, message: types.Message):
    url = message.text
    status, channl = await CHECK_JOIN_MEMBER(message.from_user.id, Config.CHANNLS, Config.API_KEY)
    if not status:
        await message.reply("""سلام برای استفاده از ربات اول در کانال های ما عضو شوید\n\n📣  ❲ @{} ❳\n و بعد از عضو شدن با ارسال دستور ( /start ) عضویت خود را تایید کنید
        """.format(channl))
        return
    message_data = await message.reply(text="درحال ارسال لطفاً صبر کنید")
    # Check Url 
    if not url.startswith('https://t.me/'):
        await message_data.edit(text="لینک ارسال شده نادرست هست")
        return
    # Get Stor data 
    # Split Url 
    try:
        chats_id = url.split('/')[-3]
        story_id = int(url.split('/')[-1])
    except Exception as e:
        await message_data.edit(text="لینک ارسال شده نادرست هست")
        return
        
    # Get Story And Download 
    status, story_data = await GET_STORES_DATA(chats_id, story_id)
    # Checkc data 
    if not status:
        await message_data.edit(text="متأسفیم، هنگام دانلود مشکلی پیش آمد")
        return
    await message_data.edit(text="دانلود با موفقیت انجام شد")
    await app.send_video(
        chat_id=message.chat.id, video=story_data
    )

    

asyncio.run(app.run())
