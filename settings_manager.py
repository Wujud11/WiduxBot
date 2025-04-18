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
                "mention_guard_warn_msg": "",
                "mention_guard_timeout_msg": "",
                "mention_guard_duration": 5,
                "mention_guard_cooldown": 86400,
                "mention_daily_cooldown": True,
                "mention_responses": [],
                "special_responses": {},
                "custom_responses": {
                    "solo_win_responses": [],
                    "team_win_responses": [],
                    "team_lose_responses": [],
                    "group_win_responses": [],
                    "group_lose_responses": [],
                    "below_50_responses": [],
                    "below_zero_responses": [],
                    "doomed_leader_responses": [],
                    "weak_leader_responses": [],
                    "kicked_responses": [],
                    "stolen_responses": []
                },
                "questions": []
            }
            self.save_settings()

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

    def update_bot_settings(self, form_data):
        keys = [
            "bot_username", "access_token", "mention_limit",
            "mention_guard_warn_msg", "mention_guard_timeout_msg",
            "mention_guard_duration", "mention_guard_cooldown",
            "mention_daily_cooldown"
        ]
        for key in keys:
            if key in form_data:
                self.update_setting(key, form_data[key])
