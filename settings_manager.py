# bot/settings_manager.py

import json
import os

SETTINGS_FILE = "bot_settings.json"

class BotSettings:
    def __init__(self):
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                "current_channel": "",
                "bot_username": "",
                "access_token": "",
                "mention_responses": [],
            }

    def save_settings(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def get_setting(self, key):
        return self.settings.get(key)

    def get_all_settings(self):
        return self.settings