from utils.responses import get_response

class TestOfFate:
    def __init__(self, questions_and_answers):
        self.questions = [
            (q["question"], q["answer"].lower(), [a.lower() for a in q.get("alt_answers", [])])
            for q in questions_and_answers
        ]

    async def ask(self, channel, bot, players, points):
        await channel.send("جولة اختبار المصير بدأت! كل سؤال له 10 ثواني، كل إجابة صح +10 وخطأ -5!")

        scores = {player: 0 for player in players}

        for i, (question, answer, alt_answers) in enumerate(self.questions[:5]):
            await channel.send(f"سؤال {i+1}: {question} (10 ثواني!)")
            answered = set()

            def check_answer(msg):
                user = msg.author.name
                response = msg.content.strip().lower()
                all_answers = [answer] + alt_answers
                if user in players and user not in answered:
                    answered.add(user)
                    if response in all_answers:
                        scores[user] += 10
                    else:
                        scores[user] -= 5
                return False

            await bot.wait_for_responses(10, check_answer)
            await channel.send(f"الإجابة الصحيحة كانت: {answer}")

        # تحديث النقاط الإجمالية
        for player, score in scores.items():
            points[player] = points.get(player, 0) + score

        results = "\n".join(f"{p}: {points[p]} نقطة" for p in players)
        await channel.send("نتائج اختبار المصير:\n" + results)

        # طقطقة للي نقاطهم تحت الصفر
        for player in players:
            if points[player] < 0:
                msg = get_response("taunts_negative", {"player": player})
                if msg:
                    await channel.send(msg)

        return points