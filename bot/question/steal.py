
import random
import asyncio

class StealQuestion:
    def __init__(self, question, correct_answer):
        self.question = question
        self.correct_answer = correct_answer.lower()
        self.choices = {}

    async def collect_choices(self, channel, bot, players):
        await channel.send("قبل لا نبدأ، كل واحد يكتب 'زرف' أو 'زود' خلال 10 ثواني!")
        self.choices = {}

        def check_choice(msg):
            user = msg.author.name
            choice = msg.content.strip().lower()
            if user in players and choice in ['زرف', 'زود'] and user not in self.choices:
                self.choices[user] = choice
            return False

        await bot.wait_for_responses(10, check_choice)

    async def ask(self, channel, bot, game_mode, players, leaders=None, points=None):
        await self.collect_choices(channel, bot, players)
        await channel.send(f"السؤال: {self.question} (10 ثواني تجاوب!)")

        winner = None

        def check_response(msg):
            nonlocal winner
            user = msg.author.name
            response = msg.content.strip().lower()
            if user in players and response == self.correct_answer and winner is None:
                winner = user
            return False

        await bot.wait_for_responses(10, check_response)

        if not winner:
            await channel.send("ما جاوب أحد! راحت الفرصة.")
            return {}

        choice = self.choices.get(winner, None)
        if not choice:
            await channel.send(f"{winner} ما اختار 'زرف' ولا 'زود' قبل السؤال!")
            return {}

        roasts = [f"@{{player}} اطلب من زياد يسلفك", "ترى مو أول مرة تنزرف،لاتعطيها وضعية حياة الفهد", "انزرفت وانت ما تدري، مسكين"]

        if game_mode == "تحدي":
            if choice == "زرف":
                target = random.choice([p for p in players if p != winner])
                stolen_points = points.get(target, 0)
                points[winner] = points.get(winner, 0) + stolen_points
                points[target] = 0
                await channel.send(f"{winner} زرف نقاط {target} كلها!")
                await channel.send(random.choice(roasts).replace("{player}", target))
            else:
                bonus = random.randint(0, 50)
                points[winner] = points.get(winner, 0) + bonus
                await channel.send(f"{winner} جرب الزود وحصل على {bonus} نقطة.")
            return points
        elif game_mode == "سولو":
            await channel.send("ما فيه زرف في السولو! تخطي للسؤال هذا.")
            return {}

