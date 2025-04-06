import asyncio
import random
from config import (
    REGISTRATION_TIMEOUT_TEAM, REGISTRATION_TIMEOUT_CHALLENGE,
    LEADER_SELECTION_TIMEOUT, MIN_PLAYERS_CHALLENGE, MIN_PLAYERS_TEAM,
    LOSER_MESSAGES, WINNER_MESSAGES, DEFAULT_QUESTION_COUNT,
    MIN_QUESTIONS, MAX_QUESTIONS_TEAM, MAX_QUESTIONS_SOLO,
    LOSER_LEADER_MESSAGES, LOSER_TEAM_MESSAGES, LOW_SCORE_MESSAGES,
    INDIVIDUAL_PRAISE_MESSAGES, TEAM_PRAISE_MESSAGES
)

class GameState:
    def __init__(self):
        self.game_active = False
        self.game_mode = None
        
        # Solo mode attributes
        self.player_points = {}
        self.consecutive_correct = {}
        
        # Challenge mode attributes
        self.players = []
        
        # Team mode attributes
        self.red_team = []
        self.blue_team = []
        self.red_team_points = 0
        self.blue_team_points = 0
        self.red_leader = None
        self.blue_leader = None
        self.player_individual_points = {}
        
        # Game outcome tracking
        self.game_over = False  # يصبح True عندما تنتهي اللعبة قبل الوقت (مثلاً بسبب خسارة سؤال الدوم)
        self.winning_team = None  # يخزن اسم الفريق الفائز ("red" أو "blue")
        
        # Game configuration
        self.question_count = DEFAULT_QUESTION_COUNT

    def reset(self):
        """Reset the game state for a new game"""
        self.game_active = False
        self.game_mode = None
        self.player_points = {}
        self.consecutive_correct = {}
        self.players = []
        self.red_team = []
        self.blue_team = []
        self.red_team_points = 0
        self.blue_team_points = 0
        self.red_leader = None
        self.blue_leader = None
        self.player_individual_points = {}
        self.game_over = False  # تعيين متغير انتهاء اللعبة قبل الوقت
        self.winning_team = None  # تعيين متغير الفريق الفائز
        self.question_count = DEFAULT_QUESTION_COUNT

class GameManager:
    def __init__(self, bot):
        self.bot = bot
        self.state = GameState()
        
    async def start_game(self, ctx, game_mode):
        """Start a new game with the specified game mode"""
        if self.state.game_active:
            await ctx.send("هناك لعبة جارية بالفعل! انتظر حتى تنتهي أو استخدم أمر إيقاف اللعبة.")
            return False
        
        self.state.reset()
        self.state.game_mode = game_mode
        self.state.game_active = True
        
        await ctx.send(f"بدء لعبة جديدة بوضع: {game_mode}")
        
        if game_mode == "فردي":
            await self._setup_solo_mode(ctx)
        elif game_mode == "تحدي":
            success = await self._setup_challenge_mode(ctx)
            if not success:
                self.state.reset()
                return False
        elif game_mode == "تيم":
            success = await self._setup_team_mode(ctx)
            if not success:
                self.state.reset()
                return False
        
        return True
    
    async def _setup_solo_mode(self, ctx):
        """Setup for the solo game mode"""
        await ctx.send("تم بدء وضع اللعب الفردي!")
        await ctx.send(f"حدد عدد الأسئلة من {MIN_QUESTIONS} إلى {MAX_QUESTIONS_SOLO}:")
        
        def check_question_count(message):
            return message.content.isdigit() and MIN_QUESTIONS <= int(message.content) <= MAX_QUESTIONS_SOLO
        
        try:
            message = await self.bot.wait_for('message', timeout=15, check=check_question_count)
            self.state.question_count = int(message.content)
            await ctx.send(f"تم تحديد عدد الأسئلة: {self.state.question_count}")
        except asyncio.TimeoutError:
            await ctx.send(f"لم يتم تحديد عدد الأسئلة، سيتم استخدام العدد الافتراضي: {DEFAULT_QUESTION_COUNT}")
            self.state.question_count = DEFAULT_QUESTION_COUNT
    
    async def _setup_challenge_mode(self, ctx):
        """Setup for the challenge game mode"""
        await ctx.send(f"وضع التحدي! لاعب ضد لاعب.")
        await ctx.send(f"على كل لاعب كتابة 'R' للتسجيل خلال {REGISTRATION_TIMEOUT_CHALLENGE} ثانية.")
        
        self.state.players = []
        
        # Function to check if a message is a registration
        def check_registration(message):
            return message.content.upper() == 'R'
        
        registration_end_time = asyncio.get_event_loop().time() + REGISTRATION_TIMEOUT_CHALLENGE
        
        while asyncio.get_event_loop().time() < registration_end_time:
            remaining_time = registration_end_time - asyncio.get_event_loop().time()
            
            try:
                message = await self.bot.wait_for('message', timeout=remaining_time, check=check_registration)
                
                if message.author.name not in self.state.players:
                    self.state.players.append(message.author.name)
                    self.state.player_points[message.author.name] = 0
                    self.state.consecutive_correct[message.author.name] = 0
                    await ctx.send(f"{message.author.name} تم تسجيله في اللعبة!")
            
            except asyncio.TimeoutError:
                break
        
        # Check if we have enough players
        if len(self.state.players) < MIN_PLAYERS_CHALLENGE:
            await ctx.send(f"لا يوجد عدد كافٍ من اللاعبين ({len(self.state.players)}). يجب أن يكون هناك {MIN_PLAYERS_CHALLENGE} لاعبين على الأقل.")
            return False
        
        await ctx.send(f"تم تسجيل {len(self.state.players)} لاعبين: {', '.join(self.state.players)}")
        
        # Set the question count
        await ctx.send(f"حدد عدد الأسئلة من {MIN_QUESTIONS} إلى {MAX_QUESTIONS_SOLO}:")
        
        def check_question_count(message):
            return message.content.isdigit() and MIN_QUESTIONS <= int(message.content) <= MAX_QUESTIONS_SOLO
        
        try:
            message = await self.bot.wait_for('message', timeout=15, check=check_question_count)
            self.state.question_count = int(message.content)
            await ctx.send(f"تم تحديد عدد الأسئلة: {self.state.question_count}")
        except asyncio.TimeoutError:
            await ctx.send(f"لم يتم تحديد عدد الأسئلة، سيتم استخدام العدد الافتراضي: {DEFAULT_QUESTION_COUNT}")
            self.state.question_count = DEFAULT_QUESTION_COUNT
        
        return True
    
    async def _setup_team_mode(self, ctx):
        """Setup for the team game mode"""
        await ctx.send("وضع الفرق! فريقين يتنافسون.")
        await ctx.send(f"على لاعبي الفريق الأزرق كتابة 'أزرق' وعلى لاعبي الفريق الأحمر كتابة 'أحمر' خلال {REGISTRATION_TIMEOUT_TEAM} ثانية.")
        
        self.state.red_team = []
        self.state.blue_team = []
        
        # Function to check if a message is a team registration
        def check_team_registration(message):
            return message.content in ["أحمر", "أزرق", "احمر", "ازرق"]
        
        registration_end_time = asyncio.get_event_loop().time() + REGISTRATION_TIMEOUT_TEAM
        
        while asyncio.get_event_loop().time() < registration_end_time:
            remaining_time = registration_end_time - asyncio.get_event_loop().time()
            
            try:
                message = await self.bot.wait_for('message', timeout=remaining_time, check=check_team_registration)
                
                if (message.content == "أحمر" or message.content == "احمر") and message.author.name not in self.state.red_team and message.author.name not in self.state.blue_team:
                    self.state.red_team.append(message.author.name)
                    await ctx.send(f"{message.author.name} انضم إلى الفريق الأحمر!")
                
                elif (message.content == "أزرق" or message.content == "ازرق") and message.author.name not in self.state.blue_team and message.author.name not in self.state.red_team:
                    self.state.blue_team.append(message.author.name)
                    await ctx.send(f"{message.author.name} انضم إلى الفريق الأزرق!")
            
            except asyncio.TimeoutError:
                break
        
        # Check if teams have enough players
        if len(self.state.red_team) < MIN_PLAYERS_TEAM or len(self.state.blue_team) < MIN_PLAYERS_TEAM:
            await ctx.send(f"لا يوجد عدد كافٍ من اللاعبين في أحد الفريقين أو كليهما. يجب أن يكون هناك {MIN_PLAYERS_TEAM} لاعبين على الأقل في كل فريق.")
            await ctx.send(f"الفريق الأحمر: {len(self.state.red_team)} لاعبين")
            await ctx.send(f"الفريق الأزرق: {len(self.state.blue_team)} لاعبين")
            return False
        
        await ctx.send(f"الفريق الأحمر ({len(self.state.red_team)} لاعبين): {', '.join(self.state.red_team)}")
        await ctx.send(f"الفريق الأزرق ({len(self.state.blue_team)} لاعبين): {', '.join(self.state.blue_team)}")
        
        # Select team leaders
        await self._select_team_leaders(ctx)
        
        # Set the question count
        await ctx.send(f"حدد عدد الأسئلة العادية من {MIN_QUESTIONS} إلى {MAX_QUESTIONS_TEAM}:")
        
        def check_question_count(message):
            return message.content.isdigit() and MIN_QUESTIONS <= int(message.content) <= MAX_QUESTIONS_TEAM
        
        try:
            message = await self.bot.wait_for('message', timeout=15, check=check_question_count)
            self.state.question_count = int(message.content)
            await ctx.send(f"تم تحديد عدد الأسئلة: {self.state.question_count}")
        except asyncio.TimeoutError:
            await ctx.send(f"لم يتم تحديد عدد الأسئلة، سيتم استخدام العدد الافتراضي: {DEFAULT_QUESTION_COUNT}")
            self.state.question_count = DEFAULT_QUESTION_COUNT
        
        return True
    
    async def _select_team_leaders(self, ctx):
        """Select leaders for each team"""
        await ctx.send("الآن، يجب اختيار قائد لكل فريق! قم بمنشن شخص من فريقك ليكون القائد.")
        await ctx.send(f"لديكم {LEADER_SELECTION_TIMEOUT} ثوانٍ لاختيار القادة.")
        
        # Wait for leader selections
        def check_leader_selection(message):
            # Check if the message mentions someone
            if not message.mentions:
                return False
            
            mentioned_user = message.mentions[0].name
            
            # Check if the author and mentioned user are in the same team
            if message.author.name in self.state.red_team and mentioned_user in self.state.red_team:
                return True
            elif message.author.name in self.state.blue_team and mentioned_user in self.state.blue_team:
                return True
            
            return False
        
        selection_end_time = asyncio.get_event_loop().time() + LEADER_SELECTION_TIMEOUT
        
        while (self.state.red_leader is None or self.state.blue_leader is None) and asyncio.get_event_loop().time() < selection_end_time:
            remaining_time = selection_end_time - asyncio.get_event_loop().time()
            
            try:
                message = await self.bot.wait_for('message', timeout=remaining_time, check=check_leader_selection)
                
                mentioned_user = message.mentions[0].name
                
                if message.author.name in self.state.red_team and self.state.red_leader is None:
                    self.state.red_leader = mentioned_user
                    await ctx.send(f"{mentioned_user} تم اختياره كقائد للفريق الأحمر!")
                
                elif message.author.name in self.state.blue_team and self.state.blue_leader is None:
                    self.state.blue_leader = mentioned_user
                    await ctx.send(f"{mentioned_user} تم اختياره كقائد للفريق الأزرق!")
            
            except asyncio.TimeoutError:
                break
        
        # If no leaders were selected, choose random ones
        if self.state.red_leader is None:
            self.state.red_leader = random.choice(self.state.red_team)
            await ctx.send(f"لم يتم اختيار قائد للفريق الأحمر، تم اختيار {self.state.red_leader} عشوائيًا!")
        
        if self.state.blue_leader is None:
            self.state.blue_leader = random.choice(self.state.blue_team)
            await ctx.send(f"لم يتم اختيار قائد للفريق الأزرق، تم اختيار {self.state.blue_leader} عشوائيًا!")
    
    def update_consecutive_correct(self, player_name, correct):
        """Update the consecutive correct answers count for a player"""
        if correct:
            self.state.consecutive_correct[player_name] = self.state.consecutive_correct.get(player_name, 0) + 1
            streak_count = self.state.consecutive_correct[player_name]
            
            # Check for bonus after consecutive correct answers
            if streak_count == 3:
                bonus = 10
                self.state.player_points[player_name] = self.state.player_points.get(player_name, 0) + bonus
                return (True, streak_count, bonus)
            elif streak_count == 6:
                bonus = 20
                self.state.player_points[player_name] = self.state.player_points.get(player_name, 0) + bonus
                return (True, streak_count, bonus)
            elif streak_count == 10:
                bonus = 40
                self.state.player_points[player_name] = self.state.player_points.get(player_name, 0) + bonus
                return (True, streak_count, bonus)
        else:
            self.state.consecutive_correct[player_name] = 0
        
        return (False, 0, 0)
    
    async def end_game(self, ctx):
        """End the current game and announce results"""
        if not self.state.game_active:
            await ctx.send("لا توجد لعبة جارية حاليًا!")
            return
        
        await ctx.send("🏁🏁🏁 انتهت اللعبة! 🏁🏁🏁")
        
        if self.state.game_mode == "فردي" or self.state.game_mode == "تحدي":
            # Sort players by points
            ranked_players = sorted(self.state.player_points.items(), key=lambda x: x[1], reverse=True)
            
            await ctx.send("🏆 الترتيب النهائي 🏆")
            
            for i, (player, points) in enumerate(ranked_players, 1):
                if i == 1:
                    await ctx.send(f"🥇 المركز الأول: {player} - {points} نقطة")
                    
                    # استخدام رسائل المدح المناسبة للفائز
                    game_type = "solo" if self.state.game_mode == "فردي" else "group"
                    praise_messages = [msg["text"] for msg in INDIVIDUAL_PRAISE_MESSAGES 
                                    if (msg["game_mode"] == game_type or msg["game_mode"] == "all") 
                                    and msg["min_score"] <= points]
                    
                    if praise_messages:
                        await ctx.send(random.choice(praise_messages))
                    else:
                        await ctx.send(random.choice(WINNER_MESSAGES))
                        
                elif i == 2 and len(ranked_players) > 1:
                    await ctx.send(f"🥈 المركز الثاني: {player} - {points} نقطة")
                elif i == 3 and len(ranked_players) > 2:
                    await ctx.send(f"🥉 المركز الثالث: {player} - {points} نقطة")
                else:
                    await ctx.send(f"#{i}: {player} - {points} نقطة")
                
                # إرسال رسائل للاعبين بنقاط أقل من 50
                if points < 50:
                    await ctx.send(f"{player}: {random.choice(LOW_SCORE_MESSAGES)}")
        
        elif self.state.game_mode == "تيم":
            await ctx.send(f"🔴 الفريق الأحمر: {self.state.red_team_points} نقطة")
            await ctx.send(f"🔵 الفريق الأزرق: {self.state.blue_team_points} نقطة")
            
            if self.state.red_team_points > self.state.blue_team_points:
                await ctx.send("🏆 الفريق الأحمر هو الفائز! 🏆")
                
                # مدح الفريق الفائز
                praise_messages = [msg["text"] for msg in TEAM_PRAISE_MESSAGES 
                                if msg["min_score"] <= self.state.red_team_points]
                
                if praise_messages:
                    await ctx.send(random.choice(praise_messages))
                else:
                    await ctx.send(random.choice(WINNER_MESSAGES))
                
                # طقطقة للفريق الخاسر
                await ctx.send(f"الفريق الأزرق: {random.choice(LOSER_TEAM_MESSAGES)}")
                
                # طقطقة لقائد الفريق الخاسر إذا كان الفرق بين النقاط كبير (أكثر من 50 نقطة)
                if (self.state.red_team_points - self.state.blue_team_points) > 50 and self.state.blue_leader:
                    await ctx.send(f"{self.state.blue_leader}: {random.choice(LOSER_LEADER_MESSAGES)}")
                
            elif self.state.blue_team_points > self.state.red_team_points:
                await ctx.send("🏆 الفريق الأزرق هو الفائز! 🏆")
                
                # مدح الفريق الفائز
                praise_messages = [msg["text"] for msg in TEAM_PRAISE_MESSAGES 
                                if msg["min_score"] <= self.state.blue_team_points]
                
                if praise_messages:
                    await ctx.send(random.choice(praise_messages))
                else:
                    await ctx.send(random.choice(WINNER_MESSAGES))
                
                # طقطقة للفريق الخاسر
                await ctx.send(f"الفريق الأحمر: {random.choice(LOSER_TEAM_MESSAGES)}")
                
                # طقطقة لقائد الفريق الخاسر إذا كان الفرق بين النقاط كبير (أكثر من 50 نقطة)
                if (self.state.blue_team_points - self.state.red_team_points) > 50 and self.state.red_leader:
                    await ctx.send(f"{self.state.red_leader}: {random.choice(LOSER_LEADER_MESSAGES)}")
                
            else:
                await ctx.send("🤝 تعادل! كلا الفريقين أحرزا نفس عدد النقاط! 🤝")
        
        # Reset the game state
        self.state.reset()
