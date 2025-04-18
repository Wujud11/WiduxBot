import asyncio
import random
from collections import defaultdict
from bot.questions.normal import NormalQuestion
from bot.questions.golden import GoldenQuestion
from bot.questions.steal_or_boost import StealOrBoostTeamQuestion, ChallengeStealOrBoostQuestion
from bot.questions.sabotage import SabotageQuestion
from bot.questions.fate import TestOfFate
from bot.questions.doom import DoomQuestion
from utils.responses import get_response

class WiduxEngine:
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.players = []
        self.teams = {"أزرق": [], "أحمر": []}
        self.leaders = {"أزرق": None, "أحمر": None}
        self.points = defaultdict(int)
        self.kicked_players = []  # لاعبين مطرودين
        self.mode = None
        self.main_player = None

    async def handle_message(self, message):
        content = message.content.strip()
        if content == "وج؟":
            self.channel = message.channel
            await message.channel.send("هلا والله! إذا بتلعب لحالك اكتب سولو، إذا ضد الكل تحدي، وإذا مع ربعك تيم.")
        elif content.lower() in ["سولو", "تحدي", "تيم"]:
            self.mode = content.lower()
            if self.mode == "سولو":
                self.main_player = message.author.name
                await message.channel.send("حدد عدد الأسئلة من 5 إلى 10.")
            elif self.mode == "تحدي":
                await message.channel.send("اكتب R للتسجيل بالتحدي! (معك 15 ثانية)")
                await self.collect_players(message.channel, "R", 15)
                await message.channel.send("حدد عدد الأسئلة من 5 إلى 10.")
            elif self.mode == "تيم":
                await message.channel.send("اكتب أزرق أو أحمر للانضمام! (معك 20 ثانية)")
                await self.collect_teams(message.channel, 20)
                await self.select_leaders(message.channel)
                await message.channel.send("حدد عدد الأسئلة من 5 إلى 10.")

        elif content.isdigit() and int(content) in range(5, 11):
            if self.mode == "تحدي" and len(self.players) < 2:
                await self.channel.send("لازم يكون فيه لاعبين أكثر من واحد علشان يبدأ التحدي.")
                return
            if self.mode == "تيم":
                if len(self.teams["أزرق"]) < 3 or len(self.teams["أحمر"]) < 3:
                    await self.channel.send("لازم كل فريق فيه 3 لاعبين أو أكثر علشان نبدأ اللعبة.")
                    return

            self.normal_questions_count = int(content)
            await self.start_game()

    async def collect_players(self, channel, keyword, duration):
        self.players = []
        await asyncio.sleep(duration)

    async def collect_teams(self, channel, duration):
        self.teams = {"أزرق": [], "أحمر": []}
        await asyncio.sleep(duration)

    async def select_leaders(self, channel):
        for team, members in self.teams.items():
            if members:
                self.leaders[team] = random.choice(members)

    async def start_game(self):
        channel = self.channel

        for _ in range(self.normal_questions_count):
            qobj = NormalQuestion(self)
            await qobj.ask(channel)
        await asyncio.sleep(2)

        golden = GoldenQuestion(self)
        await golden.ask(channel)
        await asyncio.sleep(2)

        if self.mode == "تيم":
            steal_boost = StealOrBoostTeamQuestion(self)
        else:
            steal_boost = ChallengeStealOrBoostQuestion(self)
        await steal_boost.ask(channel)
        await asyncio.sleep(2)

        if self.mode == "تيم":
            sabotage = SabotageQuestion(self)
            await sabotage.ask(channel)
            await asyncio.sleep(2)

        fate = TestOfFate(self)
        await fate.ask(channel)
        await asyncio.sleep(2)

        doom = DoomQuestion(self)
        await doom.ask(channel)
        await asyncio.sleep(2)

        await self.finish_game()

    async def finish_game(self):
        channel = self.channel

        if self.mode == "سولو":
            player = self.main_player
            if player not in self.kicked_players:
                points = self.points.get(player, 0)
                if points >= 50:
                    await channel.send(get_response("solo_win_responses", {"player": player}))
                else:
                    await channel.send(get_response("below_50_responses", {"player": player}))

        elif self.mode == "تحدي":
            valid_players = {p: pts for p, pts in self.points.items() if p not in self.kicked_players}
            if not valid_players:
                await channel.send("مافي نقاط، محد فاز!")
                return

            winner = max(valid_players, key=valid_players.get)
            points = valid_players[winner]

            if points >= 50:
                await channel.send(get_response("group_win_responses", {"player": winner}))
            else:
                await channel.send(get_response("below_50_responses", {"player": winner}))

            for player, pts in valid_players.items():
                if player != winner and pts < 50:
                    await channel.send(get_response("below_50_responses", {"player": player}))

        elif self.mode == "تيم":
            team_scores = {"أزرق": 0, "أحمر": 0}
            for player, pts in self.points.items():
                if player in self.kicked_players:
                    continue
                if player in self.teams.get("أزرق", []):
                    team_scores["أزرق"] += pts
                elif player in self.teams.get("أحمر", []):
                    team_scores["أحمر"] += pts

            winning_team = max(team_scores, key=team_scores.get)
            losing_team = "أحمر" if winning_team == "أزرق" else "أزرق"

            await channel.send(get_response("team_win_responses", {"team": winning_team}))
            await channel.send(get_response("team_lose_responses", {"team": losing_team}))

            for player, pts in self.points.items():
                if player not in self.kicked_players and player in self.teams[losing_team] and pts < 50:
                    await channel.send(get_response("below_50_responses", {"player": player}))

            for team, leader in self.leaders.items():
                if leader and leader not in self.kicked_players:
                    team_players = self.teams.get(team, [])
                    if team_players:
                        leader_points = self.points.get(leader, 0)
                        higher_members = [p for p in team_players if p not in self.kicked_players and self.points.get(p, 0) > leader_points]
                        if higher_members:
                            await channel.send(get_response("weak_leader_responses", {"leader": leader}))

        await channel.send("شكرًا لانضمامكم! تم تطوير هذه اللعبة بفكرة وإبداع Wujud © جميع الحقوق محفوظة.")
