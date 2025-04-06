
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Game timers (in seconds)
QUESTION_TIMER = 10  
REGISTRATION_TIMER = 15  
TEAM_REGISTRATION_TIMER = 20  
LEADER_SELECTION_TIMER = 10  
SABOTAGE_SELECTION_TIMER = 15  
MAX_QUESTIONS_TEAM = 15  
MAX_QUESTIONS_SOLO = 20  

# Database URL configuration - Render provides this
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Twitch configuration - Set these in Render environment variables
TWITCH_TMI_TOKEN = os.environ.get('TWITCH_TMI_TOKEN')
TWITCH_CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
TWITCH_BOT_USERNAME = os.environ.get('TWITCH_BOT_USERNAME', 'WiduxBot')
