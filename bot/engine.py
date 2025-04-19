
‏import asyncio
‏import random
‏from collections import defaultdict

‏from bot.questions.normal import TeamNormalQuestion
‏from bot.questions.golden import GoldenQuestion
‏from bot.questions.sabotage import SabotageQuestion
‏from bot.questions.doom import DoomQuestion
‏from bot.questions.fate import TestOfFate
‏from bot.questions.steal_or_boost import ChallengeStealOrBoostQuestion
‏from utils.responses import get_response

‏class WiduxEngine:
‏    def __init__(self, bot):
‏        self.bot = bot
‏        self.players = []
‏        self.blue_team = []
‏        self.red_team = []
‏        self.game_mode = None
‏        self.leader_selection = False
‏        self.blue_mentions = defaultdict(int)
‏        self.red_mentions = defaultdict(int)
‏        self.blue_leader = None
‏        self.red_leader = None
‏        self.main_player = None
‏        self.questions = []
‏        self.current_index = 0
‏        self.selected_game_mode = None
‏        self.waiting_for_normal_count = False
‏        self.points = defaultdict(int)
‏        self.kicked_players = []

‏    async def handle_message(self, message):
‏        content = message.content.strip()
‏        sender = message.author.name

‏        if content == "وج؟":
‏            await message.channel.send("هلا والله! إذا بتلعب لحالك اكتب سولو، إذا ضد الكل اكتب تحدي، وإذا مع ربعك اكتب تيم.")
‏            return

‏        if content in ["سولو", "تحدي", "تيم"] and not self.game_mode and not self.waiting_for_normal_count:
‏            self.selected_game_mode = content
‏            self.main_player = sender
‏            self.waiting_for_normal_count = True
‏            await message.channel.send("حدد عدد الأسئلة العادية من 5 إلى 10.")
‏            return

‏        if self.waiting_for_normal_count and content.isdigit():
‏            count = int(content)
‏            if 5 <= count <= 10:
‏                self.waiting_for_normal_count = False
‏                self.game_mode = self.selected_game_mode

‏                if self.game_mode == "سولو":
‏                    await message.channel.send("جاري بدء اللعبة...")
‏                    await self.start_full_game(message.channel, count)

‏                elif self.game_mode == "تحدي":
‏                    await message.channel.send("اللي بيلعب يكتب 'R' للتسجيل معكم 15 ثانية!")
‏                    await self.register_challenge_players(message.channel, count)

‏                elif self.game_mode == "تيم":
‏                    await message.channel.send("اختر فريقك! اكتب 'B' للأزرق أو 'R' للأحمر! معكم 20 ثانية!")
‏                    await self.register_team_players(message.channel, count)
‏            else:
‏                await message.channel.send("الرجاء اختيار عدد الاسئلة العادية حدد رقم بين 5 و10.")
‏            return

‏        if self.game_mode == "تحدي" and content.strip().upper() == 'R' and sender not in self.players:
‏            self.players.append(sender)

‏        if self.game_mode == "تيم" and not self.leader_selection:
‏            choice = content.strip().upper()

‏            if choice == 'B' and sender not in self.blue_team and sender not in self.red_team:
‏                self.blue_team.append(sender)
‏            elif choice == 'R' and sender not in self.red_team and sender not in self.blue_team:
‏                self.red_team.append(sender)

‏        if self.leader_selection and self.game_mode == "تيم":
‏            mentioned_players = self.extract_mentions(content)
‏            for player in mentioned_players:
‏                if player in self.blue_team:
‏                    self.blue_mentions[player] += 1
‏                elif player in self.red_team:
‏                    self.red_mentions[player] += 1

‏    def extract_mentions(self, text):
‏        mentions = []
‏        words = text.split()
‏        for word in words:
‏            if word.startswith('@'):
‏                mentions.append(word[1:])
‏        return mentions

‏    async def register_challenge_players(self, channel, normal_count):
‏        await asyncio.sleep(15)

‏        if len(self.players) < 2:
‏            await self.reset_game(channel, "ما فيه عدد كافي نبدأ فيه التحدي.")
‏        else:
‏            await channel.send(f"تم تسجيل اللاعبين: {', '.join(self.players)}")
‏            await self.start_full_game(channel, normal_count)

‏    async def register_team_players(self, channel, normal_count):
‏        await asyncio.sleep(20)

‏        if len(self.blue_team) < 3 or len(self.red_team) < 3:
‏            await self.reset_game(channel, "لازم يكون فيه على الأقل ٣ لاعبين في كل فريق.")
‏        else:
‏            await channel.send(f"الفريق الأزرق: {', '.join(self.blue_team)}")
‏            await channel.send(f"الفريق الأحمر: {', '.join(self.red_team)}")
‏            await self.select_team_leaders(channel, normal_count)

‏    async def select_team_leaders(self, channel, normal_count):
‏        self.leader_selection = True
‏        await channel.send("كل فريق يختار الليدر! رشحوا اللي تبونه بالمنشن خلال 10 ثواني.")

‏        await asyncio.sleep(10)

‏        self.blue_leader = max(self.blue_mentions.items(), key=lambda x: x[1])[0] if self.blue_mentions else random.choice(self.blue_team)
‏        self.red_leader = max(self.red_mentions.items(), key=lambda x: x[1])[0] if self.red_mentions else random.choice(self.red_team)

‏        await channel.send(f"ليدر الفريق الأزرق: {self.blue_leader}")
‏        await channel.send(f"ليدر الفريق الأحمر: {self.red_leader}")

‏        await self.start_full_game(channel, normal_count)

‏    async def start_full_game(self, channel, normal_count):
‏        self.questions = []
‏        self.questions += [{"type": "normal"}] * normal_count
‏        self.questions.append({"type": "golden"})
‏        self.questions.append({"type": "steal_or_boost"})
‏        if self.game_mode == "تيم":
‏            self.questions.append({"type": "sabotage"})
‏        self.questions.append({"type": "fate"})
‏        self.questions.append({"type": "doom"})

‏        self.current_index = 0
‏        await channel.send("اللعبة بدأت! استعد للسؤال الأول...")
‏        await self.ask_next_question(channel)

‏    async def ask_next_question(self, channel):
‏        if self.current_index >= len(self.questions):
‏            await self.finish_game(channel)
‏            return

‏        q = self.questions[self.current_index]
‏        self.current_index += 1

‏        try:
‏            if q["type"] == "normal":
‏                qobj = TeamNormalQuestion()
‏                player_scores = await qobj.ask(channel, self.bot, {"أزرق": self.blue_team, "أحمر": self.red_team}, self.points)
‏                for player, score in player_scores.items():
‏                    self.points[player] += score

‏            elif q["type"] == "golden":
‏                qobj = GoldenQuestion()
‏                result = await qobj.ask(channel, self.bot, self.game_mode, {"أزرق": self.blue_team, "أحمر": self.red_team}, self.points)
‏                for player, score in result.items():
‏                    self.points[player] += score

‏            elif q["type"] == "steal_or_boost":
‏                qobj = ChallengeStealOrBoostQuestion()
‏                await qobj.ask(channel, self.bot, self.players if self.game_mode == "تحدي" else self.blue_team + self.red_team, self.points)

‏            elif q["type"] == "sabotage" and self.game_mode == "تيم":
‏                qobj = SabotageQuestion()
‏                await qobj.ask(channel, self.bot, {"أزرق": self.blue_team, "أحمر": self.red_team},
                               {"أزرق": self.blue_leader, "أحمر": self.red_leader}, self.points, self.game_mode)

‏            elif q["type"] == "fate":
‏                qobj = TestOfFate([{"question": "مثال سؤال ١", "answer": "اجابة"},
‏                                   {"question": "مثال سؤال ٢", "answer": "اجابة"},
‏                                   {"question": "مثال سؤال ٣", "answer": "اجابة"},
‏                                   {"question": "مثال سؤال ٤", "answer": "اجابة"},
‏                                   {"question": "مثال سؤال ٥", "answer": "اجابة"}])
‏                await qobj.ask(channel, self.bot, self.players if self.game_mode == "تحدي" else self.blue_team + self.red_team, self.points)

‏            elif q["type"] == "doom":
‏                qobj = DoomQuestion()
‏                await qobj.ask(channel, self.bot,
                               {"أزرق": self.blue_leader, "أحمر": self.red_leader},
                               {"أزرق": self.blue_team, "أحمر": self.red_team},
‏                               self.points)

‏        except Exception as e:
‏            await channel.send(f"خطأ أثناء تنفيذ السؤال: {str(e)}")

‏        await asyncio.sleep(2)
‏        await self.ask_next_question(channel)

‏    async def finish_game(self, channel):
‏        if self.game_mode == "سولو":
‏            winner = self.main_player
‏            points = self.points.get(winner, 0)
‏            if points >= 50:
‏                msg = get_response("solo_win_responses", context={"player": winner})
‏            else:
‏                msg = get_response("below_50_responses", context={"player": winner})
‏            await channel.send(msg)

‏        elif self.game_mode == "تحدي":
‏            valid_players = [p for p in self.players if p not in self.kicked_players]
‏            if not valid_players:
‏                await channel.send("ماكو احد فاز!")
‏                return
‏            for player in valid_players:
‏                if self.points.get(player, 0) < 50:
‏                    msg = get_response("below_50_responses", context={"player": player})
‏                    if msg:
‏                        await channel.send(msg)
‏            winner = max(valid_players, key=lambda p: self.points.get(p, 0))
‏            points = self.points.get(winner, 0)
‏            if points >= 50:
‏                win_msg = get_response("group_win_responses", context={"player": winner})
‏                await channel.send(win_msg)

‏        elif self.game_mode == "تيم":
‏            blue_score = sum(self.points[p] for p in self.blue_team if p not in self.kicked_players)
‏            red_score = sum(self.points[p] for p in self.red_team if p not in self.kicked_players)
‏            if blue_score >= red_score:
‏                winning_team = "أزرق"
‏                losing_team = "أحمر"
‏            else:
‏                winning_team = "أحمر"
‏                losing_team = "أزرق"

‏            win_msg = get_response("team_win_responses", context={"team": winning_team})
‏            lose_msg = get_response("team_lose_responses", context={"team": losing_team})

‏            await channel.send(win_msg)
‏            await channel.send(lose_msg)

‏        await channel.send("شكرًا لانضمامكم! تم تطوير اللعبة بفكرة وإبداع Wujud © جميع الحقوق محفوظة.")
‏        await self.reset_game()

‏    async def reset_game(self, channel=None, notice=None):
‏        if channel and notice:
‏            await channel.send(notice)

‏        self.players = []
‏        self.blue_team = []
‏        self.red_team = []
‏        self.points.clear()
‏        self.kicked_players.clear()
‏        self.game_mode = None
‏        self.leader_selection = False
‏        self.blue_mentions.clear()
‏        self.red_mentions.clear()
‏        self.blue_leader = None
‏        self.red_leader = None
‏        self.main_player = None
‏        self.questions = []
‏        self.current_index = 0
‏        self.selected_game_mode = None
‏        self.waiting_for_normal_count = False
