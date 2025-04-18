import asyncio
from twitchio.ext import commands
from settings_manager import BotSettings
from bot.mention_guard import MentionGuard
from bot.engine import WiduxEngine

# تحميل الإعدادات
settings = BotSettings()
bot_username = settings.get_setting("bot_username")  # <-- عدلناه هنا
access_token = settings.get_setting("access_token")  # <-- وعدلناه هنا

# حماية المنشن
mention_guard = MentionGuard()
mention_guard.set_config(
    limit=settings.get_setting("mention_limit"),
    duration=settings.get_setting("mention_guard_duration"),
    cooldown=settings.get_setting("mention_guard_cooldown"),
    warning_thresh=settings.get_setting("mention_guard_warning_thresh"),
    warn_msg=settings.get_setting("mention_guard_warn_msg"),
    timeout_msg=settings.get_setting("mention_guard_timeout_msg"),
)

# إضافة الردود الخاصة والعامة
mention_guard.general_roasts = settings.get_setting("mention_responses") or []
specials = settings.get_setting("special_responses") or {}
for user, responses in specials.items():
    mention_guard.add_special_responses(user.lower(), responses)

class WiduxBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=access_token,
            prefix="!",
            initial_channels=[]
        )
        self.engine = WiduxEngine(self)
        self.last_channels = set()

    async def event_ready(self):
        print(f">>> البوت جاهز! اسمه: {bot_username}")
        asyncio.create_task(self.sync_channels_loop())

    async def event_message(self, message):
        if message.echo:
            return

        username = message.author.name.lower()

        # تعامل مع المنشن
        if f"@{bot_username.lower()}" in message.content.lower():
            result = mention_guard.handle_mention(username)
            if result["action"] == "warn":
                await message.channel.send(result["message"])
            elif result["action"] == "timeout":
                await message.channel.timeout(username, result["duration"], reason="Spam Mention")
                await message.channel.send(result["message"])
            elif result["action"] == "roast":
                await message.channel.send(result["message"])

        await self.engine.handle_message(message)

    async def sync_channels_loop(self):
        await self.wait_for_ready()
        while True:
            try:
                current = set(settings.get_setting("channels") or [])
                added = current - self.last_channels
                removed = self.last_channels - current

                for channel in added:
                    await self.join_channels([channel])
                    print(f"انضم البوت للقناة: {channel}")

                for channel in removed:
                    await self.part_channels([channel])
                    print(f"خرج البوت من القناة: {channel}")

                self.last_channels = current

            except Exception as e:
                print(f"[خطأ مزامنة القنوات] {e}")

            await asyncio.sleep(30)

if __name__ == "__main__":
    bot = WiduxBot()
    bot.run()
