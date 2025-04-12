import json
import asyncio
from twitchio.ext import commands
from bot.engine import WiduxEngine  # تم التعديل هنا
from bot.mention_guard import MentionGuard  # استدعاء النظام

# تحميل الإعدادات من ملف json
with open("bot_settings.json", "r", encoding="utf-8") as f:
    settings = json.load(f)

channels = settings.get("channels", [])
if not channels:
    raise ValueError("ما فيه ولا قناة مضافة! ضيفي قناة من لوحة التحكم.")

bot_username = settings["bot_username"]
access_token = settings["access_token"]

# تهيئة الحارس
mention_guard = MentionGuard()
mention_guard.set_config(settings)

engine = WiduxEngine()

class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=access_token, prefix="!", initial_channels=channels)

    async def event_ready(self):
        print(f"{bot_username} is connected to Twitch!")

    async def event_message(self, message):
        if message.echo:
            return

        # الرد على منشن البوت إذا موجود
        if message.content.startswith(f"@{bot_username}"):
            response_type, response_text = mention_guard.handle_mention(message.author.name)
            if response_text:
                await message.channel.send(response_text)
            return

        await engine.handle_message(message)
        await self.handle_commands(message)  # في حال فيه أوامر تبدأ بـ "!"

bot = TwitchBot()

if __name__ == "__main__":
    asyncio.run(bot.run())
