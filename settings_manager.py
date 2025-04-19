import json

SETTINGS_FILE_PATH = 'data/bot_settings.json'

class BotSettings:
    def __init__(self, settings_file=SETTINGS_FILE_PATH):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
