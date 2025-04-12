from utils.responses import get_response
import time

class GoldenQuestion:
    def __init__(self, question, correct_answer, alt_answers=None):
        self.question = question
        self.correct_answer = correct_answer.lower()
        self.alt_answers = [ans.lower() for ans in (alt_answers or [])]

    async def ask(self, channel, bot, game_mode, teams=None, points=None):
        await channel.send("استعدوا... هذا هو السؤال الذهبي!")
        await channel.send(f"السؤال: {self.question} (عندكم 10 ثواني!)")
        start_time = time.time()
        winner = None

        def check_response(msg):
            nonlocal winner
            user = msg.author.name
            response = msg.content.strip().lower()
            all_answers = [self.correct_answer] + self.alt_answers
            if winner is None and response in all_answers:
                winner = user
            return False

        await bot.wait_for_responses(10, check_response)

        if not winner:
            await channel.send("خلص الوقت! ما حد جاوب.")
            return {}

        await channel.send(f"{winner} جاوب صح! حصل على 100 نقطة.")

        if game_mode == "تيم" and teams and points:
            team = "أزرق" if winner in teams["أزرق"] else "أحمر"
            for player in teams[team]:
                points[player] = points.get(player, 0) + 100
            return points
        else:
            return {winner: 100}