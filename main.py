import json
import asyncio
from twitchio.ext import commands
from bot.engine import WiduxEngine
from bot.mention_guard import MentionGuard

# تحميل الإعدادات من ملف json
with open("bot_settings.json", "r", encoding="utf-8") as f:
    settings = json.load(f)

channels = settings.get("channels", [])
if not channels:
    raise ValueError("ما فيه ولا قناة مضافة! ضيفي قناة من لوحة التحكم.")

bot_username = settings["bot_username"]
access_token = settings["access_token"]

# تهيئة الحارس مع القيم المطلوبة
mention_guard = MentionGuard()
mention_guard.set_config(
    settings["mention_guard_limit"],
    settings["mention_guard_duration"],
    settings["mention_guard_cooldown"],
    settings["mention_guard_warning_thresh"],
    settings["mention_guard_warn_msg"],
    settings["mention_guard_timeout_msg"]
)

engine = WiduxEngine()

class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=access_token, prefix="!", initial_channels=channels)

    async def event_ready(self):
        print(f"{bot_username} is connected to Twitch!")

    async def event_message(self, message):
        if message.echo:
            return

        # الرد على منشن البوت
        if message.content.startswith(f"@{bot_username}"):
            response_type, response_text = mention_guard.handle_mention(message.author.name)
            if response_text:
                await message.channel.send(response_text)
            return

        # أمر تجربة يدوي
        if message.content.strip() == "!تجربة":
            await message.channel.send("تمت التجربة بنجاح يا أسطورة!")
            return

        await engine.handle_message(message)
        await self.handle_commands(message)

bot = TwitchBot()

if __name__ == "__main__":
    asyncio.run(bot.run())
