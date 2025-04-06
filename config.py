
import os

# Game timers (in seconds)
QUESTION_TIMER = 10  # Timer for each question
REGISTRATION_TIMER = 15  # Timer for group mode registration
TEAM_REGISTRATION_TIMER = 20  # Timer for team mode registration
LEADER_SELECTION_TIMER = 10  # Timer for leader selection
SABOTAGE_SELECTION_TIMER = 15  # Timer for sabotage selection
MAX_QUESTIONS_TEAM = 15  # Maximum questions for team mode
MAX_QUESTIONS_SOLO = 20  # Maximum questions for solo/challenge mode

# Database URL configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///widuxbot.db')

# Twitch configuration
TWITCH_TMI_TOKEN = os.environ.get('TWITCH_TMI_TOKEN')
TWITCH_CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
TWITCH_BOT_USERNAME = os.environ.get('TWITCH_BOT_USERNAME', 'WiduxBot')
