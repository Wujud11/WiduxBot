import os
from dotenv import load_dotenv

load_dotenv()

# Twitch Configuration
TWITCH_TMI_TOKEN = os.getenv('TWITCH_TMI_TOKEN') 
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
TWITCH_BOT_USERNAME = os.getenv('TWITCH_BOT_USERNAME', 'WiduxBot')
TWITCH_INITIAL_CHANNELS = os.getenv('TWITCH_INITIAL_CHANNELS', '').split(',')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///widuxbot.db')

# Game Configuration
QUESTION_TIMER = 10  # seconds
REGISTRATION_TIMER = 15  # seconds for تحدي mode
TEAM_REGISTRATION_TIMER = 20  # seconds for تيم mode
LEADER_SELECTION_TIMER = 20  # seconds
SABOTAGE_SELECTION_TIMER = 20  # seconds for sabotage target selection
