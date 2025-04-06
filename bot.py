import asyncio
import random
import time
from twitchio.ext import commands
from config import TWITCH_TOKEN, TWITCH_CLIENT_ID, TWITCH_CHANNEL, DEFAULT_MENTION_RESPONSES
from game_manager import GameManager
from question_handler import QuestionHandler
from models import db, UserMentionTracker, MentionSetting, CustomMentionResponse

class TriviaBot(commands.Bot):
    def __init__(self):
        # Initialize our Bot with our token, prefix and a list of channels to join on boot
        # Use list() to ensure we have a valid list even if TWITCH_CHANNEL is None
        initial_channels = [TWITCH_CHANNEL] if TWITCH_CHANNEL else []
        
        super().__init__(
            token=TWITCH_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            prefix="!",
            initial_channels=initial_channels
        )
        
        self.game_manager = GameManager(self)
        self.question_handler = QuestionHandler()
        
    def join_channels(self, channel_list):
        """Join one or more Twitch channels
        
        Args:
            channel_list (list): List of channel names to join
        """
        if not channel_list:
            return
            
        # This is a sync method, but we need to call async methods
        # We'll use asyncio.run_coroutine_threadsafe if we have a running loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a task to join the channels
            async def join_task():
                for channel in channel_list:
                    # Remove # prefix if present to avoid ##channel
                    channel = channel.lstrip('#')
                    channel = f'#{channel}'
                    
                    print(f"Joining channel: {channel}")
                    try:
                        # Use the proper twitchio method
                        await self._connection.join_channels([channel])
                        print(f"Successfully joined {channel}")
                    except Exception as e:
                        print(f"Error joining {channel}: {e}")
                        
            asyncio.run_coroutine_threadsafe(join_task(), loop)
            return True
        else:
            print("Error: No running event loop found.")
            return False

    async def event_ready(self):
        """Called once when the bot connects to Twitch"""
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        """Called every time a message is sent to the channel"""
        # Ignore messages from the bot
        if message.echo:
            return
        
        # Check for bot mentions
        if self.nick.lower() in message.content.lower() or f'@{self.nick.lower()}' in message.content.lower():
            await self.handle_mention(message)
            
        # Check for command triggers
        if message.content.lower() == "وج؟":
            await self.handle_game_start(message.channel)
        
        # Process commands
        await self.handle_commands(message)
        
    async def handle_mention(self, message):
        """Handle mentions of the bot"""
        # Get settings from database
        from flask import current_app
        with current_app.app_context():
            # Get the mention settings
            settings = MentionSetting.query.first()
            if not settings:
                settings = MentionSetting()  # Use defaults
                
            # Get or create user mention tracker
            tracker = UserMentionTracker.query.filter_by(username=message.author.name).first()
            if not tracker:
                tracker = UserMentionTracker(username=message.author.name)
                db.session.add(tracker)
                
            # Check for custom response for this user
            custom_response = CustomMentionResponse.query.filter_by(
                username=message.author.name, 
                active=True
            ).first()
                
            # Increment mention count
            count = tracker.increment()
            
            # Check if we should timeout
            if count >= settings.max_mentions and tracker.can_timeout_again(settings.global_cooldown):
                # Apply timeout
                tracker.set_timeout()
                db.session.commit()
                
                # Send timeout message
                timeout_msg = settings.timeout_message.format(
                    username=message.author.name,
                    count=count,
                    timeout=settings.timeout_duration,
                    max_mentions=settings.max_mentions
                )
                await message.channel.send(timeout_msg)
                
                # Apply the timeout (if supported by the channel)
                try:
                    await message.channel.timeout(message.author.name, settings.timeout_duration)
                except Exception as e:
                    print(f"Error applying timeout: {e}")
                    
                # After timeout duration, reset the counter
                # Note: This doesn't block execution
                asyncio.create_task(self._reset_mention_count_after_timeout(
                    message.author.name, 
                    settings.timeout_duration
                ))
            
            # Check if we should show warning
            elif count == settings.warning_threshold:
                # Send warning message
                warning_msg = settings.warning_message.format(
                    username=message.author.name,
                    count=count,
                    max_mentions=settings.max_mentions
                )
                await message.channel.send(warning_msg)
                
            else:
                # Send normal response
                if custom_response:
                    # Send custom response for this user
                    await message.channel.send(custom_response.response)
                else:
                    # Send random default response
                    response = random.choice(DEFAULT_MENTION_RESPONSES)
                    await message.channel.send(response)
                    
            # Commit changes to the database
            db.session.commit()
            
    async def _reset_mention_count_after_timeout(self, username, timeout_duration):
        """Reset mention count after timeout period"""
        await asyncio.sleep(timeout_duration)
        
        # Use app context for database access
        from flask import current_app
        with current_app.app_context():
            tracker = UserMentionTracker.query.filter_by(username=username).first()
            if tracker:
                tracker.reset()
                db.session.commit()

    async def handle_game_start(self, ctx):
        """Handle the game start command"""
        await ctx.send("هلا والله! إذا بتلعب لحالك اكتب 'فردي' إذا ضد فريق اكتب 'تحدي' وإذا فريقين اكتب 'تيم'.")
    
    @commands.command(name="فردي")
    async def solo_mode(self, ctx):
        """Start a solo game mode"""
        success = await self.game_manager.start_game(ctx, "فردي")
        if success:
            await self.run_game(ctx)
    
    @commands.command(name="تحدي")
    async def challenge_mode(self, ctx):
        """Start a challenge game mode"""
        success = await self.game_manager.start_game(ctx, "تحدي")
        if success:
            await self.run_game(ctx)
    
    @commands.command(name="تيم")
    async def team_mode(self, ctx):
        """Start a team game mode"""
        success = await self.game_manager.start_game(ctx, "تيم")
        if success:
            await self.run_game(ctx)
    
    @commands.command(name="توقف")
    async def stop_game(self, ctx):
        """Stop the current game"""
        await self.game_manager.end_game(ctx)
    
    async def run_game(self, ctx):
        """Run the game based on the current game mode"""
        game_state = self.game_manager.state
        
        await ctx.send("🎮 بدأت اللعبة! 🎮")
        await ctx.send(f"لديكم {game_state.question_count} أسئلة عادية متبوعة بأسئلة خاصة")
        
        # Regular questions phase
        for question_num in range(1, game_state.question_count + 1):
            if not game_state.game_active:
                break
            
            await ctx.send(f"🧩 السؤال {question_num}/{game_state.question_count} 🧩")
            question_data = self.question_handler.get_next_question()
            
            player_name, points, answer_time = await self.question_handler.wait_for_answer(self, ctx, question_data, game_state)
            
            if player_name:
                # Display special message based on answer time
                if answer_time <= 5:
                    await ctx.send(f"إجابة سريعة خلال {answer_time:.1f} ثوانٍ! {player_name} حصل على {points} نقاط!")
                else:
                    await ctx.send(f"إجابة صحيحة خلال {answer_time:.1f} ثوانٍ. {player_name} حصل على {points} نقاط.")
                # Update player points based on the game mode
                if game_state.game_mode == "فردي" or game_state.game_mode == "تحدي":
                    game_state.player_points[player_name] = game_state.player_points.get(player_name, 0) + points
                    
                    # Check for consecutive answers bonus
                    has_bonus, streak_count, bonus_points = self.game_manager.update_consecutive_correct(player_name, True)
                    if has_bonus:
                        if streak_count == 3:
                            await ctx.send(f"وااااو! ستريك 3 ، {player_name} +{bonus_points} نقاط إضافية لك!")
                        elif streak_count == 6:
                            await ctx.send(f"رهيييب! ستريك 6 ، {player_name} +{bonus_points} نقاط إضافية لك!")
                        elif streak_count == 10:
                            await ctx.send(f"أسطووورة! ستريك 10 ، {player_name} +{bonus_points} نقاط إضافية لك!")
                
                elif game_state.game_mode == "تيم":
                    # إضافة تتبع النقاط الفردية للاعبين في التيم
                    if 'player_individual_points' not in game_state.__dict__:
                        game_state.player_individual_points = {}
                    
                    if player_name in game_state.red_team:
                        # إضافة النقاط لفريق الأحمر
                        game_state.red_team_points += points
                        # تتبع النقاط الفردية للاعب
                        game_state.player_individual_points[player_name] = game_state.player_individual_points.get(player_name, 0) + points
                        
                        # عرض نقاط الفريق والنقاط الفردية
                        await ctx.send(f"الفريق الأحمر: +{points} نقاط")
                        await ctx.send(f"{player_name} لديه الآن {game_state.player_individual_points[player_name]} نقطة فردية")
                        
                        # Track streak for individual players in team mode
                        has_bonus, streak_count, _ = self.game_manager.update_consecutive_correct(player_name, True)
                        if has_bonus:
                            await ctx.send(f"ستريك {streak_count} ل {player_name}! الفريق الأحمر فخور بك!")
                            
                    elif player_name in game_state.blue_team:
                        # إضافة النقاط لفريق الأزرق
                        game_state.blue_team_points += points
                        # تتبع النقاط الفردية للاعب
                        game_state.player_individual_points[player_name] = game_state.player_individual_points.get(player_name, 0) + points
                        
                        # عرض نقاط الفريق والنقاط الفردية
                        await ctx.send(f"الفريق الأزرق: +{points} نقاط")
                        await ctx.send(f"{player_name} لديه الآن {game_state.player_individual_points[player_name]} نقطة فردية")
                        
                        # Track streak for individual players in team mode
                        has_bonus, streak_count, _ = self.game_manager.update_consecutive_correct(player_name, True)
                        if has_bonus:
                            await ctx.send(f"ستريك {streak_count} ل {player_name}! الفريق الأزرق فخور بك!")
            
            # Short delay between questions
            await asyncio.sleep(2)
        
        # Special question phase
        if game_state.game_active:
            # Golden Question
            await self.question_handler.handle_golden_question(self, ctx, game_state)
            await asyncio.sleep(2)
            
            # Test of Fate
            await self.question_handler.handle_test_of_fate(self, ctx, game_state)
            await asyncio.sleep(2)
            
            # Steal Question
            if game_state.game_mode in ["تحدي", "تيم"]:
                await self.question_handler.handle_steal_question(self, ctx, game_state)
                await asyncio.sleep(2)
            
            # Sabotage Question (for team mode only)
            if game_state.game_mode == "تيم":
                await self.question_handler.handle_sabotage_question(self, ctx, game_state)
                await asyncio.sleep(2)
            
            # Doom Question (for team mode only)
            if game_state.game_mode == "تيم" and not game_state.game_over:
                await self.question_handler.handle_doom_question(self, ctx, game_state)
                await asyncio.sleep(2)
                
            # التحقق من حالة انتهاء اللعبة بعد سؤال الدوم
            if game_state.game_over:
                # اللعبة انتهت بالفعل بسبب سؤال الدوم وتم تحديد الفريق الفائز
                if game_state.winning_team == "red":
                    await ctx.send("🏆 انتهت اللعبة! الفريق الأحمر هو الفائز! 🏆")
                elif game_state.winning_team == "blue":
                    await ctx.send("🏆 انتهت اللعبة! الفريق الأزرق هو الفائز! 🏆")
            else:
                # إنهاء اللعبة بالطريقة العادية إذا لم تنته بسبب سؤال الدوم
                await self.game_manager.end_game(ctx)
