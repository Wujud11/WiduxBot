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
                "mention_guard_duration": 86400,
                "mention_guard_cooldown": 5,
                "mention_guard_warning_thresh": 2,
                "mention_guard_warn_msg": "لا تصايح كل شوي، انتبه!",
                "mention_guard_timeout_msg": "تايم آوت بسيط، عشان تحترم نفسك شوي."
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

    def update_bot_settings(self, form_data):
        keys = [
            "bot_username", "access_token", "mention_guard_duration",
            "mention_guard_cooldown", "mention_guard_warning_thresh",
            "mention_guard_warn_msg", "mention_guard_timeout_msg"
        ]
        for key in keys:
            value = form_data.get(key)
            if value is not None:
                if key in ["mention_guard_duration", "mention_guard_cooldown", "mention_guard_warning_thresh"]:
                    value = int(value)
                self.update_setting(key, value)

    def add_channel(self, channel_name):
        if "channels" not in self.settings:
            self.settings["channels"] = []
        if channel_name not in self.settings["channels"]:
            self.settings["channels"].append(channel_name)
            self.save_settings()

    def delete_channel(self, channel_name):
        if "channels" in self.settings and channel_name in self.settings["channels"]:
            self.settings["channels"].remove(channel_name)
            self.save_settings()

    def get_channel_settings(self, channel_name):
        return {
            "bot_username": self.settings.get("bot_username", ""),
            "access_token": self.settings.get("access_token", "")
        }

    def update_channel_settings(self, channel_name, form_data):
        # تحديث الإعدادات العامة (ما عندنا إعدادات خاصة لكل قناة حالياً)
        self.update_bot_settings(form_data)

    def update_custom_responses(self, form_data):
        responses = {}
        for key in form_data:
            responses[key] = form_data[key].split("\n")
        self.settings["custom_responses"] = responses
        self.save_settings()
