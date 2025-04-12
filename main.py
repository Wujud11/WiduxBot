import asyncio
from twitchio.ext import commands
from bot.engine import WiduxEngine
from bot.mention_guard import MentionGuard
from settings_manager import BotSettings

# تحميل الإعدادات من BotSettings
bot_settings = BotSettings()
settings = bot_settings.get_all_settings()

channels = settings.get("channels", [])
if not channels:
    raise ValueError("ما فيه ولا قناة مضافة! ضيفي قناة من لوحة التحكم.")

bot_username = settings["bot_username"]
access_token = settings["access_token"]

# تهيئة الحارس
mention_guard = MentionGuard()
mention_guard.set_config(
    settings.get("mention_guard_limit", 2),
    settings.get("mention_guard_duration", 5),
    settings.get("mention_guard_cooldown", 86400),
    settings.get("mention_guard_warning_thresh", 1),
    settings.get("mention_guard_warn_msg", "ترى ببلعك تايم آوت"),
    settings.get("mention_guard_timeout_msg", "القم! أنا حذرتك")
)

class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=access_token, prefix="!", initial_channels=channels)
        self.engine = WiduxEngine(self)

    async def event_ready(self):
        print(f"{bot_username} is connected to Twitch!")

    async def event_message(self, message):
        if message.echo:
            return

        # الرد على منشن البوت
        if f"@{bot_username.lower()}" in message.content.lower():
            response = mention_guard.handle_mention(message.author.name)
            print("Mention Response:", response)
            if response["action"] in ["warn", "roast"]:
                await message.channel.send(response["message"])
            elif response["action"] == "timeout":
                await message.channel.send(f"/timeout {message.author.name} {response['duration']} {response['message']}")
            return

        # أمر تجربة يدوي
        if message.content.strip() == "!تجربة":
            await message.channel.send("تمت التجربة بنجاح يا أسطورة!")
            return

        await self.engine.handle_message(message)
        await self.handle_commands(message)

bot = TwitchBot()
