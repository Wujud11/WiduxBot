import logging
import asyncio
import random
from collections import defaultdict
from twitchio.ext import commands
from config import TWITCH_TMI_TOKEN, TWITCH_BOT_USERNAME, TWITCH_CLIENT_ID
from models import Channel, Question, GameSession, Player
from game import GameManager

# Set up logging
logger = logging.getLogger(__name__)

class WiduxBot(commands.Bot):
    def __init__(self, channels):
        # Verify token is in the correct format
        token = TWITCH_TMI_TOKEN
        if not token:
            raise ValueError("TWITCH_TMI_TOKEN is missing")
        if not token.startswith('oauth:'):
            token = f'oauth:{token}'

        # Initialize bot
        bot_username = TWITCH_BOT_USERNAME or "WiduxBot"
        super().__init__(
            token=token,
            prefix='!',
            initial_channels=channels,
            nick=bot_username,
            client_id=TWITCH_CLIENT_ID
        )
        self.game_managers = {}
        self.is_running = True
        self._app = None

    @property
    def app(self):
        if not self._app:
            from app import app
            self._app = app
        return self._app

    async def event_ready(self):
        """Called once when the bot goes online."""
        logger.info(f"{self.nick} is online!")
        for channel in self.connected_channels:
            try:
                with self.app.app_context():
                    self.game_managers[channel.name] = GameManager(self, channel.name)
                await channel.send(f"البوت متصل وجاهز للعب! اكتب 'وج؟' لبدء لعبة جديدة.")
            except Exception as e:
                logger.error(f"Error initializing channel {channel.name}: {str(e)}")

    async def event_message(self, message):
        """Run every time a message is sent in chat."""
        if message.echo:
            return

        channel_name = message.channel.name
        content = message.content.strip()
        username = message.author.name

        logger.info(f"Received message in channel {channel_name}: {content}")

        try:
            with self.app.app_context():
                # Check for game trigger phrase
                if content.strip().replace(' ', '') in ['وج؟', 'وج?', 'وج']:
                    await self.handle_game_start(message)
                    return

                # Pass message to game manager if exists
                if channel_name in self.game_managers:
                    logger.info(f"Passing message to game manager in channel {channel_name}")
                    await self.game_managers[channel_name].process_message(message)

        except Exception as e:
            logger.error(f"Error processing message in channel {channel_name}: {str(e)}")
            await message.channel.send("حدث خطأ في معالجة الرسالة. الرجاء المحاولة مرة أخرى.")

    async def handle_game_start(self, message):
        """Handle game start trigger"""
        try:
            channel_name = message.channel.name
            with self.app.app_context():
                if channel_name not in self.game_managers:
                    self.game_managers[channel_name] = GameManager(self, channel_name)

                game_manager = self.game_managers[channel_name]

                if game_manager.is_game_active():
                    await message.channel.send("هناك لعبة قائمة بالفعل! انتظر حتى تنتهي أو اكتب '!resetgame' إذا كنت مشرفًا.")
                    return

                game_manager.set_waiting_for_mode(True)
                await message.channel.send("هلا والله! إذا بتلعب لحالك اكتب 'فردي' إذا ضد فريق اكتب 'تحدي' وإذا فريقين اكتب 'تيم'.")

        except Exception as e:
            logger.error(f"Error in handle_game_start: {str(e)}")
            await message.channel.send("حدث خطأ أثناء بدء اللعبة. الرجاء المحاولة مرة أخرى.")

    def close(self):
        """Cleanly shut down the bot"""
        self.is_running = False
        logger.info("Bot shutdown initiated")
        for channel_name, game_manager in self.game_managers.items():
            if game_manager.is_game_active():
                asyncio.create_task(game_manager.end_game())
        super().close()

def create_bot_instance(channels):
    """Create and return a new bot instance"""
    return WiduxBot(channels)