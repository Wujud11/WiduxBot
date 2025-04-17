import asyncio
from twitchio.ext import commands
from settings_manager import BotSettings
from bot.mention_guard import MentionGuard
from engine import WiduxEngine

# تحميل الإعدادات
settings = BotSettings()
bot_username = settings.get_setting("bot_username")
access_token = settings.get_setting("access_token")
channels = settings.get_setting("channels") or []

# تهيئة الحماية من المنشن
mention_guard = MentionGuard()
mention_guard.set_config(
    limit=settings.get_setting("mention_guard_limit"),
    duration=settings.get_setting("mention_guard_duration"),
    cooldown=settings.get_setting("mention_guard_cooldown"),
    warning_thresh=settings.get_setting("mention_guard_warning_thresh"),
    warn_msg=settings.get_setting("mention_guard_warn_msg"),
    timeout_msg=settings.get_setting("mention_guard_timeout_msg"),
)

# تحميل الردود العامة (ردود الطقطقة)
mention_guard.general_roasts = settings.get_setting("mention_responses") or []

# تحميل الردود الخاصة وتسجيلها
special = settings.get_setting("special_responses") or {}
for user, responses in special.items():
    mention_guard.add_special_responses(user, responses)

# كلاس البوت
class WiduxBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=access_token,
            prefix="!",
            initial_channels=channels
        )
        self.engine = WiduxEngine(self)

    async def event_ready(self):
        print(f">>> البوت جاهز! اسمه: {bot_username}")

    async def event_message(self, message):
        if message.echo:
            return

        username = message.author.name.lower()

        # التحقق من منشن البوت
        if f"@{bot_username.lower()}" in message.content.lower():
            result = mention_guard.handle_mention(username)

            if result["action"] == "warn":
                await message.channel.send(result["message"])
            elif result["action"] == "timeout":
                await message.channel.timeout(username, result["duration"], reason="Spam Mention")
                await message.channel.send(result["message"])
            elif result["action"] == "roast":
                await message.channel.send(result["message"])

        # تمرير الرسالة لمحرك اللعبة
        await self.engine.handle_message(message)

# تشغيل البوت
if __name__ == "__main__":
    bot = WiduxBot()
    bot.run()
