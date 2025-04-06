import logging
import asyncio
from twitchio.ext import commands
from config import TWITCH_TMI_TOKEN, TWITCH_BOT_USERNAME, TWITCH_CLIENT_ID
from models import Channel, Question, GameSession, Player
from game import GameManager

logger = logging.getLogger(__name__)

class WiduxBot(commands.Bot):
    def __init__(self, channels):
        token = TWITCH_TMI_TOKEN
        if not token:
            raise ValueError("TWITCH_TMI_TOKEN is missing")
        if not token.startswith('oauth:'):
            token = f'oauth:{token}'

        super().__init__(
            token=token,
            prefix='!',
            initial_channels=channels,
            nick=TWITCH_BOT_USERNAME or "WiduxBot",
            client_id=TWITCH_CLIENT_ID
        )
        self.game_managers = {}
        self._app = None
        self._last_triggers = {}  # لتتبع آخر مرة تم فيها تشغيل "وج"

    @property
    def app(self):
        if not self._app:
            from app import app
            self._app = app
        return self._app

    async def event_ready(self):
        logger.info(f"{self.nick} is online!")
        for channel in self.connected_channels:
            try:
                with self.app.app_context():
                    self.game_managers[channel.name] = GameManager(self, channel.name)
            except Exception as e:
                logger.error(f"Error initializing channel {channel.name}: {str(e)}")

    async def event_message(self, message):
        if message.echo:
            return

        channel_name = message.channel.name
        content = message.content.strip()
        username = message.author.name

        # نظام cooldown يدوي (5 ثواني لكل مستخدم)
        now = asyncio.get_event_loop().time()
        last_trigger = self._last_triggers.get(username, 0)
        
        if content.replace(' ', '') in ['وج؟', 'وج?', 'وج']:
            if now - last_trigger < 5:  # إذا لم تمر 5 ثواني منذ آخر طلب
                return
            self._last_triggers[username] = now  # تحديث وقت آخر تشغيل
            
            try:
                with self.app.app_context():
                    if channel_name not in self.game_managers:
                        self.game_managers[channel_name] = GameManager(self, channel.name)

                    game_manager = self.game_managers[channel_name]

                    if game_manager.is_game_active():
                        await message.channel.send("هناك لعبة قائمة بالفعل! انتظر حتى تنتهي أو اكتب '!resetgame' إذا كنت مشرفًا.")
                        return

                    game_manager.set_waiting_for_mode(True)
                    await message.channel.send("هلا والله! إذا بتلعب لحالك اكتب 'فردي' إذا ضد فريق اكتب 'تحدي' وإذا فريقين اكتب 'تيم'.")

            except Exception as e:
                logger.error(f"Error in game start: {str(e)}")
                await message.channel.send("حدث خطأ أثناء بدء اللعبة. الرجاء المحاولة مرة أخرى.")
                return

        # معالجة الرسائل الأخرى للعبة (بدون تعديل)
        try:
            with self.app.app_context():
                if channel_name in self.game_managers:
                    await self.game_managers[channel_name].process_message(message)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    def close(self):
        self.is_running = False
        logger.info("Bot shutdown initiated")
        for channel_name, game_manager in self.game_managers.items():
            if game_manager.is_game_active():
                asyncio.create_task(game_manager.end_game())
        super().close()

def create_bot_instance(channels):
    return WiduxBot(channels)