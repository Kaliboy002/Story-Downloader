import telebot
import requests
from bs4 import BeautifulSoup
import re

bot = telebot.TeleBot("8179647576:AAGPGp13Pp-qF32KqDivMTEn-4LHOLcpRpI")

user_search_data = {}

class SearchData:
    def __init__(self):
        self.text = ''
        self.page = 0
        self.total_videos = 0
        self.videos = []

def extract_and_return_url(anchor):
    clip_id = re.search(r'/yarn-clip/(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})', anchor['href']).group(1)
    forward_url = f"https://y.yarn.co/{clip_id}_thumb.mp4"
    return forward_url

def extract_title_and_transcript(element):
    title = element.find('div', class_='title ab fw5 p025 px05 tal').text.strip()
    transcript = element.find('div', class_='transcript db bg-w fwb p05 tal').text.strip()
    return title, transcript

def parse_page(text, page):
    base_url = "https://yarn.co/yarn-find"
    url = f"{base_url}?text={text}&p={page}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all(class_="clip bg-t rel nomob")
    videos = []
    for element in elements:
        anchor = element.find('a', href=re.compile(r'/yarn-clip/(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})'))
        if anchor:
            title, transcript = extract_title_and_transcript(element)
            video_url = extract_and_return_url(anchor)
            videos.append((video_url, title, transcript))
    return videos

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Welcome! I'm the Memes and Clips Bot 😎\n\n"
        "I can help you find clips from movies, films, and cartoons based on the text you send. "
        "Just enter the text and I'll search for matching clips for you!\n\n"
        "Use the /help command to see more information and how to use me."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "Here's how you can use me:\n\n"
        "1. Send /clip followed by the text you want to find clips for.\n"
        "2. I'll search for clips based on the text and send them to you.\n"
        "3. If you want to load more clips, just click on 'Yes' when prompted.\n\n"
        "Have fun searching for memes and clips! 😊🎬🔍"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['clip'])
def handle_clip_command(message):
    global user_search_data
    user_id = message.chat.id
    clip_command_parts = message.text.split("/clip ", 1)
    if len(clip_command_parts) > 1:
        text = clip_command_parts[1]
        search_data = SearchData()
        search_data.text = text
        user_search_data[user_id] = search_data
        search_videos(message.chat.id)
    else:
        bot.reply_to(message, "Please provide the text to search for clips.")

def search_videos(chat_id):
    global user_search_data
    user_id = chat_id
    search_data = user_search_data.get(user_id)
    if search_data:
        search_data.videos = parse_page(search_data.text, search_data.page)
        if search_data.videos:
            for video_data in search_data.videos:
                video_url, title, transcript = video_data
                caption = f"From: {title} 🎦\nClip: {transcript} 📋"
                bot.send_video(chat_id, video_url, caption=caption)
                search_data.total_videos += 1
            bot.send_message(chat_id, f"Found {len(search_data.videos)} videos. Do you want to load more videos?",reply_markup=create_inline_keyboard_markup())
        else:
            bot.send_message(chat_id, "No videos found.")
    else:
        bot.send_message(chat_id, "No search data found.")

@bot.callback_query_handler(func=lambda call: call.data == 'load_more')
def load_more_videos(call):
    global user_search_data
    user_id = call.message.chat.id
    search_data = user_search_data.get(user_id)
    if search_data:
        search_data.page += 1
        bot.delete_message(call.message.chat.id, call.message.message_id)
        search_videos(call.message.chat.id)
    else:
        bot.send_message(call.message.chat.id, "No search data found.")

@bot.callback_query_handler(func=lambda call: call.data == 'no_more')
def no_more_videos(call):
    global user_search_data
    user_id = call.message.chat.id
    search_data = user_search_data.get(user_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if search_data and search_data.total_videos > 0:
        bot.send_message(call.message.chat.id, f"Total {search_data.total_videos} videos found.\nSend /start",parse_mode='Markdown')
    else:
        bot.send_message(call.message.chat.id, "No videos found.")

def create_inline_keyboard_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton(text='Yes', callback_data='load_more'),
        telebot.types.InlineKeyboardButton(text='No', callback_data='no_more')
    )
    return markup

bot.polling()
