import random
from bot.questions.normal import NormalQuestion, TeamNormalQuestion
from bot.questions.golden import GoldenQuestion
from bot.questions.sabotage import SabotageQuestion
from bot.questions.fate import TestOfFate
from bot.questions.doom import DoomQuestion

class GameFlowManager:
    def __init__(self, game_mode, questions, golden, steal, sabotage, fate, doom):
        self.game_mode = game_mode
        self.normal_questions = questions
        self.golden = golden
        self.steal = steal
        self.sabotage = sabotage
        self.fate = fate
        self.doom = doom

    async def start_game(self, channel, bot, teams=None, leaders=None, points=None, streaks=None):
        # Normal Questions
        for q in self.normal_questions:
            if self.game_mode == "تيم":
                nq = TeamNormalQuestion(q["question"], q["answer"], q.get("alt_answers", []))
                await nq.ask(channel, bot, teams, points, streaks)
            else:
                nq = NormalQuestion(q["question"], q["answer"], q.get("alt_answers", []))
                await nq.ask(channel, bot, streaks)

        # Golden Question
        if self.golden:
            gq = GoldenQuestion(self.golden["question"], self.golden["answer"], self.golden.get("alt_answers", []))
            golden_scores = await gq.ask(channel, bot, self.game_mode)
            if self.game_mode == "تيم":
                for player, score in golden_scores.items():
                    points[player] = points.get(player, 0) + score
            else:
                # في سولو وتحدي يتم المعالجة خارجية
                pass

        # Steal or Boost Question (يتم استيراده حسب الوضع)
        if self.steal and self.game_mode in ["تيم", "تحدي"]:
            if self.game_mode == "تيم":
                from bot.questions.steal_or_boost import StealOrBoostTeamQuestion as StealOrBoostQuestion
                sbq = StealOrBoostQuestion(self.steal["question"], self.steal["answer"], self.steal.get("alt_answers", []))
                await sbq.ask(channel, bot, teams, leaders, points)
            elif self.game_mode == "تحدي":
                from bot.questions.steal_or_boost import ChallengeStealOrBoostQuestion as StealOrBoostQuestion
                sbq = StealOrBoostQuestion(self.steal["question"], self.steal["answer"], self.steal.get("alt_answers", []))
                players = list(points.keys())
                await sbq.ask(channel, bot, players, points)

        # Sabotage Question
        if self.sabotage and self.game_mode in ["تيم", "تحدي"]:
            sabotage_q = SabotageQuestion(self.sabotage["question"], self.sabotage["answer"], self.sabotage.get("alt_answers", []))
            await sabotage_q.ask(channel, bot, teams, leaders, points)

        # Test of Fate
        if self.fate:
            ft = TestOfFate(self.fate)
            all_players = []
            if self.game_mode == "تيم":
                all_players = teams["أزرق"] + teams["أحمر"]
            elif self.game_mode == "تحدي":
                all_players = list(points.keys())
            elif self.game_mode == "سولو":
                all_players = [bot.main_player] if hasattr(bot, "main_player") else []
            fate_scores = await ft.ask(channel, bot, all_players)
            for player, score in fate_scores.items():
                points[player] = points.get(player, 0) + score

        # Doom Question
        if self.doom and self.game_mode == "تيم":
            doom_q = DoomQuestion(self.doom["question"], self.doom["answer"], self.doom.get("alt_answers", []))
            await doom_q.ask(channel, bot, leaders, teams, points)


# النسخة الخارجية المربوطة مع engine.py
async def start_game(channel, bot, game_mode, players, teams, leaders,
                     questions_data, golden_question_data, steal_question_data,
                     sabotage_question_data, fate_questions_data, doom_question_data):

    # نقاط وستريكس (تقدرين تطورينها لاحقًا بحفظ خارجي)
    points = {player: 0 for player in players}
    streaks = {player: 0 for player in players}

    manager = GameFlowManager(
        game_mode,
        questions=questions_data,
        golden=golden_question_data,
        steal=steal_question_data,
        sabotage=sabotage_question_data,
        fate=fate_questions_data,
        doom=doom_question_data
    )

    await manager.start_game(channel, bot, teams, leaders, points, streaks)
