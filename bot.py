import os
import asyncio
import logging
from twitchio.ext import commands
from app import config
from game import Game, GameMode
from questions import load_default_questions, get_random_question

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Dictionary to store active games per channel
active_games = {}

class WajBot(commands.Bot):
    def __init__(self):
        # Initialize with token from config
        super().__init__(
            token=config.token,
            client_id=config.client_id,
            nick='WiduxBot',
            prefix='!',
            initial_channels=config.active_channels
        )
        self.questions = load_default_questions()
        logger.info(f"Bot initialized with {len(self.questions)} questions")

    async def event_ready(self):
        """Called once when the bot connects to Twitch"""
        logger.info(f'Logged in as | {self.nick}')
        logger.info(f'Connected to channels: {", ".join(config.active_channels)}')

    async def event_message(self, message):
        """Run whenever a message is sent in chat"""
        # Ignore messages from the bot itself
        if message.echo:
            return

        logger.debug(f"Received message: {message.content} from {message.author.name} in {message.channel.name}")

        # Process commands like !help
        await self.handle_commands(message)
        
        # Handle game-specific messages
        channel_name = message.channel.name.lower()
        
        # Starting the game with "وج؟"
        if message.content.strip() == "وج؟":
            logger.info(f"Game start command detected in {channel_name}")
            if channel_name not in active_games:
                await message.channel.send(config.custom_messages['welcome_message'])
            else:
                await message.channel.send("هناك لعبة جارية بالفعل. انتظر حتى تنتهي.")
        
        # Handle game mode selection
        elif message.content in ["اتحداك", "تحدي", "تيم"]:
            if channel_name not in active_games:
                game_mode = None
                if message.content == "اتحداك":
                    game_mode = GameMode.SOLO
                elif message.content == "تحدي":
                    game_mode = GameMode.GROUP
                elif message.content == "تيم":
                    game_mode = GameMode.TEAM
                
                logger.debug(f"Creating new game in channel {channel_name} with mode {game_mode}")
                active_games[channel_name] = Game(message.channel, game_mode)
                await active_games[channel_name].start_registration()
            elif channel_name in active_games and not active_games[channel_name].is_active:
                # إذا كانت اللعبة موجودة ولكن غير نشطة، فقم بإزالتها وبدء لعبة جديدة
                logger.debug(f"Removing inactive game in channel {channel_name} and starting new one")
                del active_games[channel_name]
                
                game_mode = None
                if message.content == "اتحداك":
                    game_mode = GameMode.SOLO
                elif message.content == "تحدي":
                    game_mode = GameMode.GROUP
                elif message.content == "تيم":
                    game_mode = GameMode.TEAM
                
                active_games[channel_name] = Game(message.channel, game_mode)
                await active_games[channel_name].start_registration()
            else:
                await message.channel.send("هناك لعبة جارية بالفعل. انتظر حتى تنتهي.")
        
        # Process game input if a game is active in this channel
        elif channel_name in active_games and active_games[channel_name].is_active:
            await active_games[channel_name].process_message(message)

    @commands.command(name="help")
    async def help_command(self, ctx):
        """Display help information about the bot"""
        await ctx.send("مرحبا! أنا WiduxBot لألعاب وج؟. اكتب 'وج؟' لبدء لعبة جديدة ثم اختر وضع اللعب المناسب.")

    @commands.command(name="stop")
    async def stop_command(self, ctx):
        """Stop the current game in the channel"""
        channel_name = ctx.channel.name.lower()
        if channel_name in active_games and active_games[channel_name].is_active:
            logger.debug(f"Stop command issued for channel {channel_name}")
            await active_games[channel_name].end_game("تم إيقاف اللعبة بواسطة المشرف.")
            # Game will remove itself from active_games dictionary
            await ctx.send("تم إيقاف اللعبة.")
        else:
            await ctx.send("لا توجد لعبة نشطة لإيقافها.")

    @commands.command(name="addquestion")
    async def add_question(self, ctx, *, question_data):
        """Add a new question to the question bank (moderator only)"""
        # Simple way to check if user is a mod or broadcaster
        if not ctx.author.is_mod and not ctx.author.is_broadcaster:
            await ctx.send("فقط المشرفون يمكنهم إضافة أسئلة.")
            return
        
        try:
            # Expected format: question|answer|category
            parts = question_data.split('|')
            if len(parts) < 2:
                await ctx.send("تنسيق غير صحيح. استخدم: !addquestion سؤال|جواب|تصنيف")
                return
            
            question = parts[0].strip()
            answer = parts[1].strip()
            category = parts[2].strip() if len(parts) > 2 else "عام"
            
            # Add to the question bank
            self.questions.append({"question": question, "answer": answer, "category": category})
            await ctx.send(f"تمت إضافة السؤال بنجاح! عدد الأسئلة الآن: {len(self.questions)}")
        except Exception as e:
            await ctx.send(f"خطأ في إضافة السؤال: {str(e)}")

def start_bot():
    """Start the bot"""
    # تهيئة حلقة الأحداث الغير متزامنة في الخيط الحالي
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    bot = WajBot()
    new_loop.run_until_complete(bot.run())

if __name__ == "__main__":
    start_bot()
