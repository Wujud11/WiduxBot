
import asyncio

class TestOfFate:
    def __init__(self, questions):
        self.questions = questions

    async def ask(self, channel, bot, players, points):
        await channel.send("جولة اختبار المصير بدأت! عندكم 5 أسئلة ورا بعض، كل صح +10 وكل غلط -5. جاهزين؟")

        for i, (question, answer) in enumerate(self.questions[:5]):
            await channel.send(f"سؤال رقم {i+1}: {question} (10 ثواني تجاوب!)")
            answered = set()

            def check(msg):
                user = msg.author.name
                if user in players and user not in answered:
                    if msg.content.strip().lower() == answer.lower():
                        points[user] = points.get(user, 0) + 10
                    else:
                        points[user] = points.get(user, 0) - 5
                    answered.add(user)
                return False

            await bot.wait_for_responses(10, check)

        await channel.send("انتهت جولة اختبار المصير!")
        return points
