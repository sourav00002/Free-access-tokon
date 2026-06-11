import telebot
import requests
import time
from urllib.parse import urlparse, parse_qs

# Aapka provide kiya hua token
BOT_TOKEN = "8693776236:AAGjvjjJ4Go8C1msijo4dsVu_KdOd4mIaR4"
bot = telebot.TeleBot(BOT_TOKEN)

def extract_eat_info(eat_token):
    try:
        url = f"https://api-otrss.garena.com/support/callback/?access_token={eat_token}"
        # Timeout thoda kam rakha hai taaki bot fast response de
        response = requests.get(url, allow_redirects=True, timeout=20, verify=False)
        
        if "help.garena.com" in response.url:
            parsed = urlparse(response.url)
            params = parse_qs(parsed.query)
            return {
                "access_token": params.get('access_token', [None])[0],
                "region": params.get('region', [None])[0],
                "game_uid": params.get('account_id', [None])[0],
                "nickname": params.get('nickname', [None])[0]
            }
        else:
            data = response.json()
            return {
                "access_token": data.get('access_token'),
                "region": data.get('region'),
                "game_uid": data.get('account_id') or data.get('game_uid'),
                "nickname": data.get('nickname')
            }
    except Exception:
        return None

def parse_eat_input(user_input):
    if user_input.startswith(('http://', 'https://')):
        parsed = urlparse(user_input)
        params = parse_qs(parsed.query)
        eat_token = params.get('eat', [None])[0]
        if eat_token:
            return eat_token, {
                'region': params.get('region', [None])[0],
                'game_uid': params.get('account_id', [None])[0],
                'nickname': params.get('nickname', [None])[0]
            }
    return user_input, {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 **Welcome to EAT Extractor Bot!**\n\n"
        "Sourav, aap apna EAT token ya URL yahan paste karein, "
        "main details extract kar dunga."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_extraction(message):
    user_input = message.text.strip()
    
    msg = bot.reply_to(message, "🔍 *Extracting data... Please wait.*", parse_mode='Markdown')
    
    eat_token, extras = parse_eat_input(user_input)
    info = extract_eat_info(eat_token)
    
    if not info: info = {}

    access_token = info.get('access_token')
    region = info.get('region') or extras.get('region')
    game_uid = info.get('game_uid') or extras.get('game_uid')
    nickname = info.get('nickname') or extras.get('nickname')

    if not access_token:
        bot.edit_message_text("❌ *Failed to obtain access token.*", chat_id=message.chat.id, message_id=msg.message_id, parse_mode='Markdown')
        return

    result_text = (
        "🎯 **EXTRACTION RESULTS** 🎯\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Nickname:** `{nickname}`\n"
        f"🆔 **UID:** `{game_uid}`\n"
        f"🌍 **Region:** `{region}`\n\n"
        f"🔑 **Access Token:**\n`{access_token}`"
    )
    
    bot.edit_message_text(result_text, chat_id=message.chat.id, message_id=msg.message_id, parse_mode='Markdown')

print("Bot is running...")
bot.polling()