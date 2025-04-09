
import time

class GoldenQuestion:
    def __init__(self, question, correct_answer):
        self.question = question
        self.correct_answer = correct_answer.lower()

    async def ask(self, channel, bot, game_mode):
        await channel.send("استعدوا... هذا هو السؤال الذهبي!")
        await channel.send(f"السؤال: {self.question} (عندكم 10 ثواني!)")
        start_time = time.time()
        winner = None

        def check_response(msg):
            nonlocal winner
            user = msg.author.name
            response = msg.content.strip().lower()
            if winner is None and response == self.correct_answer:
                winner = user
            return False

        await bot.wait_for_responses(10, check_response)

        if game_mode == "سولو":
            if winner:
                await channel.send(f"{winner} جاوب صح! حصل على 100 نقطة.")
                return {winner: 100}
            else:
                await channel.send("خلص الوقت!")
                return {}
        else:
            if winner:
                await channel.send(f"{winner} أول من جاوب صح! حصل على 100 نقطة.")
                return {winner: 100}
            else:
                await channel.send("خلص الوقت!")
                return {}
