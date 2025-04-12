import asyncio
import random
from collections import defaultdict

from bot.questions.normal import NormalQuestion, TeamNormalQuestion
from bot.questions.golden import GoldenQuestion
from bot.questions.sabotage import SabotageQuestion
from bot.flow.game_flow_manager import start_game
from bot.question_manager import QuestionManager


class WiduxEngine:
    def __init__(self):
        self.players = []
        self.blue_team = []
        self.red_team = []
        self.game_mode = None
        self.leader_selection = False
        self.blue_mentions = defaultdict(int)
        self.red_mentions = defaultdict(int)
        self.blue_leader = None
        self.red_leader = None
        self.main_player = None
        self.bot = None
        self.q_manager = QuestionManager()

    async def handle_message(self, message):
        content = message.content.strip()
        sender = message.author.name
        self.bot = message._bot  # حفظ البوت للاستخدام في start_game

        if content == "وج؟":
            await message.channel.send("هلا والله! إذا بتلعب لحالك اكتب سولو، إذا ضد الكل اكتب تحدي، وإذا مع ربعك اكتب تيم.")
            return

        if content in ["سولو", "تحدي", "تيم"] and not self.game_mode:
            self.game_mode = content
            self.main_player = sender

            if content == "سولو":
                await message.channel.send("عندك 10 ثواني لكل سؤال، جاهز؟")
                await self.start_full_game(message.channel)

            elif content == "تحدي":
                await message.channel.send("اللي بيلعب يكتب 'R' للتسجيل معكم 15 ثانية!")
                await self.register_challenge_players(message.channel)

            elif content == "تيم":
                await message.channel.send("كل واحد يختار فريقه، يكتب 'أزرق' أو 'أحمر' معكم 20 ثانية!")
                await self.register_team_players(message.channel)

            return

        if self.game_mode == "تحدي" and content.upper() == 'R' and sender not in self.players:
            self.players.append(sender)

        if self.game_mode == "تيم" and not self.leader_selection:
            if content == 'أزرق' and sender not in self.blue_team and sender not in self.red_team:
                self.blue_team.append(sender)
            elif content == 'أحمر' and sender not in self.red_team and sender not in self.blue_team:
                self.red_team.append(sender)

        if self.leader_selection and self.game_mode == "تيم":
            mentioned_players = self.extract_mentions(content)
            for player in mentioned_players:
                if player in self.blue_team:
                    self.blue_mentions[player] += 1
                elif player in self.red_team:
                    self.red_mentions[player] += 1

    def extract_mentions(self, text):
        return [word[1:] for word in text.split() if word.startswith('@')]

    async def register_challenge_players(self, channel):
        await asyncio.sleep(15)
        if len(self.players) < 2:
            await self.reset_game(channel, "ما فيه عدد كافي نبدأ فيه التحدي.")
        else:
            await channel.send(f"تم تسجيل اللاعبين: {', '.join(self.players)}")
            await self.start_full_game(channel)

    async def register_team_players(self, channel):
        await asyncio.sleep(20)
        if len(self.blue_team) < 3 or len(self.red_team) < 3:
            await self.reset_game(channel, "لازم ٣ لاعبين على الأقل في كل فريق.")
        else:
            await channel.send(f"الفريق الأزرق: {', '.join(self.blue_team)}")
            await channel.send(f"الفريق الأحمر: {', '.join(self.red_team)}")
            await self.select_team_leaders(channel)

    async def select_team_leaders(self, channel):
        self.leader_selection = True
        await channel.send("اختاروا الليدر! منشنوه خلال 10 ثواني.")
        await asyncio.sleep(10)

        self.blue_leader = max(self.blue_mentions.items(), key=lambda x: x[1])[0] if self.blue_mentions else random.choice(self.blue_team)
        self.red_leader = max(self.red_mentions.items(), key=lambda x: x[1])[0] if self.red_mentions else random.choice(self.red_team)

        await channel.send(f"ليدر الأزرق: {self.blue_leader}")
        await channel.send(f"ليدر الأحمر: {self.red_leader}")
        await self.start_full_game(channel)

    async def start_full_game(self, channel):
        await start_game(
            channel=channel,
            bot=self.bot,
            game_mode=self.game_mode,
            teams={"أزرق": self.blue_team, "أحمر": self.red_team},
            leaders={"أزرق": self.blue_leader, "أحمر": self.red_leader},
            players=self.players if self.game_mode == "تحدي" else self.blue_team + self.red_team if self.game_mode == "تيم" else [self.main_player],
            questions_data=self.q_manager.get_questions_by_type("Normal"),
            golden_question_data=self.q_manager.get_random_question("Golden"),
            steal_question_data=self.q_manager.get_random_question("Steal"),
            sabotage_question_data=self.q_manager.get_random_question("Sabotage"),
            fate_questions_data=self.q_manager.get_questions_by_type("Fate"),
            doom_question_data=self.q_manager.get_random_question("Doom")
        )
        await self.reset_game(channel)

    async def reset_game(self, channel=None, notice=None):
        if channel and notice:
            await channel.send(notice)

        self.players.clear()
        self.blue_team.clear()
        self.red_team.clear()
        self.game_mode = None
        self.leader_selection = False
        self.blue_mentions.clear()
        self.red_mentions.clear()
        self.blue_leader = None
        self.red_leader = None
        self.main_player = None