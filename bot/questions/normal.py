# bot/questions/normal.py

import time

class NormalQuestion:
    def __init__(self, question, correct_answer, alt_answers=None):
        self.question = question
        self.correct_answer = correct_answer.lower()
        self.alt_answers = [ans.lower() for ans in (alt_answers or [])]
        self.answers = {}

    async def ask(self, channel, bot, streaks, mode="solo"):
        await channel.send(f"السؤال: {self.question} (10 ثوانٍ للإجابة!)")
        start_time = time.time()

        def check_response(msg):
            user = msg.author.name
            response = msg.content.strip().lower()
            all_answers = [self.correct_answer] + self.alt_answers

            if user not in self.answers and response in all_answers:
                response_time = time.time() - start_time
                self.answers[user] = response_time
            return False

        await bot.wait_for_responses(10, check_response)

        player_scores = {}
        for player, response_time in self.answers.items():
            points = 0
            if response_time <= 5:
                points = 10
            elif response_time <= 10:
                points = 5

            streaks[player] += 1
            bonus = (streaks[player] // 3) * 10 if streaks[player] % 3 == 0 else 0
            total_points = points + bonus
            player_scores[player] = total_points

        all_players = bot.get_all_players()
        for player in all_players:
            if player not in self.answers:
                streaks[player] = 0

        return player_scores


class TeamNormalQuestion(NormalQuestion):
    async def ask(self, channel, bot, teams, points, streaks):
        player_scores = await super().ask(channel, bot, streaks, mode="team")

        for player, score in player_scores.items():
            if player in teams["أزرق"]:
                points[player] = points.get(player, 0) + score
            elif player in teams["أحمر"]:
                points[player] = points.get(player, 0) + score
