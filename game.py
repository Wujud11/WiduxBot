import asyncio
import random
import logging
import time
import re
import datetime
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict
from config import QUESTION_TIMER, REGISTRATION_TIMER, TEAM_REGISTRATION_TIMER, LEADER_SELECTION_TIMER, SABOTAGE_SELECTION_TIMER
from models import Channel, Question, GameSession, Player
from app import db

# Set up logging
logger = logging.getLogger(__name__)

class GameManager:
    """Manages a game session in a specific Twitch channel"""

    def __init__(self, bot, channel_name):
        self.bot = bot
        self.channel_name = channel_name
        self.reset_game_state()

    def reset_game_state(self):
        """Reset all game state variables to their defaults"""
        self.active_game: Optional[GameSession] = None
        self.current_question: Optional[Question] = None
        self.question_start_time: float = 0
        self.waiting_for_mode: bool = False
        self.waiting_for_registration: bool = False
        self.waiting_for_question_count: bool = False
        self.question_count_end_time: float = 0
        self.normal_question_count: int = 5  # Default value
        self.registration_end_time: float = 0
        self.waiting_for_leader: bool = False
        self.leader_selection_end_time: float = 0
        self.players: Dict[str, Player] = {}  # username -> Player object
        self.registered_players: Set[str] = set()  # Set of registered usernames
        self.red_team: Set[str] = set()  # Red team usernames
        self.blue_team: Set[str] = set()  # Blue team usernames
        self.red_leader: Optional[str] = None  # Red team leader username
        self.blue_leader: Optional[str] = None  # Blue team leader username
        self.question_queue: List[Question] = []
        self.normal_questions: List[Question] = []
        self.special_questions: Dict[str, Optional[Question]] = {
            'golden': None,
            'fate': None,
            'steal': None,
            'sabotage': None,
            'doom': None
        }
        self.is_golden_question: bool = False
        self.is_doom_question: bool = False
        self.is_steal_question: bool = False
        logger.info(f"Game state reset for channel {self.channel_name}")
        self.is_fate_test: bool = False
        self.is_sabotage_question: bool = False  # Track if this is a sabotage question
        self.waiting_for_doom_decision: bool = False
        self.waiting_for_steal_selection: bool = False
        self.waiting_for_sabotage_selection: bool = False  # Track if waiting for sabotage player selection
        self.sabotage_selection_end_time: float = 0  # End time for sabotage selection period
        self.sabotage_targets: Dict[str, str] = {}  # username -> target username for sabotage
        self.eliminated_players: Set[str] = set()  # Eliminated players set
        self.steal_request: Optional[Dict] = None
        self.consecutive_answers: Dict[str, int] = defaultdict(int)
        self.fate_test_questions_remaining: int = 0
        self.player_scores_before_fate: Dict[str, int] = {}  # For tracking player scores before Test of Fate
        self.team_scores_before_fate: Dict[str, int] = {}  # For tracking team scores before Test of Fate
        self.player_choices: Dict[str, str] = {}  # For storing player choices in steal/boost questions
        self.red_team_accepted_doom: bool = False  # Track if red team accepted doom question
        self.blue_team_accepted_doom: bool = False  # Track if blue team accepted doom question

    def is_game_active(self) -> bool:
        """Check if a game is currently active"""
        return self.active_game is not None or self.waiting_for_mode or self.waiting_for_registration

    def set_waiting_for_mode(self, value: bool):
        """Set the waiting_for_mode flag"""
        self.waiting_for_mode = value

    async def process_message(self, message):
        """Process messages for game-related commands and responses"""
        username = message.author.name
        content = message.content.strip()

        logger.info(f"GameManager processing message from {username}: '{content}'")
        logger.info(f"Current game state - waiting_for_mode: {self.waiting_for_mode}, active_game: {self.active_game}")
        logger.info(f"Current question: {self.current_question.text if self.current_question else 'None'}")
        logger.info(f"Players in game: {list(self.players.keys()) if self.players else 'None'}")
        logger.info(f"Registered players: {list(self.registered_players) if self.registered_players else 'None'}")

        # Skip messages from eliminated players
        if username in self.eliminated_players:
            logger.info(f"Skipping message from eliminated player: {username}")
            return

        # Check for game mode selection
        if self.waiting_for_mode:
            logger.info(f"Routing to handle_mode_selection with message: '{content}'")
            await self.handle_mode_selection(message)
            return

        # Check for registration responses
        if self.waiting_for_registration:
            await self.handle_registration(message)
            return

        # Check for question count selection
        if self.waiting_for_question_count:
            await self.handle_question_count_selection(message)
            return

        # Check for leader selection
        if self.waiting_for_leader:
            await self.handle_leader_selection(message)
            return

        # Check for doom question decision
        if self.waiting_for_doom_decision and self.active_game and self.active_game.mode == 'تيم':
            await self.handle_doom_decision(message)
            return

        # Check for steal question target selection
        if self.waiting_for_steal_selection and self.active_game and self.active_game.mode == 'تيم':
            await self.handle_steal_selection(message)
            return

        # Check for sabotage target selection
        if self.waiting_for_sabotage_selection and self.active_game and (self.active_game.mode == 'تيم' or self.active_game.mode == 'تحدي'):
            await self.handle_sabotage_selection(message)
            return

        # Check for "زرف" or "زود" choices in steal questions
        if self.is_steal_question and self.active_game and content.lower() in ['زرف', 'زود']:
            self.player_choices[username] = content.lower()
            await message.channel.send(f"@{username} اختار {content}!")
            return

        # Check for question answers if there's an active question
        if self.current_question and self.active_game:
            await self.handle_question_answer(message)
            return

    async def handle_mode_selection(self, message):
        """Handle game mode selection"""
        username = message.author.name
        content = message.content.strip()

        logger.info(f"Game mode selection: User {username} selected content: '{content}'")

        if content in ['فردي', 'تحدي', 'تيم']:
            logger.info(f"Valid game mode selected: {content}")
            self.waiting_for_mode = False

            # Send confirmation before starting game
            confirmation = ""
            if content == 'فردي':
                confirmation = f"@{username} تم بدء اللعبة في وضع اللعب الفردي! 🎮"
            elif content == 'تحدي':
                confirmation = f"@{username} تم بدء اللعبة في وضع تحدي المجموعة! 👥"
            elif content == 'تيم':
                confirmation = f"@{username} تم بدء اللعبة في وضع الفرق! 🏆"

            await message.channel.send(confirmation)
            logger.info(f"Sent confirmation message: {confirmation}")

            # Start the appropriate game mode
            await self.start_game(message.channel, content, username)
        else:
            logger.info(f"Invalid game mode: '{content}', expected one of: 'فردي', 'تحدي', 'تيم'")
            await message.channel.send(f"@{username} اختيار غير صالح! الرجاء كتابة 'فردي'، 'تحدي'، أو 'تيم'.")

    async def start_game(self, channel, mode, initiator):
        """Start a new game with the specified mode"""
        logger.info(f"Starting new game with mode: {mode}, initiator: {initiator}")

        from app import app, db

        # Create a new game session in the database
        try:
            with app.app_context():
                db_channel = Channel.query.filter_by(name=self.channel_name).first()
                if not db_channel:
                    # Create channel if it doesn't exist
                    logger.info(f"Creating new channel in database: {self.channel_name}")
                    db_channel = Channel(name=self.channel_name, is_active=True)
                    db.session.add(db_channel)
                    db.session.commit()
                
                # Create new game session
                self.active_game = GameSession(channel_id=db_channel.id, mode=mode, is_active=True)
                db.session.add(self.active_game)
                db.session.commit()
                logger.info(f"Created new game session. ID: {self.active_game.id}, Mode: {mode}")
        except Exception as e:
            logger.error(f"Database error in start_game: {str(e)}")
            await channel.send("حدث خطأ أثناء بدء اللعبة. الرجاء المحاولة مرة أخرى.")
            return

        # Create new game session
        self.active_game = GameSession(channel_id=db_channel.id, mode=mode, is_active=True)
        db.session.add(self.active_game)
        db.session.commit()
        logger.info(f"Created new game session in database. ID: {self.active_game.id}, Mode: {mode}")

        # Reset game state
        self.players = {}
        self.registered_players = set()
        self.red_team = set()
        self.blue_team = set()
        self.red_leader = None
        self.blue_leader = None
        self.question_queue = []
        self.consecutive_answers = defaultdict(int)

        # Handle different game modes
        if mode == 'فردي':
            # Challenge mode - just start the game with the initiator
            player = Player(
                session_id=self.active_game.id,
                username=initiator,
                score=0
            )
            db.session.add(player)
            db.session.commit()

            self.players[initiator] = player
            self.registered_players.add(initiator)

            # Send instructions instead of duplicate message
            await channel.send(f"@{initiator} استعد للأسئلة! سيتم طرح عدة أسئلة عليك في وضع اللعب الفردي. عليك الإجابة على كل سؤال في الوقت المحدد.")
            await self.start_question_sequence(channel)

        elif mode == 'تحدي':
            # Team challenge mode - open registration
            self.waiting_for_registration = True
            self.registration_end_time = time.time() + REGISTRATION_TIMER

            await channel.send(f"تم بدء اللعبة في وضع التحدي الجماعي! للتسجيل اكتب 'R' خلال {REGISTRATION_TIMER} ثانية.")

            # Wait for registration period then start game
            await asyncio.sleep(REGISTRATION_TIMER)
            await self.end_registration(channel)

        elif mode == 'تيم':
            # Team vs team mode - open team registration
            self.waiting_for_registration = True
            self.registration_end_time = time.time() + TEAM_REGISTRATION_TIMER

            await channel.send(f"تم بدء اللعبة في وضع الفرق! للتسجيل في الفريق الأحمر اكتب 'أحمر' وللفريق الأزرق اكتب 'أزرق' خلال {TEAM_REGISTRATION_TIMER} ثانية.")

            # Wait for registration period then start leader selection
            await asyncio.sleep(TEAM_REGISTRATION_TIMER)
            await self.end_team_registration(channel)

    async def handle_registration(self, message):
        """Handle player registration for game modes"""
        username = message.author.name
        content = message.content.strip().lower()
        game_mode = self.active_game.mode if self.active_game else None

        # Check if registration is still open
        if time.time() > self.registration_end_time:
            return

        if game_mode == 'تحدي' and content == 'r':
            # Register player for team challenge mode
            if username not in self.registered_players:
                player = Player(
                    session_id=self.active_game.id,
                    username=username,
                    score=0
                )
                db.session.add(player)
                db.session.commit()

                self.players[username] = player
                self.registered_players.add(username)

                await message.channel.send(f"@{username} تم تسجيلك في اللعبة!")

        elif game_mode == 'تيم':
            # Register player for team vs team mode
            if content == 'أحمر' and username not in self.registered_players:
                player = Player(
                    session_id=self.active_game.id,
                    username=username,
                    team='أحمر',
                    score=0
                )
                db.session.add(player)
                db.session.commit()

                self.players[username] = player
                self.registered_players.add(username)
                self.red_team.add(username)

                await message.channel.send(f"@{username} تم تسجيلك في الفريق الأحمر!")

            elif content == 'أزرق' and username not in self.registered_players:
                player = Player(
                    session_id=self.active_game.id,
                    username=username,
                    team='أزرق',
                    score=0
                )
                db.session.add(player)
                db.session.commit()

                self.players[username] = player
                self.registered_players.add(username)
                self.blue_team.add(username)

                await message.channel.send(f"@{username} تم تسجيلك في الفريق الأزرق!")

    async def end_registration(self, channel):
        """End the registration period for team challenge mode"""
        self.waiting_for_registration = False

        # Check if there are enough registered players (at least 2)
        if len(self.registered_players) < 2:
            await channel.send("لم يسجل عدد كافٍ من اللاعبين! يجب أن يكون هناك لاعبين على الأقل. تم إلغاء اللعبة.")
            await self.end_game()
            return

        await channel.send(f"انتهت فترة التسجيل! تم تسجيل {len(self.registered_players)} لاعب.")
        player_list = ", ".join([f"@{username}" for username in self.registered_players])
        await channel.send(f"اللاعبون المسجلون: {player_list}")

        # Start the game
        await self.start_question_sequence(channel)

    async def end_team_registration(self, channel):
        """End the team registration period for team vs team mode"""
        self.waiting_for_registration = False

        # Check if there are enough players in each team (at least 3 per team)
        if len(self.red_team) < 3 or len(self.blue_team) < 3:
            await channel.send("لا يوجد عدد كافٍ من اللاعبين في أحد الفرق! يجب أن يكون هناك 3 لاعبين على الأقل في كل فريق. تم إلغاء اللعبة.")
            await self.end_game()
            return

        # Start leader selection
        self.waiting_for_leader = True
        self.leader_selection_end_time = time.time() + LEADER_SELECTION_TIMER

        red_team_list = ", ".join([f"@{username}" for username in self.red_team])
        blue_team_list = ", ".join([f"@{username}" for username in self.blue_team])

        await channel.send(f"انتهت فترة التسجيل! الفريق الأحمر: {red_team_list}")
        await channel.send(f"الفريق الأزرق: {blue_team_list}")
        await channel.send(f"الآن اختاروا قائد لكل فريق! اكتبوا اسم اللاعب بالطريقة التالية '@اسم_اللاعب' خلال {LEADER_SELECTION_TIMER} ثانية.")

        # Wait for leader selection period then start game
        await asyncio.sleep(LEADER_SELECTION_TIMER)
        await self.end_leader_selection(channel)

    async def handle_leader_selection(self, message):
        """Handle leader selection for team vs team mode"""
        username = message.author.name
        content = message.content.strip()

        # Check if leader selection is still open
        if time.time() > self.leader_selection_end_time:
            return

        # Check for '@username' format
        match = re.match(r'@(\w+)', content)
        if not match:
            return

        nominated_player = match.group(1).lower()

        # Check if nominated player is in the appropriate team
        if username in self.red_team and nominated_player in self.red_team and not self.red_leader:
            self.red_leader = nominated_player
            # Update player as leader in database
            player = self.players[nominated_player]
            player.is_leader = True
            db.session.commit()

            await message.channel.send(f"@{nominated_player} تم اختياره كقائد للفريق الأحمر!")

        elif username in self.blue_team and nominated_player in self.blue_team and not self.blue_leader:
            self.blue_leader = nominated_player
            # Update player as leader in database
            player = self.players[nominated_player]
            player.is_leader = True
            db.session.commit()

            await message.channel.send(f"@{nominated_player} تم اختياره كقائد للفريق الأزرق!")

    async def end_leader_selection(self, channel):
        """End the leader selection period and start the game"""
        self.waiting_for_leader = False

        # Choose random leaders if not selected
        if not self.red_leader and self.red_team:
            self.red_leader = random.choice(list(self.red_team))
            # Update player as leader in database
            player = self.players[self.red_leader]
            player.is_leader = True
            db.session.commit()

            await channel.send(f"@{self.red_leader} تم اختياره عشوائياً كقائد للفريق الأحمر!")

        if not self.blue_leader and self.blue_team:
            self.blue_leader = random.choice(list(self.blue_team))
            # Update player as leader in database
            player = self.players[self.blue_leader]
            player.is_leader = True
            db.session.commit()

            await channel.send(f"@{self.blue_leader} تم اختياره عشوائياً كقائد للفريق الأزرق!")

        # Start the game
        await channel.send("بدأت المباراة! استعدوا للأسئلة.")
        await self.start_question_sequence(channel)

    async def start_question_sequence(self, channel):
        """Start the sequence of questions for the game"""
        # Ask the initiator to specify the number of normal questions
        self.waiting_for_question_count = True
        self.question_count_end_time = time.time() + 30  # 30 seconds to choose

        if self.active_game and self.active_game.mode == 'تيم':
            initiator = list(self.registered_players)[0]  # First player who started the game
            max_questions = 10
        else:  # 'تحدي' or 'فردي'
            initiator = list(self.registered_players)[0]
            max_questions = 20

        await channel.send(f"@{initiator} يرجى تحديد عدد الأسئلة العادية (5-{max_questions}). اكتب الرقم فقط في الدردشة.")

    async def handle_question_count_selection(self, message):
        """Handle the selection of question count"""
        username = message.author.name
        content = message.content.strip()

        # Check if question count selection is still open
        if time.time() > self.question_count_end_time:
            return

        # Check if the message is from the game initiator
        if username != list(self.registered_players)[0]:
            return

        # Check if the content is a valid number
        try:
            question_count = int(content)
            max_questions = 10 if self.active_game and self.active_game.mode == 'تيم' else 20

            if 5 <= question_count <= max_questions:
                self.waiting_for_question_count = False
                self.normal_question_count = question_count

                await message.channel.send(f"تم تحديد عدد الأسئلة العادية: {question_count}")

                # Load and organize questions
                await self.load_and_organize_questions(message.channel)
            else:
                await message.channel.send(f"@{username} الرقم غير صالح. يرجى اختيار رقم بين 5 و {max_questions}.")
        except ValueError:
            await message.channel.send(f"@{username} يرجى إدخال رقم صحيح فقط.")

    async def load_and_organize_questions(self, channel):
        """Load and organize questions in a specific sequence according to the specified order"""
        self.question_queue = []

        # Load questions from database
        await self.load_questions()

        # Log the question loading process
        logger.info(f"Organizing questions for game mode: {self.active_game.mode if self.active_game else 'unknown'}")
        logger.info(f"Total questions loaded: {len(self.all_questions)}")

        # Organize questions in specific sequence
        # 1. Normal questions
        # 2. Golden question
        # 3. Test of Fate (5 questions)
        # 4. Steal question
        # 5. Sabotage question
        # 6. Doom question
        normal_questions = [q for q in self.all_questions if q.question_type == 'normal']
        max_questions = MAX_QUESTIONS_TEAM if self.active_game.mode == 'تيم' else MAX_QUESTIONS_SOLO
        golden_questions = [q for q in self.all_questions if q.question_type == 'golden']
        fate_questions = [q for q in self.all_questions if q.question_type == 'normal']  # Use normal questions for fate test
        steal_questions = [q for q in self.all_questions if q.question_type == 'steal']
        sabotage_questions = [q for q in self.all_questions if q.question_type == 'normal']  # Use normal questions for sabotage
        doom_questions = [q for q in self.all_questions if q.question_type == 'doom']

        # Log available questions by type
        logger.info(f"Normal questions: {len(normal_questions)}")
        logger.info(f"Golden questions: {len(golden_questions)}")
        logger.info(f"Steal questions: {len(steal_questions)}")
        logger.info(f"Doom questions: {len(doom_questions)}")

        # 1. First - normal questions (always include)
        max_questions = 15 if self.active_game and self.active_game.mode == 'تيم' else 20

        # Make sure we don't run out of normal questions
        if len(normal_questions) < self.normal_question_count:
            self.normal_question_count = max(5, len(normal_questions))
            logger.warning(f"Not enough normal questions, reducing count to {self.normal_question_count}")
            await channel.send(f"تم تعديل عدد الأسئلة العادية إلى {self.normal_question_count} بسبب محدودية الأسئلة المتوفرة.")

        # Select random normal questions
        selected_normal = random.sample(normal_questions, self.normal_question_count)
        self.question_queue.extend(selected_normal)
        logger.info(f"Added {len(selected_normal)} normal questions to queue")

        # 2. Golden question (always include)
        if golden_questions:
            golden_q = random.choice(golden_questions)
            self.question_queue.append(golden_q)
            logger.info(f"Added golden question: {golden_q.text}")
        else:
            # If no golden questions, use a normal question
            if normal_questions:
                fallback_golden = random.choice(normal_questions)
                self.question_queue.append(fallback_golden)
                logger.info(f"No golden questions available, using normal question instead: {fallback_golden.text}")
            else:
                logger.error("No questions available for golden question!")

        # 3. Test of Fate (5 questions) - only for تيم and تحدي modes
        if self.active_game and self.active_game.mode in ['تيم', 'تحدي']:
            # Use 5 random normal questions for Fate Test
            fate_count = min(5, len(fate_questions))
            if fate_count > 0:
                self.fate_test_questions_remaining = fate_count
                selected_fate = random.sample(fate_questions, fate_count)
                for q in selected_fate:
                    q.question_type = "fate"  # Mark as fate question
                self.question_queue.extend(selected_fate)
                logger.info(f"Added {fate_count} fate test questions")

        # 4. Steal question (always include)
        if steal_questions:
            steal_q = random.choice(steal_questions)
            self.question_queue.append(steal_q)
            logger.info(f"Added steal question: {steal_q.text}")
        else:
            # If no steal questions, use a normal question
            if normal_questions:
                fallback_steal = random.choice(normal_questions)
                fallback_steal.question_type = "steal"  # Mark as steal question
                self.question_queue.append(fallback_steal)
                logger.info(f"No steal questions available, using normal question instead: {fallback_steal.text}")

        # 5. Sabotage question - only for تيم and تحدي modes
        if self.active_game and self.active_game.mode in ['تيم', 'تحدي']:
            if sabotage_questions:
                sabotage_q = random.choice(sabotage_questions)
                sabotage_q.question_type = "sabotage"  # Mark as sabotage question
                self.question_queue.append(sabotage_q)
                logger.info(f"Added sabotage question: {sabotage_q.text}")

        # 6. Doom question - only for تيم mode
        if self.active_game and self.active_game.mode == 'تيم':
            if doom_questions:
                doom_q = random.choice(doom_questions)
                self.question_queue.append(doom_q)
                logger.info(f"Added doom question: {doom_q.text}")
            else:
                # If no doom questions, use a normal question
                if normal_questions:
                    fallback_doom = random.choice(normal_questions)
                    fallback_doom.question_type = "doom"  # Mark as doom question
                    self.question_queue.append(fallback_doom)
                    logger.info(f"No doom questions available, using normal question instead: {fallback_doom.text}")

        logger.info(f"Total questions in queue: {len(self.question_queue)}")

        # Start asking questions
        await self.ask_next_question(channel)

    async def load_questions(self):
        """Load questions from the database"""
        # Check if there are questions in the database
        questions = Question.query.all()

        # If there are no questions, create some sample questions
        if not questions:
            sample_questions = [
                Question(
                    text="من هو مخترع المصباح الكهربائي؟",
                    answers="توماس إديسون,إديسون,توماس,edison",
                    category="science",
                    difficulty="easy"
                ),
                Question(
                    text="ما هي عاصمة المملكة العربية السعودية؟",
                    answers="الرياض,الرياض المملكة العربية السعودية,riyadh",
                    category="geography",
                    difficulty="easy"
                ),
                Question(
                    text="من هو مؤسس شركة مايكروسوفت؟",
                    answers="بيل غيتس,بيل جيتس,بيل قيتس,بل غيتس,bill gates",
                    category="technology",
                    difficulty="easy"
                ),
                Question(
                    text="ما هو العنصر الكيميائي الذي رمزه Hg؟",
                    answers="الزئبق,زئبق,زءبق,زيبق,mercury",
                    category="science",
                    difficulty="medium"
                ),
                Question(
                    text="من هو المؤسس الأول للدولة السعودية؟",
                    answers="محمد بن سعود,محمد ابن سعود,الإمام محمد بن سعود",
                    category="history",
                    difficulty="medium"
                ),
                Question(
                    text="كم عدد أحرف اللغة العربية؟",
                    answers="28,٢٨,ثمانية وعشرون",
                    category="language",
                    difficulty="easy"
                ),
                Question(
                    text="ما هو أطول نهر في العالم؟",
                    answers="النيل,نهر النيل,the nile",
                    category="geography",
                    difficulty="medium"
                ),
                Question(
                    text="ما هي أكبر دولة عربية من حيث المساحة؟",
                    answers="الجزائر,algeria",
                    category="geography",
                    difficulty="medium"
                ),
                Question(
                    text="من هو مخترع الهاتف؟",
                    answers="جراهام بيل,غراهام بيل,ألكسندر جراهام بيل,ألكسندر غراهام بيل,alexander graham bell",
                    category="science",
                    difficulty="easy"
                ),
                Question(
                    text="ما هي أكبر قارة في العالم؟",
                    answers="آسيا,asia",
                    category="geography",
                    difficulty="easy"
                )
            ]

            # Add sample questions to database
            for question in sample_questions:
                db.session.add(question)

            db.session.commit()
            questions = sample_questions

        # Store all questions in the instance
        self.all_questions = list(questions)

    async def ask_next_question(self, channel):
        """Ask the next question in the queue"""
        if not self.question_queue:
            # No more questions, end the game
            await self.end_game_with_results(channel)
            return

        # Get the next question
        self.current_question = self.question_queue.pop(0)
        logger.info(f"Asking next question: {self.current_question.text}, type: {self.current_question.question_type}")

        # Determine question type based on the question object
        self.is_golden_question = self.current_question.question_type == 'golden'
        self.is_doom_question = self.current_question.question_type == 'doom'
        self.is_steal_question = self.current_question.question_type == 'steal'
        self.is_fate_test = self.current_question.question_type == 'fate'
        self.is_sabotage_question = self.current_question.question_type == 'sabotage'

        # Safety check for active_game
        if not self.active_game:
            logger.error("active_game is None in ask_next_question, this shouldn't happen")
            return

        logger.info(f"Question types - Golden: {self.is_golden_question}, Doom: {self.is_doom_question}, " +
                   f"Steal: {self.is_steal_question}, Fate: {self.is_fate_test}, Sabotage: {self.is_sabotage_question}")

        # Handle special question types
        if self.is_sabotage_question:
            # Sabotage question
            await channel.send("🔪 **SABOTAGE QUESTION!** 🔪")

            if self.active_game.mode == 'تيم':
                await channel.send("اختر شخصًا من الفريق الآخر ترغب في استبعاده من اللعبة، قم بعمل منشن له.")
            else:  # تحدي mode
                await channel.send("اختر شخصًا ترغب في استبعاده من اللعبة، قم بعمل منشن له.")

            # Initialize the sabotage selection period
            self.waiting_for_sabotage_selection = True
            self.sabotage_selection_end_time = time.time() + SABOTAGE_SELECTION_TIMER
            self.sabotage_targets = {}

            # Wait for target selection
            await asyncio.sleep(SABOTAGE_SELECTION_TIMER)

            # If still waiting, proceed with the question anyway
            if self.waiting_for_sabotage_selection:
                self.waiting_for_sabotage_selection = False
                await channel.send("انتهت مهلة اختيار الأهداف! ستستمر اللعبة بدون استبعاد.")

            # Proceed with the question
            await channel.send("الآن، للإجابة على السؤال، أول من يجيب صح سيستبعد اللاعب الذي تم منشنه.")

        elif self.is_doom_question:
            # Doom question for team mode
            await channel.send("🔥 **DOOM Question!** 🔥")
            await channel.send(f"قادة الفرق! هذا سؤال خطير لكم القرار تجاوبوا أو تنسحبوا. إذا أجبتم إجابة صحيحة، تتضاعف النقاط! لكن إذا كانت الإجابة خاطئة أو انتهىالوقت، يخسر الفريق جميع نقاطه.")
            await channel.send(f"القادة فقط، اكتبوا '1' للقبول أو '2' للرفض خلال 10 ثوان.")

            self.waiting_for_doom_decision = True
            self.red_team_accepted_doom = False
            self.blue_team_accepted_doom = False

            # Wait for leaders' decisions
            await asyncio.sleep(10)

            # If still waiting, consider it a rejection
            if self.waiting_for_doom_decision:
                self.waiting_for_doom_decision = False
                await channel.send("انتهت مهلة القرار! اعتبار السؤال كسؤال عادي.")
                self.is_doom_question = False

        elif self.is_steal_question:
            if self.active_game.mode == 'تيم':
                # Steal question for team mode
                await channel.send("🔄 **Steal or Boost Question!** 🔄")
                await channel.send(f"جميع اللاعبين، اكتبوا 'زرف' أو 'زود' قبل بدء السؤال التالي!")

                # Wait for players to choose
                self.player_choices = {}
                await asyncio.sleep(10)  # Give players 10 seconds to choose

                await channel.send(f"الآن السؤال! الفريق الذي يجيب أولاً بشكل صحيح، سيتم تنفيذ اختياره!")

            elif self.active_game.mode == 'تحدي':
                # Steal question for challenge mode
                await channel.send("🔄 **Steal Question!** 🔄")
                await channel.send(f"إذا أجبت إجابة صحيحة، سيختار البوت لاعباً عشوائياً لزرف نقاطه!")

        elif self.is_golden_question:
            # Golden question
            await channel.send("🌟 **Golden Question!** 🌟")
            await channel.send("إذا أجبت إجابة صحيحة، ستحصل على 50 نقطة!")

        elif self.is_fate_test:
            # Test of Fate
            await channel.send("⚡ **Test of Fate!** ⚡")
            await channel.send("ستواجهون 5 أسئلة متتابعة! 10 نقاط لكل إجابة صحيحة، وخصم 5 نقاط لكل إجابة خاطئة. وعند انتهاء الوقت بدون إجابة، لا يوجد خصم!")

            # The fate questions are already in the queue with the right type marking
            # Just set the counter for tracking fate test progress
            logger.info("Starting Fate Test question sequence")
            self.fate_test_questions_remaining = 5
            # Store the initial scores at the start of test of fate
            if self.active_game.mode == 'تيم':
                self.team_scores_before_fate = {
                    'red': sum(self.players[p].score for p in self.red_team),
                    'blue': sum(self.players[p].score for p in self.blue_team)
                }
            else:
                self.player_scores_before_fate = {username: player.score for username, player in self.players.items()}

        # Ask the question with timer
        await channel.send(f"السؤال: {self.current_question.text}")
        await channel.send(f"لديكم {QUESTION_TIMER} ثوان للإجابة...")

        # Set question start time
        self.question_start_time = time.time()

        # Wait for the timer to expire
        await asyncio.sleep(QUESTION_TIMER)

        # If question is still active, no one answered correctly
        if self.current_question:
            await channel.send(f"انتهى الوقت! الإجابة الصحيحة هي: {self.current_question.answers.split(',')[0]}")

            # Check if this was a doom question and some leaders accepted it
            if self.is_doom_question and self.active_game and self.active_game.mode == 'تيم':
                # Apply consequences for teams who accepted but didn't answer
                if self.red_team_accepted_doom and self.red_leader:
                    # Reset red team scores to 0
                    for member in self.red_team:
                        self.players[member].score = 0
                    await channel.send(f"🔥 انتهى الوقت! الفريق الأحمر يخسر جميع نقاطه في سؤال الدووم! 🔥")

                if self.blue_team_accepted_doom and self.blue_leader:
                    # Reset blue team scores to 0
                    for member in self.blue_team:
                        self.players[member].score = 0
                    await channel.send(f"🔥 انتهى الوقت! الفريق الأزرق يخسر جميع نقاطه في سؤال الدووم! 🔥")

                db.session.commit()

            # Move to next question
            self.current_question = None

            # If this was part of a fate test, continue with next questions
            if self.fate_test_questions_remaining > 0:
                self.fate_test_questions_remaining -= 1
                await self.ask_next_question(channel)
            elif self.fate_test_questions_remaining == 0 and self.is_fate_test:
                # End of Test of Fate - summarize results
                if self.active_game.mode == 'تيم':
                    # Calculate team scores during fate test
                    red_current_score = sum(self.players[p].score for p in self.red_team)
                    blue_current_score = sum(self.players[p].score for p in self.blue_team)
                    red_gained = red_current_score - self.team_scores_before_fate.get('red', 0)
                    blue_gained = blue_current_score - self.team_scores_before_fate.get('blue', 0)

                    await channel.send(f"⚡ Test of Fate Complete! ⚡")
                    await channel.send(f"🔴 الفريق الأحمر: جمع {red_gained} نقطة في الاختبار")
                    await channel.send(f"🔵 الفريق الأزرق: جمع {blue_gained} نقطة في الاختبار")
                    self.is_fate_test = False
                else:
                    # Calculate individual scores for challenge mode
                    results = []
                    for username, player in self.players.items():
                        initial_score = self.player_scores_before_fate.get(username, 0)
                        gained = player.score - initial_score
                        results.append((username, gained))

                    await channel.send(f"⚡ Test of Fate Complete! ⚡")
                    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
                    for username, points in sorted_results[:3]:  # Top 3 players
                        await channel.send(f"@{username}: جمع {points} نقطة في الاختبار")
                    self.is_fate_test = False

                await asyncio.sleep(2)  # Pause between questions
                await self.ask_next_question(channel)
            else:
                await asyncio.sleep(2)  # Pause between questions
                await self.ask_next_question(channel)

    async def handle_question_answer(self, message):
        """Handle player answers to questions"""
        # Safety check - need an active game and current question
        if not self.active_game or not self.current_question:
            logger.warning("Attempted to handle answer with no active game or current question")
            return

        username = message.author.name
        content = message.content.strip()

        # Skip messages from eliminated players
        if username in self.eliminated_players:
            return

        # Check if the player is registered for the game
        if (self.active_game.mode != 'فردي' and username not in self.registered_players) or \
           (self.active_game.mode == 'فردي' and username != list(self.registered_players)[0]):
            return

        # Check if the answer is correct
        if self.current_question.check_answer(content):
            # Handle sabotage question if applicable
            if self.is_sabotage_question and self.sabotage_targets.get(username):
                # Get the target player
                target_player = self.sabotage_targets.get(username)

                # Add player to eliminated list
                self.eliminated_players.add(target_player)

                # Send elimination message with funny message
                elimination_messages = [
                    f"@{target_player} تم استبعادك من اللعبة! يبدو أن خصمك ذكي جدًا! 🔪",
                    f"@{target_player} صدمة! تم استبعادك من المنافسة! حظًا أوفر في المرة القادمة! 💀",
                    f"@{target_player} وداعاً! تم استبعادك بواسطة @{username}! 👋",
                    f"@{target_player} أخرجت من اللعبة! ربما كان يجب عليك الاختباء بشكل أفضل! 🙈",
                    f"@{target_player} اوووووت! 🏃‍♂️",
                    f"@{target_player} برررا! 👉",
                    f"@{target_player} تفرج بس! لا تشارك! 🍿",
                    f"@{target_player} محد قالك ماتجاوب! 🤦‍♂️",
                    f"@{target_player} الفكررر ياانسان! 🧠",
                    f"@{target_player} يلا خيره! 👋",
                    f"@{target_player} تستاهل! 😎",
                    f"@{target_player} الققممم! ✨",
                    f"@{target_player} عسسل على قلبي! 🍯",
                    f"@{target_player} شلوووتي! 👟",
                    f"@{target_player} لاتكثر كلام! 🤐",
                    f"@{target_player} تفنش واااء! 💨",
                    f"@{target_player} انتهى وقتك! ⏱️",
                    f"@{target_player} الله يعين! 🙏",
                    f"@{target_player} مع السلامة! 👋",
                    f"@{target_player} اللعب احلى بدونك! 😜",
                    f"@{target_player} فشلنا في إنقاذك! 🚑",
                    f"@{target_player} هههههههه! 😂",
                    f"@{target_player} اقضب الباب! 🚪",
                    f"@{target_player} كاااك! 🐔",
                    f"@{target_player} يفهههم اللي طلعك! 👌"
                ]
                await message.channel.send(random.choice(elimination_messages))

                # Reset sabotage flags for future questions
                self.is_sabotage_question = False
                self.sabotage_targets = {}

            # Calculate score based on response time
            response_time = time.time() - self.question_start_time
            points = 0

            if self.is_golden_question:
                points = 50  # Golden question points
            elif response_time <= 5:
                points = 10  # Fast answer
            elif response_time <= 10:
                points = 5   # Slower answer

            # Handle consecutive correct answers bonus
            self.consecutive_answers[username] += 1
            if self.consecutive_answers[username] >= 3:
                points += 10  # Bonus for 3+ consecutive correct answers
                await message.channel.send(f"وااااو! @{username} سلسلة اجابات رائعة، القم 10 نقاط إضافية لك!")
                self.consecutive_answers[username] = 0  # Reset streak after awarding bonus

            # Handle Test of Fate points
            if self.is_fate_test:
                points = 10  # Fixed points for Test of Fate

            # Handle Doom Question points
            if self.is_doom_question and self.active_game.mode == 'تيم':
                # Check if this player is a leader who accepted the doom question
                is_doom_participant = (username == self.red_leader and self.red_team_accepted_doom) or (username == self.blue_leader and self.blue_team_accepted_doom)

                if is_doom_participant:
                    # Double the points for correct answer to doom question
                    points *= 2
                    await message.channel.send(f"إجابة صحيحة على سؤال الدووم! النقاط مضاعفة!")

            # Update player score
            player = self.players[username]
            team = player.team if self.active_game.mode == 'تيم' else None

            # Add points to player only if not eliminated
            if username not in self.eliminated_players:
                player.score += points
                db.session.commit()

            # Handle steal question logic for team mode
            if self.is_steal_question:
                if self.active_game.mode == 'تيم':
                    team_name = "الأحمر" if username in self.red_team else "الأزرق"
                    leader_name = self.red_leader if username in self.red_team else self.blue_leader

                    await message.channel.send(f"إجابة صحيحة من @{username} من الفريق {team_name}! +{points} نقطة")

                    # Check player's choice (زرف or زود)
                    choice = self.player_choices.get(username, 'زرف')  # Default to زرف if no choice made

                    if choice == 'زرف':
                        # Steal points
                        self.waiting_for_steal_selection = True
                        self.steal_request = {
                            'team': team,
                            'leader': leader_name,
                            'points': points
                        }

                        await message.channel.send(f"@{leader_name} اختار زرف! يمكنك الآن اختيار لاعب من الفريق المنافس لخصم نقاطه. اكتب اسم اللاعب مثل '@اسم_اللاعب' خلال 10 ثوان.")
                    else:  # زود
                        # Random bonus points
                        bonus_points = random.randint(0, 30)
                        if bonus_points > 0:
                            self.players[username].score += bonus_points
                            db.session.commit()
                            await message.channel.send(f"@{username} اختار زود! حصل على {bonus_points} نقطة إضافية بالحظ!")
                        else:
                            await message.channel.send(f"@{username} اختار زود! لكن لم يحالفه الحظ وحصل على 0 نقطة إضافية!")

                elif self.active_game.mode == 'تحدي':
                    # Random steal in challenge mode
                    await message.channel.send(f"إجابة صحيحة من @{username}! +{points} نقطة")

                    # Select random player to steal from
                    other_players = [p for p in self.registered_players if p != username]
                    if other_players:
                        target_player = random.choice(other_players)
                        steal_points = min(self.players[target_player].score, points // 2)  # Steal up to half of earned points

                        if steal_points > 0:
                            self.players[target_player].score -= steal_points
                            self.players[username].score += steal_points
                            db.session.commit()

                            await message.channel.send(f"@{username} زرف {steal_points} نقطة من @{target_player}!")

                # Wait for leader to choose a player
                await asyncio.sleep(10)

                # If still waiting, auto-skip
                if self.waiting_for_steal_selection:
                    self.waiting_for_steal_selection = False
                    await message.channel.send(f"انتهت المهلة! لم يتم اختيار أي لاعب للخصم.")

            else:
                # Normal scoring announcement
                if self.active_game.mode == 'تيم':
                    team_name = "الأحمر" if username in self.red_team else "الأزرق"
                    await message.channel.send(f"إجابة صحيحة من @{username} من الفريق {team_name}! +{points} نقطة")
                else:
                    await message.channel.send(f"إجابة صحيحة من @{username}! +{points} نقطة")

            # Mark question as answered
            self.current_question = None

            # Move to next question after a short delay
            if self.fate_test_questions_remaining > 0:
                self.fate_test_questions_remaining -= 1
                await self.ask_next_question(message.channel)
            elif self.fate_test_questions_remaining == 0 and self.is_fate_test:
                # End of Test of Fate - summarize results
                if self.active_game.mode == 'تيم':
                    # Calculate team scores during fate test
                    red_current_score = sum(self.players[p].score for p in self.red_team)
                    blue_current_score = sum(self.players[p].score for p in self.blue_team)
                    red_gained = red_current_score - self.team_scores_before_fate.get('red', 0)
                    blue_gained = blue_current_score - self.team_scores_before_fate.get('blue', 0)

                    await message.channel.send(f"⚡ Test of Fate Complete! ⚡")
                    await message.channel.send(f"🔴 الفريق الأحمر: جمع {red_gained} نقطة في الاختبار")
                    await message.channel.send(f"🔵 الفريق الأزرق: جمع {blue_gained} نقطة في الاختبار")
                    self.is_fate_test = False
                else:
                    # Calculate individual scores for challenge mode
                    results = []
                    for username, player in self.players.items():
                        initial_score = self.player_scores_before_fate.get(username, 0)
                        gained = player.score - initial_score
                        results.append((username, gained))

                    await message.channel.send(f"⚡ Test of Fate Complete! ⚡")
                    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
                    for username, points in sorted_results[:3]:  # Top 3 players
                        await message.channel.send(f"@{username}: جمع {points} نقطة في الاختبار")
                    self.is_fate_test = False

                await asyncio.sleep(2)  # Pause between questions
                await self.ask_next_question(message.channel)
            else:
                await asyncio.sleep(2)  # Pause between questions
                await self.ask_next_question(message.channel)

        elif self.is_fate_test:
            # Wrong answer in Test of Fate - deduct points
            player = self.players[username]
            player.score = max(0, player.score - 5)  # Don't go below 0
            db.session.commit()

            # Reset consecutive correct answers
            self.consecutive_answers[username] = 0

            # Inform about point deduction
            if self.active_game.mode == 'تيم':
                team_name = "الأحمر" if username in self.red_team else "الأزرق"
                await message.channel.send(f"إجابة خاطئة من @{username} من الفريق {team_name}! -5 نقاط")
            else:
                await message.channel.send(f"إجابة خاطئة من @{username}! -5 نقاط")
        else:
            # Wrong answer - reset consecutive correct answers
            self.consecutive_answers[username] = 0

            # Handle Doom Question failure for team mode
            if self.is_doom_question and self.active_game.mode == 'تيم':
                # Check if this player is a leader who accepted the doom question
                is_doom_participant = (username == self.red_leader and self.red_team_accepted_doom) or (username == self.blue_leader and self.blue_team_accepted_doom)

                if is_doom_participant:
                    team = "أحمر" if username in self.red_team else "أزرق"
                    team_members = self.red_team if team == "أحمر" else self.blue_team

                    # Reset all team members' scores to 0
                    for member in team_members:
                        self.players[member].score = 0

                    db.session.commit()

                    await message.channel.send(f"🔥 إجابة خاطئة من @{username} على سؤال الدووم! الفريق {team} يخسر جميع نقاطه! 🔥")

                    # End game and declare other team as winner
                    winning_team = "أزرق" if team == "أحمر" else "أحمر"
                    await message.channel.send(f"🎉 انتهت اللعبة! الفريق {winning_team} هو الفائز! 🎉")
                    await self.end_game()
                    return

                # Mark question as answered
                self.current_question = None

                # Move to next question after a short delay
                await asyncio.sleep(2)
                await self.ask_next_question(message.channel)

    async def handle_doom_decision(self, message):
        """Handle leader decisions for doom questions"""
        username = message.author.name
        content = message.content.strip()

        # Only team leaders can make decisions
        if username not in [self.red_leader, self.blue_leader]:
            return

        if content == '1':  # Accept the doom question
            team = "أحمر" if username == self.red_leader else "أزرق"

            # Update team's acceptance status
            if username == self.red_leader:
                self.red_team_accepted_doom = True
            else:
                self.blue_team_accepted_doom = True

            await message.channel.send(f"الفريق {team} قبل تحدي سؤال الدووم!")

            # Check if both teams have responded
            if self.red_team_accepted_doom and self.blue_team_accepted_doom:
                # Both teams have accepted/rejected, stop waiting
                self.waiting_for_doom_decision = False
                await message.channel.send(f"الفريقان اتخذا قرارهما! سيتم طرح سؤال الدووم على الليدر فقط.")
            elif (username == self.red_leader and self.blue_leader is None) or (username == self.blue_leader and self.red_leader is None):
                # Only one team exists (unlikely), so proceed with the doom question
                self.waiting_for_doom_decision = False

        elif content == '2':  # Reject the doom question
            team = "أحمر" if username == self.red_leader else "أزرق"
            await message.channel.send(f"الفريق {team} رفض سؤال الدووم! سيتم طرح سؤال عادي للفريق {team}.")

            # Mark team's refusal
            if username == self.red_leader:
                self.red_team_accepted_doom = False
            else:
                self.blue_team_accepted_doom = False

            # Check if both teams have responded
            if not self.red_team_accepted_doom and not self.blue_team_accepted_doom:
                # Both teams rejected, turn off doom question entirely
                self.is_doom_question = False
                self.waiting_for_doom_decision = False
            elif (self.red_leader is not None and self.blue_leader is not None) and ((not self.red_team_accepted_doom and self.blue_team_accepted_doom) or (self.red_team_accepted_doom and not self.blue_team_accepted_doom)):
                # One team accepted, one team rejected
                self.waiting_for_doom_decision = False

    async def handle_sabotage_selection(self, message):
        """Handle player selection for sabotage questions"""
        username = message.author.name
        content = message.content.strip()

        # Skip if not a registered player
        if username not in self.registered_players:
            return

        # Check if time has expired
        if time.time() > self.sabotage_selection_end_time:
            return

        # Check for '@username' format
        match = re.match(r'@(\w+)', content)
        if not match:
            return

        target_player = match.group(1).lower()

        # In تيم mode, verify player is selecting from opposite team
        if self.active_game.mode == 'تيم':
            player_team = 'red' if username in self.red_team else 'blue'
            target_team = 'red' if target_player in self.red_team else 'blue'

            # Player must select from opposite team
            if player_team == target_team:
                await message.channel.send(f"@{username} يجب اختيار لاعب من الفريق المنافس!")
                return

        # In تحدي mode, any player can be selected
        elif self.active_game.mode == 'تحدي':
            # Cannot select yourself
            if target_player == username:
                await message.channel.send(f"@{username} لا يمكنك استبعاد نفسك!")
                return

        # Store the target for later use when someone answers correctly
        if target_player in self.registered_players and target_player not in self.sabotage_targets.values():
            self.sabotage_targets[username] = target_player
            await message.channel.send(f"@{username} اختار استبعاد @{target_player}!")

        # If all players have selected targets, end selection phase
        if len(self.sabotage_targets) == len(self.registered_players):
            self.waiting_for_sabotage_selection = False
            await message.channel.send("تم اختيار جميع الأهداف! الآن للإجابة على السؤال...")
        elif len(self.sabotage_targets) >= len(self.registered_players) // 2:
            # If at least half have selected, end early
            self.waiting_for_sabotage_selection = False
            await message.channel.send("تم اختيار ما يكفي من الأهداف! الآن للإجابة على السؤال...")

    async def handle_steal_selection(self, message):
        """Handle leader selection for steal questions"""
        username = message.author.name
        content = message.content.strip()

        # Check if it's the correct leader making the selection
        if username != self.steal_request['leader']:
            return

        # Check for '@username' format
        match = re.match(r'@(\w+)', content)
        if not match:
            return

        target_player = match.group(1).lower()

        # Check if the target player is in the opposing team
        stealing_team = self.steal_request['team']
        if stealing_team == 'أحمر' and target_player in self.blue_team:
            # Red team stealing from blue team
            if target_player in self.players:
                # Deduct points from target player (up to current score)
                steal_points = min(self.players[target_player].score, self.steal_request['points'])
                self.players[target_player].score -= steal_points

                # Add points to the leader
                self.players[username].score += steal_points

                db.session.commit()

                await message.channel.send(f"@{username} زرف {steal_points} نقطة من @{target_player}!")

        elif stealing_team == 'أزرق' and target_player in self.red_team:
            # Blue team stealing from red team
            if target_player in self.players:
                # Deduct points from target player (up to current score)
                steal_points = min(self.players[target_player].score, self.steal_request['points'])
                self.players[target_player].score -= steal_points

                # Add points to the leader
                self.players[username].score += steal_points

                db.session.commit()

                await message.channel.send(f"@{username} زرف {steal_points} نقطة من @{target_player}!")

        self.waiting_for_steal_selection = False
        self.steal_request = None

    async def end_game_with_results(self, channel):
        """End the game and display results"""
        if not self.active_game:
            return

        game_mode = self.active_game.mode

        await channel.send("🎮 انتهت اللعبة! 🎮")
        await channel.send("🏆 إعلان النتائج النهائية 🏆")

        if game_mode == 'فردي':
            # Challenge mode - display player score
            player = next(iter(self.players.values()))
            await channel.send(f"النتيجة النهائية: @{player.username} حصل على {player.score} نقطة")

            # Fun message for low scores
            if player.score < 50:
                fun_messages = [
                    "حظًا أوفر في المرة القادمة! 😉",
                    "مش مشكلة، كلنا مررنا بيوم سيئ! 😅",
                    "أنا واثق أنك تعرف أكثر من هذا، ربما كنت مشغولاً! 🤔",
                    "لا تقلق، المعرفة تأتي مع الوقت! 📚"
                ]
                await channel.send(random.choice(fun_messages))
            else:
                await channel.send("أداء ممتاز! 👏")

        elif game_mode == 'تحدي':
            # Team challenge mode - display player rankings
            sorted_players = sorted(self.players.values(), key=lambda p: p.score, reverse=True)

            await channel.send("🏆 ترتيب اللاعبين 🏆")

            for i, player in enumerate(sorted_players[:3], 1):
                await channel.send(f"{i}. @{player.username}: {player.score} نقطة")

            # Fun messages for low scoring players
            low_scorers = [p for p in sorted_players if p.score < 50]
            if low_scorers:
                fun_messages = [
                    "لا بأس، المهم المشاركة! 😊",
                    "استمر في المحاولة، ستتحسن في المرة القادمة! 💪",
                    "حظًا أوفر في المرة القادمة! 🍀",
                    "الجميع يبدأ من مكان ما! 🌱",
                    "أقل من 50؟ مبروك، جبت رقم قياسي! على الاغبياء",
                    "أقل من 50؟ احسك تمزح مستحيل",
                    "لو نايم مو ازين لك ولنا",
                    "مبروك فزت معانا بدورة لتطوير",
                    "يمكن المرة الجاية تظبط لاحظ انها (تظبط)",
                    "50؟ عقلك محدووودالذكاء",
                    "أقل من 50؟ أعتقد عقلك نايم",
                    "50 نقطة؟ مايحتاج اتكلم",
                    "واضح  مااااافيه عقل",
                    "أقل من 50؟ والله جبت أقل من توقعاتي... المرة الجاية اكيد تحت الصفر",
                    "أقل من 50؟ بس بس كفاية اليوم!",
                    "خلاص روح جرب ألعاب ثانية، هذي مو لك!",
                    "عقلك مو معك ضدك!",
                    "50 نقطة؟ ههههههههههههههههه",
                    "لاحول ولا قوة الا بالله جبت أقل من 50؟ كيف فكرت في السؤال؟",
                    "عقلك نايم روح كمل نوم معه",
                    "ماودي اجرحك بس انت غبي وهطف",
                    "ماشاءالله وعدم الذكاء اللي عندك",
                    "المرة الجاية بغششك لأن الغباء هذا كارثة",
                    "أقل من 50؟ صدقني لو لاعب حقرة بقرة ازين لك"
                ]

                # Get a random player with low score
                random_player = random.choice(low_scorers)
                await channel.send(f"@{random_player.username}: {random.choice(fun_messages)}")

        elif game_mode == 'تيم':
            # Team vs team mode - calculate team scores
            red_score = sum(self.players[p].score for p in self.red_team)
            blue_score = sum(self.players[p].score for p in self.blue_team)

            await channel.send(f"🔴 الفريق الأحمر: {red_score} نقطة")
            await channel.send(f"🔵 الفريق الأزرق: {blue_score} نقطة")

            if red_score > blue_score:
                await channel.send("🎉 الفريق الأحمر هو الفائز! 🎉")

                # Fun message for losing team
                fun_messages = [
                    "الفريق الأزرق، لا تحزنوا! الفوز والخسارة جزء من اللعبة! 😊",
                    "الفريق الأزرق، حظكم أفضل في المرة القادمة! 💙",
                    "الفريق الأزرق، أنتم أبطال رغم الخسارة! 🌟",
                    "الفريق الأزرق، استعدوا للانتقام في الجولة القادمة! 💪",
                    "لا تحزنوا! الفوز والخسارة جزء من اللعبة! 😊",
                    "حظكم أفضل في المرة القادمة! 💙❤️",
                    "أنتم أبطال رغم الخسارة! 🌟",
                    "استعدوا لل الانتقام في الجولة القادمة! 💪"
                ]
                await channel.send(random.choice(fun_messages))

            elif blue_score > red_score:
                await channel.send("🎉 الفريق الأزرق هو الفائز! 🎉")

                # Fun message for losing team
                fun_messages = [
                    "الفريق الأحمر، لا تحزنوا! الفوز والخسارة جزء من اللعبة! 😊",
                    "الفريق الأحمر، حظكم أفضل في المرة القادمة! ❤️",
                    "الفريق الأحمر، أنتم أبطال رغم الخسارة! 🌟",
                    "الفريق الأحمر، استعدوا للانتقام في الجولة القادمة! 💪",
                    "لا تحزنوا! الفوز والخسارة جزء من اللعبة! 😊",
                    "حظكم أفضل في المرة القادمة! 💙❤️",
                    "أنتم أبطال رغم الخسارة! 🌟",
                    "استعدوا للانتقام في الجولة القادمة! 💪"
                ]
                await channel.send(random.choice(fun_messages))

            else:
                await channel.send("🎉 تعادل! كلا الفريقين فائز! 🎉")

        # Additional motivational messages to winners
        if game_mode == 'فردي' and player.score >= 50:
            motivational_messages = [
                "أنت بطل حقيقي! استمر في التألق! ✨",
                "إنجاز رائع! استمتع بالنصر! 🎖️",
                "ذكاءخارق! أنت تستحق كل التقدير! 🧠",
                "مستوى استثنائي من المعرفة! 🔥"
            ]
            await channel.send(random.choice(motivational_messages))
        elif game_mode == 'تحدي' and sorted_players and sorted_players[0].score >= 50:
            winner = sorted_players[0]
            motivational_messages = [
                f"@{winner.username} أنت نجم المباراة! إبداع لا مثيل له! ✨",
                f"@{winner.username} قيادة رائعة وذكاء متميز! 🥇",
                f"@{winner.username} لا أحد يستطيع منافستك! رائع! 🔥",
                f"@{winner.username} إنجاز يستحق الاحتفال! 🎊"
            ]
            await channel.send(random.choice(motivational_messages))

        # End game
        await self.end_game()

    async def end_game(self):
        """End the current game session"""
        if self.active_game:
            # Update game session in database
            self.active_game.is_active = False
            self.active_game.end_time = datetime.datetime.utcnow()
            db.session.commit()

            # Reset game state
            self.active_game = None
            self.current_question = None
            self.waiting_for_mode = False
            self.waiting_for_registration = False
            self.waiting_for_leader = False
            self.waiting_for_doom_decision = False
            self.waiting_for_steal_selection = False
            self.waiting_for_sabotage_selection = False
            self.eliminated_players = set()
            self.players = {}
            self.registered_players = set()
            self.red_team = set()
            self.blue_team = set()
            self.red_leader = None
            self.blue_leader = None
            self.consecutive_answers = defaultdict(int)

MAX_QUESTIONS_SOLO = 20
MAX_QUESTIONS_TEAM = 10