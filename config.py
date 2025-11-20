import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API credentials
API_ID = os.getenv('API_ID', 'your_api_id')
API_HASH = os.getenv('API_HASH', 'your_api_hash')
BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token')

# Channel subscription
CHANNEL_ID = os.getenv('CHANNEL_ID', '@your_channel')  # Replace with your channel
BOT_USERNAME = os.getenv('BOT_USERNAME', 'your_bot_username')

# Admin IDs (comma-separated)
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '123456789').split(',')]

# Database path
DB_PATH = 'movie_bot.db'
