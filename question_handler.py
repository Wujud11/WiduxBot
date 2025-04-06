import random
import asyncio
from config import QUESTIONS, QUESTION_TIMEOUT

class QuestionHandler:
    def __init__(self):
        self.questions = QUESTIONS.copy()
        random.shuffle(self.questions)
        self.current_question_index = 0
        self.questions_asked = []

    def reset(self):
        """Reset the question handler for a new game"""
        self.questions = QUESTIONS.copy()
        random.shuffle(self.questions)
        self.current_question_index = 0
        self.questions_asked = []

    def get_next_question(self):
        """Get the next question from the pool"""
        if self.current_question_index >= len(self.questions):
            # If we've gone through all questions, reshuffle
            random.shuffle(self.questions)
            self.current_question_index = 0
        
        question_data = self.questions[self.current_question_index]
        self.current_question_index += 1
        self.questions_asked.append(question_data)
        return question_data

    def get_random_question(self):
        """Get a random question that hasn't been asked yet"""
        available_questions = [q for q in self.questions if q not in self.questions_asked]
        if not available_questions:
            # If all questions have been asked, reset
            available_questions = self.questions
            self.questions_asked = []
        
        question_data = random.choice(available_questions)
        self.questions_asked.append(question_data)
        return question_data

    def check_answer(self, user_answer, correct_answer):
        """Check if the user's answer is correct"""
        # Normalize answers for comparison (lowercase, strip spaces)
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        
        return user_answer == correct_answer

    async def wait_for_answer(self, bot, ctx, question_data, game_state, timeout=QUESTION_TIMEOUT):
        """Wait for an answer to a question within the timeout period"""
        question_text = question_data["question"]
        correct_answer = question_data["answer"]
        
        start_time = asyncio.get_event_loop().time()
        
        # Function to check if a message is a valid answer attempt
        def check_answer(message):
            # Only accept answers from registered players in the current game
            if game_state.game_mode == "فردي":
                return True  # In solo mode, anyone can answer
            
            elif game_state.game_mode == "تحدي":
                return message.author.name in game_state.players
            
            elif game_state.game_mode == "تيم":
                return (message.author.name in game_state.red_team or 
                        message.author.name in game_state.blue_team)
            
            return False
        
        await ctx.send(f"السؤال: {question_text}")
        
        try:
            while True:
                # Calculate remaining time
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining = timeout - elapsed
                
                if remaining <= 0:
                    await ctx.send(f"انتهى الوقت! الإجابة الصحيحة هي: {correct_answer}")
                    return None, None, timeout  # No one answered in time
                
                try:
                    # Wait for a message that could be an answer
                    message = await bot.wait_for('message', timeout=remaining, check=check_answer)
                    
                    # Check if the answer is correct
                    if self.check_answer(message.content, correct_answer):
                        # Calculate how long it took to answer
                        answer_time = asyncio.get_event_loop().time() - start_time
                        
                        # Determine points based on answer time
                        points = 10 if answer_time <= 5 else 5
                        
                        # Don't send message here, we'll do it in the caller to provide more details
                        return message.author.name, points, answer_time
                    
                    # Wrong answer, continue waiting
                except asyncio.TimeoutError:
                    # This inner timeout means no one answered within the remaining time
                    await ctx.send(f"انتهى الوقت! الإجابة الصحيحة هي: {correct_answer}")
                    return None, None, timeout
        
        except Exception as e:
            print(f"Error waiting for answer: {e}")
            await ctx.send(f"حدث خطأ أثناء انتظار الإجابة. الإجابة الصحيحة هي: {correct_answer}")
            return None, None, timeout

    async def handle_golden_question(self, bot, ctx, game_state):
        """Handle a golden question with 50 point reward"""
        question_data = self.get_random_question()
        
        await ctx.send("⭐⭐⭐ Golden Question! ⭐⭐⭐")
        await ctx.send("الإجابة الصحيحة تمنحك 50 نقطة!")
        
        player_name, _, answer_time = await self.wait_for_answer(bot, ctx, question_data, game_state)
        
        if player_name:
            if game_state.game_mode == "فردي":
                game_state.player_points[player_name] = game_state.player_points.get(player_name, 0) + 50
            
            elif game_state.game_mode == "تحدي":
                game_state.player_points[player_name] = game_state.player_points.get(player_name, 0) + 50
            
            elif game_state.game_mode == "تيم":
                # تأكد من وجود قائمة نقاط فردية
                if 'player_individual_points' not in game_state.__dict__:
                    game_state.player_individual_points = {}
                
                if player_name in game_state.red_team:
                    # إضافة النقاط لفريق الأحمر
                    game_state.red_team_points += 50
                    # تسجيل النقاط الفردية للاعب
                    game_state.player_individual_points[player_name] = game_state.player_individual_points.get(player_name, 0) + 50
                    
                    await ctx.send(f"الفريق الأحمر حصل على 50 نقطة إضافية!")
                    await ctx.send(f"⭐ {player_name} حصل على 50 نقطة فردية! لديه الآن {game_state.player_individual_points[player_name]} نقطة ⭐")
                
                elif player_name in game_state.blue_team:
                    # إضافة النقاط لفريق الأزرق
                    game_state.blue_team_points += 50
                    # تسجيل النقاط الفردية للاعب
                    game_state.player_individual_points[player_name] = game_state.player_individual_points.get(player_name, 0) + 50
                    
                    await ctx.send(f"الفريق الأزرق حصل على 50 نقطة إضافية!")
                    await ctx.send(f"⭐ {player_name} حصل على 50 نقطة فردية! لديه الآن {game_state.player_individual_points[player_name]} نقطة ⭐")

    async def handle_test_of_fate(self, bot, ctx, game_state):
        """Handle a Test of Fate series of 5 questions"""
        # اختبار المصير متاح فقط في وضع التحدي والفرق
        if game_state.game_mode == "فردي":
            await ctx.send("The Test of Fate غير متاح في وضع اللعب الفردي!")
            return

        await ctx.send("🔥🔥🔥 The Test of Fate! 🔥🔥🔥")
        await ctx.send("5 أسئلة متتابعة. الإجابة الصحيحة: +10 نقاط. الإجابة الخاطئة: -5 نقاط.")
        await ctx.send("لا يتم خصم نقاط عند انتهاء الوقت بدون إجابة.")
        
        # Initialize temporary points for each player/team
        temp_points = {}
        incorrect_answers = {}  # تتبع الإجابات الخاطئة لكل لاعب
        
        for question_num in range(1, 6):
            question_data = self.get_random_question()
            await ctx.send(f"سؤال {question_num}/5:")
            
            try:
                # قائمة للاعبين الذين أجابوا إجابة خاطئة في هذا السؤال
                wrong_players = []
                
                # انتظار الإجابة لمدة 10 ثوانٍ
                start_time = asyncio.get_event_loop().time()
                correct_player = None
                
                while asyncio.get_event_loop().time() - start_time < 10 and not correct_player:
                    remaining_time = 10 - (asyncio.get_event_loop().time() - start_time)
                    
                    try:
                        def check_answer(message):
                            # تجاهل الرسائل التي تبدأ بـ "!" لأنها قد تكون أوامر للبوت
                            if message.content.startswith('!'):
                                return False
                                
                            # التحقق من اللاعب إذا كان في وضع اللعب المناسب
                            if game_state.game_mode == "تحدي" and message.author.name not in game_state.players:
                                return False
                            
                            if game_state.game_mode == "تيم" and message.author.name not in game_state.red_team and message.author.name not in game_state.blue_team:
                                return False
                                
                            # تجاهل اللاعبين الذين سبق وأجابوا إجابة خاطئة على هذا السؤال
                            if message.author.name in wrong_players:
                                return False
                                
                            return True
                            
                        message = await bot.wait_for('message', timeout=remaining_time, check=check_answer)
                        
                        # التحقق من الإجابة
                        if self.check_answer(message.content, question_data["answer"]):
                            # إجابة صحيحة
                            correct_player = message.author.name
                            temp_points[correct_player] = temp_points.get(correct_player, 0) + 10
                            await ctx.send(f"إجابة صحيحة من {correct_player}! +10 نقاط")
                        else:
                            # إجابة خاطئة، خصم 5 نقاط
                            wrong_player = message.author.name
                            wrong_players.append(wrong_player)
                            incorrect_answers[wrong_player] = incorrect_answers.get(wrong_player, 0) + 1
                            
                            if game_state.game_mode == "تحدي":
                                # خصم 5 نقاط في وضع التحدي
                                game_state.player_points[wrong_player] = max(0, game_state.player_points.get(wrong_player, 0) - 5)
                                await ctx.send(f"إجابة خاطئة من {wrong_player}. -5 نقاط.")
                            elif game_state.game_mode == "تيم":
                                # تحديد الفريق
                                if wrong_player in game_state.red_team:
                                    game_state.red_team_points = max(0, game_state.red_team_points - 5)
                                    await ctx.send(f"إجابة خاطئة من {wrong_player}. -5 نقاط للفريق الأحمر.")
                                elif wrong_player in game_state.blue_team:
                                    game_state.blue_team_points = max(0, game_state.blue_team_points - 5)
                                    await ctx.send(f"إجابة خاطئة من {wrong_player}. -5 نقاط للفريق الأزرق.")
                    
                    except asyncio.TimeoutError:
                        # انتهى الوقت المتبقي، لكن لا زال الوقت الكلي متاحًا
                        continue
                
                # إذا لم يجب أحد إجابة صحيحة
                if not correct_player:
                    await ctx.send(f"لم يجب أحد إجابة صحيحة على هذا السؤال. الإجابة الصحيحة هي: {question_data['answer']}")
            
            except Exception as e:
                print(f"حدث خطأ أثناء معالجة سؤال اختبار المصير: {e}")
                await ctx.send("حدث خطأ أثناء معالجة السؤال. الانتقال إلى السؤال التالي.")
            
            # انتظار قصير بين الأسئلة
            await asyncio.sleep(2)
        
        # تطبيق النتائج النهائية
        if game_state.game_mode == "تحدي":
            # إظهار نتائج النقاط المكتسبة
            for player, points in temp_points.items():
                await ctx.send(f"{player} كسب {points} نقطة من اختبار المصير!")
                
            # إظهار النقاط المخصومة
            for player, count in incorrect_answers.items():
                penalty = min(count * 5, game_state.player_points.get(player, 0))
                if penalty > 0:
                    await ctx.send(f"{player} خسر {penalty} نقطة بسبب الإجابات الخاطئة!")
        
        elif game_state.game_mode == "تيم":
            red_total = 0
            blue_total = 0
            
            # حساب نقاط كل فريق من الإجابات الصحيحة
            for player, points in temp_points.items():
                if player in game_state.red_team:
                    red_total += points
                elif player in game_state.blue_team:
                    blue_total += points
            
            # إظهار النتائج
            if red_total > 0:
                await ctx.send(f"الفريق الأحمر كسب {red_total} نقطة من اختبار المصير!")
            
            if blue_total > 0:
                await ctx.send(f"الفريق الأزرق كسب {blue_total} نقطة من اختبار المصير!")
            
            # حساب إجمالي النقاط بعد اختبار المصير
            await ctx.send(f"نقاط الفريق الأحمر الآن: {game_state.red_team_points}")
            await ctx.send(f"نقاط الفريق الأزرق الآن: {game_state.blue_team_points}")
    
    async def handle_steal_question(self, bot, ctx, game_state):
        """Handle a steal question"""
        if game_state.game_mode == "تحدي":
            await self._handle_steal_challenge(bot, ctx, game_state)
        elif game_state.game_mode == "تيم":
            await self._handle_steal_team(bot, ctx, game_state)
    
    async def _handle_steal_challenge(self, bot, ctx, game_state):
        """Handle steal question in challenge mode"""
        # Randomly select a player to steal points from
        if len(game_state.players) <= 1:
            await ctx.send("لا يوجد لاعبين كافيين للزرف!")
            return
        
        # في حالة وجود لاعبين فقط، اختر اللاعب الآخر
        if len(game_state.players) == 2:
            # اختر اللاعب الذي ليس هو اللاعب الحالي (الذي سيجيب)
            possible_targets = game_state.players.copy()
            # سنختار هدف عشوائي الآن وسنتحقق لاحقًا من أن اللاعب المجيب ليس هو الهدف
            target_player = random.choice(possible_targets)
        else:
            # في حالة وجود أكثر من لاعبين، اختر لاعب عشوائي
            target_player = random.choice(game_state.players)
            
        await ctx.send(f"🎯 Steal Question! 🎯")
        await ctx.send(f"إذا أجبت صحيح، ستزرف كل نقاط اللاعب {target_player}!")
        
        question_data = self.get_random_question()
        player_name, _, _ = await self.wait_for_answer(bot, ctx, question_data, game_state)
        
        if player_name and player_name != target_player:
            # The answering player gets ALL the target's points
            stolen_points = game_state.player_points.get(target_player, 0)
            game_state.player_points[player_name] = game_state.player_points.get(player_name, 0) + stolen_points
            game_state.player_points[target_player] = 0
            
            await ctx.send(f"🔥 {player_name} زرف {stolen_points} نقطة من {target_player}! 🔥")
            await ctx.send(f"تم تصفير نقاط {target_player}! 😱")
    
    async def _handle_steal_team(self, bot, ctx, game_state):
        """Handle steal question in team mode"""
        await ctx.send("🎯 Steal Question! 🎯")
        await ctx.send("الليدر: اختر 'زرف' أو 'زود' قبل السؤال")
        
        choice_red = None
        choice_blue = None
        
        # Wait for leaders to make their choices
        def check_leader_choice(message):
            return (message.author.name == game_state.red_leader and message.content in ["زرف", "زود"]) or \
                   (message.author.name == game_state.blue_leader and message.content in ["زرف", "زود"])
        
        # Give 10 seconds for leaders to choose
        try:
            start_time = asyncio.get_event_loop().time()
            while (choice_red is None or choice_blue is None) and (asyncio.get_event_loop().time() - start_time < 10):
                remaining = 10 - (asyncio.get_event_loop().time() - start_time)
                
                try:
                    message = await bot.wait_for('message', timeout=remaining, check=check_leader_choice)
                    if message.author.name == game_state.red_leader:
                        choice_red = message.content
                        await ctx.send(f"الفريق الأحمر اختار: {choice_red}")
                    elif message.author.name == game_state.blue_leader:
                        choice_blue = message.content
                        await ctx.send(f"الفريق الأزرق اختار: {choice_blue}")
                except asyncio.TimeoutError:
                    break
        
        except Exception as e:
            print(f"Error waiting for leader choices: {e}")
        
        # If leaders didn't choose, assign random choices
        if choice_red is None:
            choice_red = random.choice(["زرف", "زود"])
            await ctx.send(f"الفريق الأحمر لم يختر، سيتم اختيار {choice_red} تلقائيًا")
        
        if choice_blue is None:
            choice_blue = random.choice(["زرف", "زود"])
            await ctx.send(f"الفريق الأزرق لم يختر، سيتم اختيار {choice_blue} تلقائيًا")
        
        # Ask the question
        question_data = self.get_random_question()
        player_name, _, _ = await self.wait_for_answer(bot, ctx, question_data, game_state)
        
        if player_name:
            # Determine which team the answering player belongs to
            if player_name in game_state.red_team:
                winning_team = "red"
                winning_choice = choice_red
                winning_leader = game_state.red_leader
            else:
                winning_team = "blue"
                winning_choice = choice_blue
                winning_leader = game_state.blue_leader
            
            # Execute the chosen action
            if winning_choice == "زرف":
                await ctx.send(f"{winning_leader}: منشن شخص من الفريق المنافس لزرف نقاطه")
                
                # Wait for the leader to mention a player
                def check_mention(message):
                    return message.author.name == winning_leader and len(message.mentions) > 0
                
                try:
                    mention_msg = await bot.wait_for('message', timeout=10, check=check_mention)
                    target_player = mention_msg.mentions[0].name
                    
                    # Check if the target is from the opposing team
                    if (winning_team == "red" and target_player in game_state.blue_team) or \
                       (winning_team == "blue" and target_player in game_state.red_team):
                        
                        # تعديل منطق زرف النقاط ليكون للاعب المحدد فقط
                        # نضيف قائمة فردية لنقاط كل لاعب في وضع التيم إن لم تكن موجودة
                        if 'player_individual_points' not in game_state.__dict__:
                            game_state.player_individual_points = {}
                            
                        # نحصل على نقاط اللاعب المحدد من الفريق المنافس (إن وجدت)
                        target_points = game_state.player_individual_points.get(target_player, 0)
                        
                        if target_points == 0:
                            # إذا لم تكن للاعب نقاط، اجعله يخسر 10 نقاط من فريقه
                            if winning_team == "red":
                                # زرف 10 نقاط من الفريق الأزرق
                                stolen_points = min(10, game_state.blue_team_points)
                                game_state.red_team_points += stolen_points
                                game_state.blue_team_points -= stolen_points
                                await ctx.send(f"الفريق الأحمر زرف {stolen_points} نقطة من الفريق الأزرق لأن {target_player} ليس لديه نقاط فردية!")
                            else:
                                # زرف 10 نقاط من الفريق الأحمر
                                stolen_points = min(10, game_state.red_team_points)
                                game_state.blue_team_points += stolen_points
                                game_state.red_team_points -= stolen_points
                                await ctx.send(f"الفريق الأزرق زرف {stolen_points} نقطة من الفريق الأحمر لأن {target_player} ليس لديه نقاط فردية!")
                        else:
                            # زرف نقاط اللاعب المستهدف
                            if winning_team == "red":
                                # زرف نقاط اللاعب المستهدف من الفريق الأزرق
                                game_state.red_team_points += target_points
                                game_state.blue_team_points -= target_points
                                game_state.player_individual_points[target_player] = 0
                                await ctx.send(f"🔥 الفريق الأحمر زرف {target_points} نقطة من {target_player}! 🔥")
                                await ctx.send(f"تم تصفير نقاط {target_player} الفردية! 😱")
                            else:
                                # زرف نقاط اللاعب المستهدف من الفريق الأحمر
                                game_state.blue_team_points += target_points
                                game_state.red_team_points -= target_points
                                game_state.player_individual_points[target_player] = 0
                                await ctx.send(f"🔥 الفريق الأزرق زرف {target_points} نقطة من {target_player}! 🔥")
                                await ctx.send(f"تم تصفير نقاط {target_player} الفردية! 😱")
                    else:
                        await ctx.send("هذا اللاعب ليس من الفريق المنافس!")
                
                except asyncio.TimeoutError:
                    await ctx.send("انتهى الوقت، لم يتم اختيار لاعب للزرف")
            
            elif winning_choice == "زود":
                # Add random points between 0 and 30
                bonus_points = random.randint(0, 30)
                
                if winning_team == "red":
                    game_state.red_team_points += bonus_points
                    await ctx.send(f"الفريق الأحمر حصل على {bonus_points} نقطة إضافية من الحظ!")
                else:
                    game_state.blue_team_points += bonus_points
                    await ctx.send(f"الفريق الأزرق حصل على {bonus_points} نقطة إضافية من الحظ!")

    async def handle_doom_question(self, bot, ctx, game_state):
        """Handle a Doom question that can double points or lose all points"""
        # سؤال الدوم متاح فقط في وضع التيم
        if game_state.game_mode != "تيم":
            await ctx.send("سؤال Doom متاح فقط في وضع التيم!")
            return
            
        await ctx.send("☠️☠️☠️ Doom Question! ☠️☠️☠️")
        await ctx.send("هذا سؤال Doom لك القرار تجاوب او تنسحب")
        await ctx.send("عند الاجابة الخاطئة او انتهاء الوقت يخسر الفريق كل نقاطه وتنتهي اللعبة")
        await ctx.send("اكتب 1 للقبول أو 2 للرفض")
        
        # متغيرات خاصة باختيارات قادة الفرق
        red_accept = None
        blue_accept = None
        
        # دالة للتحقق من اختيارات قادة الفرق
        def check_leader_choice(message):
            return (message.author.name == game_state.red_leader and message.content in ["1", "2"]) or \
                   (message.author.name == game_state.blue_leader and message.content in ["1", "2"])
        
        # انتظار اختيارات قادة الفرق - 10 ثواني
        try:
            start_time = asyncio.get_event_loop().time()
            timeout_duration = 10
            
            while (red_accept is None or blue_accept is None) and (asyncio.get_event_loop().time() - start_time < timeout_duration):
                remaining = timeout_duration - (asyncio.get_event_loop().time() - start_time)
                
                try:
                    message = await bot.wait_for('message', timeout=remaining, check=check_leader_choice)
                    
                    if message.author.name == game_state.red_leader:
                        red_accept = message.content == "1"
                        await ctx.send(f"الفريق الأحمر {'قبل' if red_accept else 'رفض'} سؤال Doom!")
                    elif message.author.name == game_state.blue_leader:
                        blue_accept = message.content == "1"
                        await ctx.send(f"الفريق الأزرق {'قبل' if blue_accept else 'رفض'} سؤال Doom!")
                
                except asyncio.TimeoutError:
                    # إذا انتهى الوقت ولم يختر أحد القادة، الخروج من الحلقة
                    break
        
        except Exception as e:
            # تسجيل الخطأ للمطورين فقط
            print(f"Error in handle_doom_question: {e}")
        
        # تعيين رفض افتراضي للفرق التي لم تختر
        if red_accept is None:
            red_accept = False
            await ctx.send("الفريق الأحمر لم يرد، سيتم اعتبار ذلك رفضًا")
            
        if blue_accept is None:
            blue_accept = False
            await ctx.send("الفريق الأزرق لم يرد، سيتم اعتبار ذلك رفضًا")
        
        # معالجة سؤال الدوم للفرق التي قبلت التحدي
        if red_accept:
            await self._process_doom_for_team(bot, ctx, game_state, "red")
            
        if blue_accept:
            await self._process_doom_for_team(bot, ctx, game_state, "blue")
            
        # إذا رفض كلا الفريقين، أخبر المستخدمين ونستمر
        if not red_accept and not blue_accept:
            await ctx.send("كلا الفريقين رفضا سؤال Doom! دعونا نستمر!")
    
    async def _process_doom_for_team(self, bot, ctx, game_state, team):
        """Process the doom question for a specific team"""
        question_data = self.get_random_question()
        
        team_name = "الأحمر" if team == "red" else "الأزرق"
        leader_name = game_state.red_leader if team == "red" else game_state.blue_leader
        
        await ctx.send(f"سؤال Doom للفريق {team_name}:")
        await ctx.send(f"فقط {leader_name} يمكنه الإجابة!")
        
        await ctx.send(question_data["question"])
        
        # Only accept answers from the team leader
        def check_leader_answer(message):
            return message.author.name == leader_name
        
        try:
            # Give the leader 10 seconds to answer
            message = await bot.wait_for('message', timeout=10, check=check_leader_answer)
            
            # Check if the answer is correct
            if self.check_answer(message.content, question_data["answer"]):
                # Double the team's points
                if team == "red":
                    game_state.red_team_points *= 2
                    await ctx.send(f"إجابة صحيحة! نقاط الفريق الأحمر تضاعفت إلى {game_state.red_team_points}!")
                else:
                    game_state.blue_team_points *= 2
                    await ctx.send(f"إجابة صحيحة! نقاط الفريق الأزرق تضاعفت إلى {game_state.blue_team_points}!")
            else:
                # Wrong answer, lose all points and end the game (the other team wins)
                if team == "red":
                    game_state.red_team_points = 0
                    await ctx.send(f"إجابة خاطئة! الفريق الأحمر خسر كل نقاطه!")
                    await ctx.send(f"انتهت اللعبة! الفريق الأزرق هو الفائز! 🏆")
                    
                    # إنهاء اللعبة وإعلان الفريق الأزرق كفائز
                    game_state.game_over = True
                    game_state.winning_team = "blue"
                else:
                    game_state.blue_team_points = 0
                    await ctx.send(f"إجابة خاطئة! الفريق الأزرق خسر كل نقاطه!")
                    await ctx.send(f"انتهت اللعبة! الفريق الأحمر هو الفائز! 🏆")
                    
                    # إنهاء اللعبة وإعلان الفريق الأحمر كفائز
                    game_state.game_over = True
                    game_state.winning_team = "red"
                
                await ctx.send(f"الإجابة الصحيحة كانت: {question_data['answer']}")
        
        except asyncio.TimeoutError:
            # Time's up, lose all points and end the game (the other team wins)
            if team == "red":
                game_state.red_team_points = 0
                await ctx.send(f"انتهى الوقت! الفريق الأحمر خسر كل نقاطه!")
                await ctx.send(f"انتهت اللعبة! الفريق الأزرق هو الفائز! 🏆")
                
                # إنهاء اللعبة وإعلان الفريق الأزرق كفائز
                game_state.game_over = True
                game_state.winning_team = "blue"
            else:
                game_state.blue_team_points = 0
                await ctx.send(f"انتهى الوقت! الفريق الأزرق خسر كل نقاطه!")
                await ctx.send(f"انتهت اللعبة! الفريق الأحمر هو الفائز! 🏆")
                
                # إنهاء اللعبة وإعلان الفريق الأحمر كفائز
                game_state.game_over = True
                game_state.winning_team = "red"
            
            await ctx.send(f"الإجابة الصحيحة كانت: {question_data['answer']}")

    async def handle_sabotage_question(self, bot, ctx, game_state):
        """Handle a sabotage question to eliminate a player from the opposing team"""
        if game_state.game_mode != "تيم":
            await ctx.send("سؤال الاستبعاد متاح فقط في وضع التيم!")
            return
        
        await ctx.send("🔥 Sabotage Question! 🔥")
        await ctx.send("اختر شخصًا من الفريق الآخر ترغب في استبعاده من اللعبة، قم بعمل منشن له.")
        
        # Wait for each team to choose a player to sabotage
        red_target = None
        blue_target = None
        
        start_time = asyncio.get_event_loop().time()
        
        # Function to check valid mentions
        def check_valid_mention(message):
            if message.author.name == game_state.red_leader and message.mentions:
                # Red leader should mention someone from blue team
                return message.mentions[0].name in game_state.blue_team
            elif message.author.name == game_state.blue_leader and message.mentions:
                # Blue leader should mention someone from red team
                return message.mentions[0].name in game_state.red_team
            return False
        
        # Give 15 seconds for leaders to make their choices
        while (red_target is None or blue_target is None) and (asyncio.get_event_loop().time() - start_time < 15):
            remaining = 15 - (asyncio.get_event_loop().time() - start_time)
            
            try:
                message = await bot.wait_for('message', timeout=remaining, check=check_valid_mention)
                
                if message.author.name == game_state.red_leader:
                    red_target = message.mentions[0].name
                    await ctx.send(f"الفريق الأحمر اختار استبعاد {red_target} من الفريق الأزرق!")
                elif message.author.name == game_state.blue_leader:
                    blue_target = message.mentions[0].name
                    await ctx.send(f"الفريق الأزرق اختار استبعاد {blue_target} من الفريق الأحمر!")
            
            except asyncio.TimeoutError:
                break
        
        # If a team didn't choose, select random targets
        if red_target is None and game_state.blue_team:
            red_target = random.choice(game_state.blue_team)
            await ctx.send(f"الفريق الأحمر لم يختر، سيتم اختيار {red_target} من الفريق الأزرق عشوائيًا!")
        
        if blue_target is None and game_state.red_team:
            blue_target = random.choice(game_state.red_team)
            await ctx.send(f"الفريق الأزرق لم يختر، سيتم اختيار {blue_target} من الفريق الأحمر عشوائيًا!")
        
        # Now ask the sabotage question
        await ctx.send("الآن، للإجابة على السؤال، أول من يجيب صح سيستبعد اللاعب الذي تم منشنه.")
        
        question_data = self.get_random_question()
        player_name, _, _ = await self.wait_for_answer(bot, ctx, question_data, game_state)
        
        if player_name:
            # Determine which player gets eliminated based on who answered
            if player_name in game_state.red_team and blue_target:
                eliminated_player = blue_target
                elimination_messages = self._get_elimination_messages()
                game_state.blue_team.remove(blue_target)
                await ctx.send(f"{elimination_messages} {eliminated_player} تم استبعاده من الفريق الأزرق!")
            
            elif player_name in game_state.blue_team and red_target:
                eliminated_player = red_target
                elimination_messages = self._get_elimination_messages()
                game_state.red_team.remove(red_target)
                await ctx.send(f"{elimination_messages} {eliminated_player} تم استبعاده من الفريق الأحمر!")
    
    def _get_elimination_messages(self):
        """Get a random elimination message"""
        from config import ELIMINATION_MESSAGES
        return random.choice(ELIMINATION_MESSAGES)
