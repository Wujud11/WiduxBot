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
                "bot_username": "",
                "access_token": "",
                "channels": [],
                "mention_limit": 2,
                "mention_guard_warn_msg": "ترى ببلعك تايم أوت",
                "mention_guard_timeout_msg": "القم! أنا حذرتك",
                "mention_guard_duration": 3,
                "mention_guard_cooldown": 86400,
                "mention_daily_cooldown": True,
                "mention_responses": [],
                "special_responses": {},
                "custom_responses": {},
                "questions": []
            }

    def save_settings(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def get_setting(self, key):
        return self.settings.get(key)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def get_all_settings(self):
        return self.settings
