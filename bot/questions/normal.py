from utils.responses import get_response
import time

class NormalQuestion:
    def __init__(self, question, correct_answer, alt_answers=None):
        self.question = question
        self.correct_answer = correct_answer.lower()
        self.alt_answers = [ans.lower() for ans in (alt_answers or [])]
        self.answers = {}

    async def ask(self, channel, bot, streaks, mode="solo"):
        await channel.send(f"السؤال: {self.question} (10 ثواني تجاوب!)")
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

        if player_scores:
            results = '\n'.join([f"{player}: {points} نقطة" for player, points in player_scores.items()])
            await channel.send("نتائج السؤال:\n" + results)

            # ردود مدح حسب الوضع (تم تعديل المفاتيح هنا)
            for player in player_scores:
                key = "solo_win" if mode == "solo" else "team_win"
                msg = get_response(key, {"player": player})
                if msg:
                    await channel.send(msg)
        else:
            await channel.send("ما حد جاوب صح!")

        return player_scores