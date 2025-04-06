import logging
import asyncio
import random
import re
import time
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict
from twitchio.ext import commands
from config import TWITCH_TMI_TOKEN, TWITCH_BOT_USERNAME, TWITCH_CLIENT_ID
from models import Channel, Question, GameSession, Player
from app import db
from game import GameManager

# Set up logging
logger = logging.getLogger(__name__)

class WiduxBot(commands.Bot):
    def __init__(self, channels):
        # Verify token is in the correct format
        token = TWITCH_TMI_TOKEN
        
        # Check if token is available
        if not token:
            logger.error("TWITCH_TMI_TOKEN is not set. Bot cannot connect to Twitch.")
            raise ValueError("TWITCH_TMI_TOKEN is missing. Please set this environment variable.")
            
        # Add oauth: prefix if not present
        if not token.startswith('oauth:'):
            token = f'oauth:{token}'
            
        # Check if client_id is available
        if not TWITCH_CLIENT_ID:
            logger.warning("TWITCH_CLIENT_ID is not set. Some functionality may be limited.")
            
        # Check if bot username is available
        bot_username = TWITCH_BOT_USERNAME or "WiduxBot"
        
        logger.debug(f"Initializing bot with username: {bot_username} for channels: {channels}")
        
        super().__init__(
            token=token,
            prefix='!',
            initial_channels=channels,
            nick=bot_username,
            client_id=TWITCH_CLIENT_ID
        )
        self.game_managers = {}  # Map channel names to GameManager instances
        self.is_running = True
    
    async def event_ready(self):
        """Called once when the bot goes online."""
        logger.info(f"{TWITCH_BOT_USERNAME} is online! Connected to: {', '.join(self.initial_channels)}")
        
        # Initialize game managers for each channel
        for channel_name in self.initial_channels:
            self.game_managers[channel_name] = GameManager(self, channel_name)
    
    async def event_message(self, message):
        """Run every time a message is sent in chat."""
        # Ignore messages from the bot itself
        if message.echo:
            return
        
        # Get channel name and content
        channel_name = message.channel.name
        content = message.content.strip()
        
        # Log message for debugging
        logger.info(f"Received message in channel {channel_name}: {content}")
        
        # Check for game trigger phrase
        if content == 'وج؟':
            logger.info(f"Game trigger detected from {message.author.name} in channel {channel_name}")
            await self.handle_game_start(message)
            return  # Return here to avoid processing the same message elsewhere
        
        # Check for game mode selection if a game manager exists
        if channel_name in self.game_managers and self.game_managers[channel_name].waiting_for_mode:
            if content in ['فردي', 'تحدي', 'تيم']:
                logger.info(f"Mode selection detected: {content}")
                # Pass directly to the game manager
                await self.game_managers[channel_name].process_message(message)
                return  # Return to avoid further processing
                
        try:
            # Process commands
            await self.handle_commands(message)
            
            # Pass message to the appropriate game manager if exists
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
            logger.info(f"Game start trigger received from {message.author.name} in channel {channel_name}")
            
            # Create or get the game manager for this channel
            if channel_name not in self.game_managers:
                logger.info(f"Creating new GameManager for channel {channel_name}")
                self.game_managers[channel_name] = GameManager(self, channel_name)
            
            game_manager = self.game_managers[channel_name]
            
            # Check if a game is already running
            if game_manager.is_game_active():
                logger.warning(f"Game is already active in channel {channel_name}")
                await message.channel.send("هناك لعبة قائمة بالفعل! انتظر حتى تنتهي أو اكتب '!resetgame' إذا كنت مشرفًا لإعادة تعيين اللعبة.")
                return
                
            # Set waiting for mode flag
            game_manager.set_waiting_for_mode(True)
            logger.info(f"Set waiting_for_mode to True for channel {channel_name}")
            
            # Send welcome message
            welcome_msg = "هلا والله! إذا بتلعب لحالك اكتب 'فردي' إذا ضد فريق اكتب 'تحدي' وإذا فريقين اكتب 'تيم'."
            await message.channel.send(welcome_msg)
            logger.info(f"Sent welcome message in channel {channel_name}: {welcome_msg}")
            
        except Exception as e:
            logger.error(f"Error in handle_game_start: {str(e)}")
            await message.channel.send("حدث خطأ أثناء بدء اللعبة. الرجاء المحاولة مرة أخرى.")
            logger.warning(f"Game is already active in channel {channel_name}")
            await message.channel.send("هناك لعبة قائمة بالفعل! انتظر حتى تنتهي أو اكتب '!resetgame' إذا كنت مشرفًا لإعادة تعيين اللعبة.")
            return
        
        # Set waiting for mode flag
        game_manager.set_waiting_for_mode(True)
        logger.info(f"Set waiting_for_mode to True for channel {channel_name}")
        
        # Send welcome message
        welcome_msg = "هلا والله! إذا بتلعب لحالك اكتب 'فردي' إذا ضد فريق اكتب 'تحدي' وإذا فريقين اكتب 'تيم'."
        await message.channel.send(welcome_msg)
        logger.info(f"Sent welcome message in channel {channel_name}: {welcome_msg}")
        
        # Wait for game mode selection
        game_manager.set_waiting_for_mode(True)
    
    @commands.command(name='stop')
    async def command_stop(self, ctx):
        """Stop the currently running game"""
        channel_name = ctx.channel.name
        
        # Check for moderator privileges
        if not ctx.author.is_mod and ctx.author.name != channel_name:
            await ctx.send(f"@{ctx.author.name} فقط المشرفين وصاحب القناة يمكنهم إيقاف اللعبة.")
            return
        
        if channel_name in self.game_managers:
            game_manager = self.game_managers[channel_name]
            if game_manager.is_game_active():
                await game_manager.end_game()
                await ctx.send("تم إيقاف اللعبة.")
            else:
                await ctx.send("لا توجد لعبة قائمة حالياً.")
        else:
            await ctx.send("لا توجد لعبة قائمة حالياً.")
    
    @commands.command(name='help')
    async def command_help(self, ctx):
        """Display help message"""
        await ctx.send("لبدء لعبة، اكتب 'وج؟' في الدردشة. البوت سيرشدك خلال عملية اللعب. "
                      "المشرفين يمكنهم استخدام الأمر !stop لإيقاف اللعبة.")
                      
    @commands.command(name='resetgame')
    async def command_resetgame(self, ctx):
        """Reset the game state"""
        channel_name = ctx.channel.name
        
        # التحقق من صلاحيات المشرف
        if not ctx.author.is_mod and ctx.author.name != channel_name:
            await ctx.send(f"@{ctx.author.name} فقط المشرفين وصاحب القناة يمكنهم إعادة تعيين اللعبة.")
            return
        
        if channel_name in self.game_managers:
            self.game_managers[channel_name] = GameManager(self, channel_name)
            await ctx.send("تم إعادة تعيين حالة اللعبة. يمكنك الآن بدء لعبة جديدة بكتابة 'وج؟'")
        else:
            self.game_managers[channel_name] = GameManager(self, channel_name)
            await ctx.send("تم إعادة تعيين حالة اللعبة.")
    
    def close(self):
        """Cleanly shut down the bot"""
        self.is_running = False
        logger.info("Bot shutdown initiated")
        # Cleanup any active games
        for channel_name, game_manager in self.game_managers.items():
            if game_manager.is_game_active():
                asyncio.create_task(game_manager.end_game())
        
        # Close the bot connection
        super().close()

def create_bot_instance(channels: List[str]) -> WiduxBot:
    """Create and return a new bot instance"""
    return WiduxBot(channels)
