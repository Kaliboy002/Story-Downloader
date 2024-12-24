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
    json.dump({'users': [], 'languages': {}}, open('./data.json', 'w'), indent=3)

# Initialize Pyrogram Client
app = Client(
    "./.session/bot",
    bot_token=Config.API_KEY,
    api_hash=Config.API_HASH,
    api_id=Config.API_ID,
    parse_mode=enums.ParseMode.DEFAULT
)

LANGUAGE_TEXTS = {
    "en": {
        "welcome": "Welcome to the Telegram Story Downloader bot! Send me the story link or username to download.",
        "join_channel": "To use this bot, you must join our channel first:\n\n📣 @{}\nClick the button below to verify your membership.",
        "verify_join": "Check Join",
        "not_joined": "You are not a member of our channel. Please join and try again.",
        "downloading": "Downloading, please wait...",
        "download_successful": "Download completed successfully!",
        "error": "Sorry, there was an issue while downloading.",
        "no_stories": "No recent stories found for the username: {}",
    },
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

# Story Downloader for Usernames
async def GET_STORIES_BY_USERNAME(username: str):
    client = Client(":memory:", api_hash=Config.API_HASH, api_id=Config.API_ID, session_string=Config.SESSION, workers=2, no_updates=True)
    try:
        await client.connect()
        user = await client.get_users(username)
        stories = await client.get_stories(chat_id=user.id)
        if not stories:
            return False, None, None
        latest_story = stories[0]
        media = await client.download_media(latest_story, in_memory=True)
        description = latest_story.caption if latest_story.caption else "No description available."
    except Exception as e:
        print(f"Error in GET_STORIES_BY_USERNAME: {e}")
        return False, None, None
    finally:
        await client.disconnect()
    return True, media, description

# On Start
@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    await message.reply(LANGUAGE_TEXTS["en"]["welcome"])

# Handle Story Links or Usernames
@app.on_message(filters.private & filters.text)
async def HANDLE_INPUT(app: Client, message: types.Message):
    user_id = message.from_user.id
    status, channel = await CHECK_JOIN_MEMBER(user_id, Config.CHANNLS, Config.API_KEY)
    if not status:
        join_message = LANGUAGE_TEXTS["en"]["join_channel"].format(channel)
        button = types.InlineKeyboardButton(LANGUAGE_TEXTS["en"]["verify_join"], callback_data="check_join")
        await message.reply(join_message, reply_markup=types.InlineKeyboardMarkup([[button]]))
        return

    input_text = message.text.strip()
    downloading_message = await message.reply(LANGUAGE_TEXTS["en"]["downloading"])

    if input_text.startswith('@'):  # Handle Username
        username = input_text[1:]
        status, story_data, description = await GET_STORIES_BY_USERNAME(username)
        if not status:
            await downloading_message.edit(LANGUAGE_TEXTS["en"]["no_stories"].format(username))
            return
    else:
        await downloading_message.edit(LANGUAGE_TEXTS["en"]["error"])
        return

    await downloading_message.edit(LANGUAGE_TEXTS["en"]["download_successful"])
    await app.send_video(chat_id=message.chat.id, video=story_data, caption=description)

# Run the bot
asyncio.run(app.run())
