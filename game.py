import enum
import asyncio
import time
import random
import logging
from typing import Dict, List, Set, Optional, Tuple, Union
import random
from typing import List, Optional, Union
try:
    from app import app, db
    from models import Question as DBQuestion, FunnyResponse
except:
    # fallback for when app isn't available
    pass

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GameMode(enum.Enum):
    """Different game modes for the Waj game"""
    SOLO = "اتحداك"
    GROUP = "تحدي"
    TEAM = "تيم"

class GameState(enum.Enum):
    """Different states the game can be in"""
    INACTIVE = 0
    REGISTRATION = 1
    LEADER_SELECTION = 2
    RUNNING = 3
    WAITING_FOR_ANSWER = 4
    WAITING_FOR_DECISION = 5
    FINISHED = 6

class Player:
    """Represents a player in the game"""
    def __init__(self, username, user_id):
        self.username = username
        self.user_id = user_id
        self.team = None  # "أحمر" or "أزرق" for team mode
        self.score = 0
        self.consecutive_correct = 0
        self.is_leader = False
    
    def add_score(self, points):
        """Add points to player's score"""
        self.score += points
    
    def reset_consecutive(self):
        """Reset consecutive correct answers"""
        self.consecutive_correct = 0
    
    def add_consecutive(self):
        """Increment consecutive correct answers"""
        self.consecutive_correct += 1
        # Award bonus for 3 consecutive correct answers
        if self.consecutive_correct == 3:
            self.score += 10
            return True
        return False

class Team:
    """Represents a team in team mode"""
    def __init__(self, name):
        self.name = name  # "أحمر" or "أزرق"
        self.players = []
        self.score = 0
        self.leader = None
    
    def add_player(self, player):
        """Add a player to the team"""
        self.players.append(player)
        player.team = self.name
    
    def set_leader(self, player):
        """Set a player as team leader"""
        self.leader = player
        player.is_leader = True
    
    def add_score(self, points):
        """Add points to team score"""
        self.score += points
    
    def get_total_score(self):
        """Get total score of the team"""
        return self.score

class Question:
    """Represents a question in the game"""
    def __init__(self, text, answer, category="عام", question_type="normal"):
        self.text = text
        self.answer = answer
        self.category = category
        self.type = question_type  # normal, golden, steal, doom, test_of_fate
        self.asked_at = None
    
    def ask(self):
        """Mark the question as asked now"""
        self.asked_at = time.time()
    
    def is_correct(self, answer):
        """Check if the provided answer is correct"""
        return answer.lower().strip() == self.answer.lower().strip()
    
    def get_response_time(self):
        """Get the time taken to respond to this question"""
        if self.asked_at:
            return time.time() - self.asked_at
        return 0

class Game:
    """Main game class for managing the Waj game"""
    def __init__(self, channel, mode: GameMode):
        self.channel = channel
        self.mode = mode
        self.state = GameState.INACTIVE
        self.players = {}  # username -> Player
        self.questions = []
        self.current_question = None
        self.start_time = None
        self.end_time = None
        self.is_active = False
        self.registration_task = None
        self.answer_task = None
        self.teams = {
            "أحمر": Team("أحمر"),
            "أزرق": Team("أزرق")
        }
        self.question_count = 0
        self.max_questions = 10  # القيمة الافتراضية
        self.waiting_for_question_count = False # هل ننتظر اللاعب أن يحدد عدد الأسئلة
        
        # For special question types
        self.is_golden_question = False
        self.is_steal_question = False
        self.is_doom_question = False
        self.is_test_of_fate = False
        self.test_of_fate_questions = []
        self.test_of_fate_index = 0
        
        # For steal question
        self.steal_player = None
        self.steal_target = None
        self.steal_type = None  # 'زرف' or 'زود'
        self.doom_decision_required = False
        
        # متغيرات جديدة لتتبع الأسئلة الخاصة
        self.has_golden_question_appeared = False
        self.has_steal_question_appeared = False
        self.has_test_of_fate_appeared = False
        
        # عنصر موجود مرتين - يجب إزالة هذا السطر
        # self.doom_decision_required = False
        
        logger.info(f"Game created with mode: {mode.value}")
    
    async def start_registration(self):
        """Start the registration phase"""
        self.is_active = True
        self.state = GameState.REGISTRATION
        
        if self.mode == GameMode.SOLO:
            # Solo mode needs to ask how many questions
            self.waiting_for_question_count = True
            await self.channel.send("كم عدد الأسئلة 5 أو 10؟")
            # استخدام الوضع التقليدي للبدء فقط بعد تحديد عدد الأسئلة
            # self.registration_task = asyncio.create_task(self.wait_for_solo_start())
        
        elif self.mode == GameMode.GROUP:
            await self.channel.send("اكتب R للتسجيل")
            self.registration_task = asyncio.create_task(self.wait_for_group_registration())
        
        elif self.mode == GameMode.TEAM:
            await self.channel.send("اختار فريقك اكتب احمر او ازرق")
            self.registration_task = asyncio.create_task(self.wait_for_team_registration())
    
    async def wait_for_solo_start(self):
        """Wait for solo player to start or auto-start after timeout"""
        await asyncio.sleep(10)
        if self.state == GameState.REGISTRATION:
            await self.start_game()
    
    async def wait_for_group_registration(self):
        """Wait for group players to register"""
        await asyncio.sleep(20)
        if self.state == GameState.REGISTRATION:
            if len(self.players) > 1:  # تعديل: يجب أن يكون هناك أكثر من لاعب واحد
                await self.channel.send(f"انتهى وقت التسجيل! {len(self.players)} لاعب مسجل.")
                await self.start_game()
            else:
                await self.channel.send("عدد اللاعبين غير كافٍ. يجب أن يكون هناك لاعبين على الأقل. تم إلغاء اللعبة.")
                self.is_active = False
    
    async def wait_for_team_registration(self):
        """Wait for team players to register"""
        await asyncio.sleep(30)
        if self.state == GameState.REGISTRATION:
            red_count = len(self.teams["أحمر"].players)
            blue_count = len(self.teams["أزرق"].players)
            
            # تعديل: يجب أن يكون هناك أكثر من لاعب في كل فريق
            if red_count > 1 and blue_count > 1:
                await self.channel.send(f"انتهى وقت التسجيل! الفريق الأحمر: {red_count} لاعب، الفريق الأزرق: {blue_count} لاعب.")
                await self.select_team_leaders()
            else:
                await self.channel.send("عدد اللاعبين غير كافٍ. يجب أن يكون هناك لاعبين على الأقل في كل فريق. تم إلغاء اللعبة.")
                self.is_active = False
    
    async def select_team_leaders(self):
        """Start the leader selection phase for team mode"""
        self.state = GameState.LEADER_SELECTION
        
        await self.channel.send("حان وقت اختيار القادة! اكتب '@username' لاختيار قائد للفريق الأحمر.")
        
        # Wait for red team leader selection
        self.registration_task = asyncio.create_task(self.wait_for_leader_selection("أحمر"))
    
    async def wait_for_leader_selection(self, team_name):
        """Wait for leader selection for a team"""
        await asyncio.sleep(20)
        
        if self.state == GameState.LEADER_SELECTION:
            # If no leader was selected, pick one randomly
            if self.teams[team_name].leader is None and len(self.teams[team_name].players) > 0:
                leader = random.choice(self.teams[team_name].players)
                self.teams[team_name].set_leader(leader)
                await self.channel.send(f"تم اختيار {leader.username} كقائد للفريق {team_name} عشوائيًا.")
            
            # For red team, now select blue team leader
            if team_name == "أحمر":
                await self.channel.send("اكتب '@username' لاختيار قائد للفريق الأزرق.")
                self.registration_task = asyncio.create_task(self.wait_for_leader_selection("أزرق"))
            
            # For blue team, start the game after leader selection
            elif team_name == "أزرق":
                await self.start_game()
    
    async def start_game(self):
        """Start the actual game"""
        self.state = GameState.RUNNING
        self.start_time = time.time()
        
        # فقط في وضع الفرق نحتاج لعرض قادة الفرق
        if self.mode == GameMode.TEAM:
            red_leader = self.teams["أحمر"].leader.username if self.teams["أحمر"].leader else "لا أحد"
            blue_leader = self.teams["أزرق"].leader.username if self.teams["أزرق"].leader else "لا أحد"
            
            await self.channel.send(f"قائد الفريق الأحمر: {red_leader}، قائد الفريق الأزرق: {blue_leader}")
        
        # Ask the first question
        await self.ask_next_question()
    
    def get_random_question(self, question_type="normal"):
        """
        الحصول على سؤال عشوائي من قاعدة البيانات
        
        Args:
            question_type: نوع السؤال (normal, golden, steal, doom)
        
        Returns:
            Question: كائن من نوع Question يمثل السؤال المختار
        """
        try:
            with app.app_context():
                # جلب سؤال عشوائي من قاعدة البيانات حسب النوع
                if question_type == "doom":
                    # سحب سؤال من نوع doom
                    db_question = DBQuestion.query.filter_by(question_type="doom").order_by(db.func.random()).first()
                else:
                    # سحب سؤال عشوائي
                    db_question = DBQuestion.query.filter_by(question_type=question_type).order_by(db.func.random()).first()
                
                # إذا لم يجد سؤالاً من النوع المطلوب، اسحب سؤالاً عادياً
                if db_question is None:
                    db_question = DBQuestion.query.filter_by(question_type="normal").order_by(db.func.random()).first()
                
                # تحويل السؤال من قاعدة البيانات إلى نوع سؤال في اللعبة
                question = Question(
                    text=db_question.text,
                    answer=db_question.answer,
                    category=db_question.category,
                    question_type=db_question.question_type
                )
                
                # زيادة عداد مرات ظهور السؤال
                db_question.times_asked += 1
                db.session.commit()
                
                return question
                
        except Exception as e:
            logger.error(f"Error getting question from database: {e}")
            # إرجاع سؤال افتراضي في حالة حدوث خطأ
            return Question("ما هي عاصمة المملكة العربية السعودية؟", "الرياض", "جغرافيا")
    
    def get_random_funny_response(self, score, is_team=False):
        """
        الحصول على رد طقطقة عشوائي مناسب
        
        Args:
            score: النقاط المحققة
            is_team: هل الرد للفريق أم لفرد
        
        Returns:
            str: نص رد الطقطقة
        """
        try:
            with app.app_context():
                # جلب رد طقطقة عشوائي مناسب للنقاط
                responses = FunnyResponse.query.filter(
                    FunnyResponse.min_score <= score,
                    FunnyResponse.max_score >= score,
                    FunnyResponse.is_team_response == is_team
                ).all()
                
                if responses:
                    return random.choice(responses).text
                else:
                    # رد افتراضي إذا لم يجد ردود مناسبة
                    return "حاول مرة أخرى!" if not is_team else "فريق الخسرانين!"
                
        except Exception as e:
            logger.error(f"Error getting funny response: {e}")
            return "حاول مرة أخرى!" if not is_team else "فريق الخسرانين!"
    
    async def ask_next_question(self):
        """Ask the next question"""
        logger.debug(f"Asking next question: question_count={self.question_count}, max_questions={self.max_questions}")
        if self.question_count >= self.max_questions:
            logger.debug("Reached max questions, ending game")
            await self.end_game("انتهت الأسئلة!")
            return
        
        self.question_count += 1
        logger.debug(f"Incremented question count to {self.question_count}")
        
        # على المسألة الأخيرة، يجب أن يكون السؤال من نوع دووم
        if self.question_count == self.max_questions:
            self.is_doom_question = True
            self.current_question = self.get_random_question("doom")
            await self.channel.send("⚠️ سؤال دووم! اجابة صح = ضعف النقاط، خطأ = صفر")
            
            if self.mode == GameMode.TEAM:
                # القادة يحتاجون اتخاذ قرار
                self.doom_decision_required = True
                await self.channel.send("قادة الفريق: 1 للقبول، 2 للرفض")
                self.state = GameState.WAITING_FOR_DECISION
                return
        # الأسئلة الاعتيادية
        elif self.is_test_of_fate:
            # مواصلة أسئلة اختبار المصير
            if self.test_of_fate_index < len(self.test_of_fate_questions):
                self.current_question = self.test_of_fate_questions[self.test_of_fate_index]
                self.test_of_fate_index += 1
            else:
                self.is_test_of_fate = False
                self.current_question = self.get_random_question()
        else:
            # اختيار نوع السؤال بناءً على رقم السؤال الحالي
            random_val = random.random()
            
            # الأسئلة الخاصة تظهر بالترتيب بعد الأسئلة العادية في النصف الثاني من اللعبة
            # حتى تضمن عدم ظهورها في البداية
            special_question_threshold = (self.max_questions / 2)
            
            # السؤال الذهبي يظهر فقط في منتصف اللعبة
            if self.question_count == int(self.max_questions / 2) and not self.has_golden_question_appeared:
                logger.debug(f"Showing golden question at question number {self.question_count} (max: {self.max_questions})")
                self.is_golden_question = True
                self.has_golden_question_appeared = True
                self.current_question = self.get_random_question("golden")
                await self.channel.send("✨ سؤال ذهبي +50 نقطة!")
            
            # سؤال الزرف يظهر فقط في وضع تيم وبعد الأسئلة العادية أيضاً
            elif self.question_count > special_question_threshold and not self.is_doom_question and not self.is_golden_question and self.mode == GameMode.TEAM and not self.has_steal_question_appeared and self.question_count > 3:  
                logger.debug(f"Showing steal question at question number {self.question_count} (max: {self.max_questions})")
                self.is_steal_question = True
                self.has_steal_question_appeared = True  # تعليم أن سؤال الزرف قد ظهر
                self.current_question = self.get_random_question("steal")
                await self.channel.send("🔄 سؤال زرف! اكتب 'زرف' قبل الإجابة لخصم نقاط من الفريق الآخر أو 'زود' لمضاعفة نقاطك!")
            
            # اختبار المصير يظهر فقط بعد الأسئلة العادية
            elif self.question_count > special_question_threshold and not self.is_doom_question and not self.is_golden_question and not self.is_steal_question and not self.has_test_of_fate_appeared and self.question_count > 3:
                logger.debug(f"Showing test of fate at question number {self.question_count} (max: {self.max_questions})")
                self.is_test_of_fate = True
                self.has_test_of_fate_appeared = True  # تعليم أن اختبار المصير قد ظهر
                self.test_of_fate_questions = [self.get_random_question() for _ in range(5)]
                self.test_of_fate_index = 0
                self.current_question = self.test_of_fate_questions[self.test_of_fate_index]
                self.test_of_fate_index += 1
                await self.channel.send("🔥 اختبار المصير! 5 أسئلة متتالية. كل إجابة صحيحة: +10 نقاط. كل إجابة خاطئة: -5 نقاط.")
            
            else:
                # سؤال عادي
                self.current_question = self.get_random_question()
        
        # Ask the current question
        self.current_question.ask()
        await self.channel.send(f"السؤال {self.question_count}/{self.max_questions}: {self.current_question.text}")
        
        # Set the state to waiting for answer
        self.state = GameState.WAITING_FOR_ANSWER
        
        # Create a task to handle timeout for answers
        self.answer_task = asyncio.create_task(self.handle_answer_timeout())
    
    async def handle_answer_timeout(self):
        """Handle timeout for answers"""
        await asyncio.sleep(10)  # وقت الإجابة 10 ثوانٍ فقط
        
        if self.state == GameState.WAITING_FOR_ANSWER:
            await self.channel.send(f"انتهى الوقت! الإجابة الصحيحة هي: {self.current_question.answer}")
            
            # Reset special question flags
            self.is_golden_question = False
            self.is_steal_question = False
            self.is_doom_question = False
            
            # إضافة فاصل زمني قصير قبل طرح السؤال التالي
            await asyncio.sleep(1.5)
            
            # If we're in test of fate mode, continue with the next question
            if self.is_test_of_fate and self.test_of_fate_index < len(self.test_of_fate_questions):
                await self.ask_next_question()
            elif self.is_test_of_fate and self.test_of_fate_index >= len(self.test_of_fate_questions):
                self.is_test_of_fate = False
                await self.channel.send("انتهى اختبار المصير!")
                await self.ask_next_question()
            else:
                await self.ask_next_question()
    
    async def process_message(self, message):
        """Process a message during the game"""
        content = message.content.strip()
        username = message.author.name
        user_id = message.author.id
        
        # Registration phase
        if self.state == GameState.REGISTRATION:
            # تحديد عدد الأسئلة في وضع اتحداك
            if self.mode == GameMode.SOLO and self.waiting_for_question_count:
                try:
                    question_count = int(content.strip())
                    if 5 <= question_count <= 10:
                        self.max_questions = question_count
                        self.waiting_for_question_count = False
                        
                        # تسجيل اللاعب وبدء اللعبة
                        self.players[username] = Player(username, user_id)
                        await self.channel.send(f"{username} تم تحديد {question_count} أسئلة. اللعبة ستبدأ الآن. تذكر أن لديك 10 ثوانٍ فقط للإجابة على كل سؤال!")
                        
                        # إضافة مهلة 5 ثوانٍ للسماح للاعب بقراءة الرسائل
                        logger.debug(f"Waiting 5 seconds before starting the game for player {username}")
                        await asyncio.sleep(5)
                        
                        # بدء اللعبة بعد المهلة
                        await self.start_game()
                    else:
                        await self.channel.send("الرجاء إدخال رقم بين 5 و 10.")
                except ValueError:
                    await self.channel.send("الرجاء إدخال رقم صحيح بين 5 و 10.")
            
            # الطريقة القديمة للبدء باستخدام R
            elif self.mode == GameMode.SOLO and content.lower() == "r":
                # Add the solo player
                self.players[username] = Player(username, user_id)
                await self.channel.send(f"{username} مستعد للعب! اللعبة ستبدأ الآن. تذكر أن لديك 10 ثوانٍ فقط للإجابة على كل سؤال!")
                
                # إضافة مهلة 5 ثوانٍ للسماح للاعب بقراءة الرسائل
                logger.debug(f"Waiting 5 seconds before starting the game for player {username}")
                await asyncio.sleep(5)
                
                # Cancel registration task and start the game
                if self.registration_task:
                    self.registration_task.cancel()
                await self.start_game()
            
            elif self.mode == GameMode.GROUP and content.lower() == "r":
                # Add the player to the group
                if username not in self.players:
                    self.players[username] = Player(username, user_id)
                    await self.channel.send(f"{username} تم تسجيلك!")
            
            elif self.mode == GameMode.TEAM:
                if content in ["أحمر", "احمر"]:
                    # Add player to red team
                    if username not in self.players:
                        player = Player(username, user_id)
                        self.players[username] = player
                        self.teams["أحمر"].add_player(player)
                        await self.channel.send(f"{username} انضممت للفريق الأحمر!")
                
                elif content in ["أزرق", "ازرق"]:
                    # Add player to blue team
                    if username not in self.players:
                        player = Player(username, user_id)
                        self.players[username] = player
                        self.teams["أزرق"].add_player(player)
                        await self.channel.send(f"{username} انضممت للفريق الأزرق!")
        
        # Leader selection phase
        elif self.state == GameState.LEADER_SELECTION:
            if content.startswith('@'):
                # Extract the username from the mention
                mentioned_username = content[1:].strip().lower()
                
                # Check if the mentioned user is in the team
                for team_name in ["أحمر", "أزرق"]:
                    if self.teams[team_name].leader is None:  # This team needs a leader
                        for player in self.teams[team_name].players:
                            if player.username.lower() == mentioned_username:
                                self.teams[team_name].set_leader(player)
                                await self.channel.send(f"{player.username} تم تعيينك كقائد للفريق {team_name}!")
                                
                                # If red team leader was selected, now select blue team leader
                                if team_name == "أحمر":
                                    if self.registration_task:
                                        self.registration_task.cancel()
                                    await self.channel.send("اكتب '@username' لاختيار قائد للفريق الأزرق.")
                                    self.registration_task = asyncio.create_task(self.wait_for_leader_selection("أزرق"))
                                
                                # If blue team leader was selected, start the game
                                elif team_name == "أزرق":
                                    if self.registration_task:
                                        self.registration_task.cancel()
                                    # إضافة مهلة 5 ثوانٍ للسماح للاعب بقراءة الرسائل
                                    await self.channel.send("اللعبة ستبدأ خلال 5 ثوانٍ. تذكر أن لديك 10 ثوانٍ فقط للإجابة على كل سؤال!")
                                    logger.debug("Waiting 5 seconds before starting the team game")
                                    await asyncio.sleep(5)
                                    await self.start_game()
                                
                                return
        
        # Waiting for doom question decision
        elif self.state == GameState.WAITING_FOR_DECISION:
            if self.mode == GameMode.TEAM and self.doom_decision_required:
                # Check if message is from a team leader
                is_leader = False
                leader_team = None
                
                for team_name in ["أحمر", "أزرق"]:
                    if self.teams[team_name].leader and self.teams[team_name].leader.username == username:
                        is_leader = True
                        leader_team = team_name
                        break
                
                if is_leader:
                    if content == "1":  # Accept the doom question
                        await self.channel.send(f"فريق {leader_team} قبل التحدي! إليكم السؤال، تذكروا: الإجابة الصحيحة تضاعف النقاط، والإجابة الخاطئة تفقدكم كل النقاط!")
                        self.doom_decision_required = False
                        self.state = GameState.WAITING_FOR_ANSWER
                    
                    elif content == "2":  # Reject the doom question
                        await self.channel.send(f"فريق {leader_team} رفض التحدي. سأطرح سؤالًا عاديًا.")
                        self.is_doom_question = False
                        self.doom_decision_required = False
                        await self.ask_next_question()
        
        # Waiting for answer phase
        elif self.state == GameState.WAITING_FOR_ANSWER:
            # For steal question in team mode
            if self.is_steal_question and self.mode == GameMode.TEAM:
                if content.lower() == "زرف" or content.lower() == "زود":
                    # Record the player's choice for steal or boost
                    player = self.players.get(username)
                    if player:
                        self.steal_player = player
                        self.steal_type = "زرف" if content.lower() == "زرف" else "زود"
                        
                        player_team = player.team
                        await self.channel.send(f"{username} اختار {self.steal_type}!")
                    
                    return  # Wait for the actual answer
            
            # Check if the answer is correct
            if self.current_question and self.current_question.is_correct(content):
                # Cancel the timeout task
                if self.answer_task:
                    self.answer_task.cancel()
                
                response_time = self.current_question.get_response_time()
                points = 10 if response_time <= 5 else 5
                
                # Apply special question modifiers
                if self.is_golden_question:
                    points = 50
                elif self.is_doom_question:
                    points *= 2
                
                # Handle the correct answer based on game mode
                if self.mode == GameMode.SOLO or self.mode == GameMode.GROUP:
                    player = self.players.get(username)
                    if player:
                        # Add points
                        player.add_score(points)
                        
                        # Check for consecutive answers bonus
                        got_bonus = player.add_consecutive()
                        
                        bonus_msg = " وحصلت على بونص سلسلة 10 نقاط إضافية!" if got_bonus else ""
                        await self.channel.send(f"إجابة صحيحة، {username}! +{points} نقطة.{bonus_msg}")
                    else:
                        # New player joined during the game (only in GROUP mode)
                        if self.mode == GameMode.GROUP:
                            player = Player(username, user_id)
                            self.players[username] = player
                            player.add_score(points)
                            await self.channel.send(f"إجابة صحيحة، {username}! +{points} نقطة. (لاعب جديد)")
                
                elif self.mode == GameMode.TEAM:
                    player = self.players.get(username)
                    if player:
                        team_name = player.team
                        team = self.teams.get(team_name)
                        
                        if team:
                            # Handle steal question
                            if self.is_steal_question and self.steal_player and self.steal_player.username == username:
                                if self.steal_type == "زرف":
                                    # Leader needs to choose who to steal from
                                    await self.channel.send(f"قائد فريق {team_name}، اختر لاعب من الفريق الآخر لخصم {points} نقطة منه. اكتب '@username'.")
                                    self.state = GameState.WAITING_FOR_DECISION
                                    self.steal_target = None
                                    return
                                elif self.steal_type == "زود":
                                    # Double the points
                                    points *= 2
                                    await self.channel.send(f"تم مضاعفة النقاط! +{points} نقطة لفريق {team_name}!")
                            
                            # Add points to team score
                            team.add_score(points)
                            player.add_score(points)  # Also track individual score
                            
                            # Check for consecutive answers bonus
                            got_bonus = player.add_consecutive()
                            if got_bonus:
                                team.add_score(10)  # Add bonus to team score
                                await self.channel.send(f"إجابة صحيحة، {username}! +{points} نقطة لفريق {team_name}. وحصلت على بونص سلسلة 10 نقاط إضافية!")
                            else:
                                await self.channel.send(f"إجابة صحيحة، {username}! +{points} نقطة لفريق {team_name}.")
                
                # Reset special question flags
                self.is_golden_question = False
                self.is_steal_question = False
                self.is_doom_question = False
                self.steal_player = None
                
                # If we're in test of fate mode, continue with the next question
                if self.is_test_of_fate and self.test_of_fate_index < len(self.test_of_fate_questions):
                    await self.ask_next_question()
                elif self.is_test_of_fate and self.test_of_fate_index >= len(self.test_of_fate_questions):
                    self.is_test_of_fate = False
                    await self.channel.send("انتهى اختبار المصير!")
                    await self.ask_next_question()
                else:
                    await self.ask_next_question()
            
            # Wrong answer in test of fate
            elif self.is_test_of_fate and not self.current_question.is_correct(content):
                player = self.players.get(username)
                if player:
                    # Deduct points for wrong answer in test of fate
                    player.add_score(-5)
                    player.reset_consecutive()
                    
                    if self.mode == GameMode.TEAM:
                        team = self.teams.get(player.team)
                        if team:
                            team.add_score(-5)
                            await self.channel.send(f"إجابة خاطئة، {username}! -5 نقاط من فريق {player.team}.")
                    else:
                        await self.channel.send(f"إجابة خاطئة، {username}! -5 نقاط.")
            
            # Wrong answer in doom question
            elif self.is_doom_question and not self.current_question.is_correct(content):
                player = self.players.get(username)
                if player and self.mode == GameMode.TEAM:
                    team = self.teams.get(player.team)
                    if team:
                        # Team loses all points
                        old_score = team.get_total_score()
                        team.score = 0
                        await self.channel.send(f"إجابة خاطئة في سؤال الدووم! فريق {player.team} فقد جميع نقاطه ({old_score} نقطة)!")
                        
                        # Reset doom question flag
                        self.is_doom_question = False
                        
                        # Ask next question
                        await self.ask_next_question()
            
            # For other wrong answers, just reset consecutive counter but continue waiting
            elif not self.current_question.is_correct(content):
                player = self.players.get(username)
                if player:
                    player.reset_consecutive()
        
        # During steal decision (team leader picking who to steal from)
        elif self.state == GameState.WAITING_FOR_DECISION and self.steal_player:
            # Check if message is from the team leader
            team_name = self.steal_player.team
            team = self.teams.get(team_name)
            
            if team and team.leader and team.leader.username == username:
                if content.startswith('@'):
                    # Extract the username from the mention
                    mentioned_username = content[1:].strip().lower()
                    
                    # Find the player in the opposing team
                    opposing_team_name = "أزرق" if team_name == "أحمر" else "أحمر"
                    opposing_team = self.teams.get(opposing_team_name)
                    
                    for player in opposing_team.players:
                        if player.username.lower() == mentioned_username:
                            # Found the player to steal from
                            points_to_steal = 10  # Default steal amount
                            
                            # Steal points from player and team
                            player.score = max(0, player.score - points_to_steal)
                            opposing_team.score = max(0, opposing_team.score - points_to_steal)
                            
                            # Add points to stealer's team
                            team.score += points_to_steal
                            
                            await self.channel.send(f"تم خصم {points_to_steal} نقطة من {player.username} وإضافتها لفريق {team_name}!")
                            
                            # Reset steal variables
                            self.steal_player = None
                            self.state = GameState.RUNNING
                            
                            # Ask next question
                            await self.ask_next_question()
                            return
                    
                    # Player not found in opposing team
                    await self.channel.send(f"لم يتم العثور على اللاعب {mentioned_username} في الفريق المنافس.")
    
    async def end_game(self, reason="انتهت اللعبة!"):
        """End the game and announce winners"""
        logger.debug(f"Ending game. Reason: {reason}")
        self.state = GameState.FINISHED
        self.is_active = False
        self.end_time = time.time()
        
        await self.channel.send(reason)
        
        channel_name = self.channel.name.lower()
        # إزالة اللعبة من القائمة النشطة
        try:
            # Import locally to avoid circular import
            from bot import active_games
            if channel_name in active_games:
                logger.debug(f"Removing game from active_games dictionary for channel {channel_name}")
                del active_games[channel_name]
        except Exception as e:
            logger.error(f"Error removing game from active_games: {e}")
        
        # إضافة إعلان الفائزين للوضعين الآخرين
        if self.mode == GameMode.SOLO:
            player = list(self.players.values())[0]
            await self.channel.send(f"نتيجتك النهائية: {player.score} نقطة")
            if player.score < 30:
                funny_response = self.get_random_funny_response(player.score)
                await self.channel.send(f"{player.username}: {funny_response}")
            
        elif self.mode == GameMode.GROUP:
            # Sort players by score
            sorted_players = sorted(self.players.values(), key=lambda x: x.score, reverse=True)
            
            # Announce top 3 players
            await self.channel.send("🏆 النتائج النهائية 🏆")
            
            for i, player in enumerate(sorted_players[:3]):
                medals = ["🥇", "🥈", "🥉"]
                medal = medals[i] if i < 3 else ""
                await self.channel.send(f"{medal} المركز {i+1}: {player.username} - {player.score} نقطة")
            
            # رسائل تشجيعية للاعبين ذوي النقاط المنخفضة
            low_scorers = [p for p in sorted_players if p.score < 50]
            if low_scorers:
                await self.channel.send("رسائل تشجيعية للاعبين:")
                for player in low_scorers:
                    await self.channel.send(f"{player.username}: زين باقي معك شوية عقل يمشي أمورك")
        
        elif self.mode == GameMode.TEAM:
            # Get team scores
            red_score = self.teams["أحمر"].get_total_score()
            blue_score = self.teams["أزرق"].get_total_score()
            
            await self.channel.send(f"🏆 النتائج النهائية 🏆")
            await self.channel.send(f"الفريق الأحمر: {red_score} نقطة")
            await self.channel.send(f"الفريق الأزرق: {blue_score} نقطة")
            
            # Announce winner
            if red_score > blue_score:
                await self.channel.send("🎉 الفريق الأحمر هو الفائز! 🎉")
                await self.channel.send("رسالة للفريق الأزرق: حظ أوفر في المرة القادمة! 😅")
            elif blue_score > red_score:
                await self.channel.send("🎉 الفريق الأزرق هو الفائز! 🎉")
                await self.channel.send("رسالة للفريق الأحمر: حظ أوفر في المرة القادمة! 😅")
            else:
                await self.channel.send("🎉 تعادل! كلا الفريقين فائز! 🎉")
