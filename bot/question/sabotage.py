
import asyncio
import random

class SabotageQuestion:
    def __init__(self, question, correct_answer):
        self.question = question
        self.correct_answer = correct_answer.lower()

    async def ask(self, channel, bot, teams, leaders, points):
        await channel.send("اختر شخصًا من الفريق الآخر ترغب في استبعاده من اللعبة، قم بعمل منشن له (15 ثانية).")

        mentions = {"أزرق": None, "أحمر": None}

        def check_mention(msg):
            user = msg.author.name
            for team, members in teams.items():
                if user in members:
                    for word in msg.content.split():
                        if word.startswith("@"):
                            target = word[1:]
                            if target not in members:
                                mentions[team] = target
            return False

        await bot.wait_for_responses(15, check_mention)

        if not mentions["أزرق"] and not mentions["أحمر"]:
            await channel.send("ما أحد منشن، تم تخطي السؤال.")
            return {}, []

        await channel.send(f"السؤال: {self.question} (أول من يجاوب صح يتم تنفيذ الطرد!)")

        winner = None

        def check_answer(msg):
            nonlocal winner
            if msg.content.strip().lower() == self.correct_answer and winner is None:
                winner = msg.author.name
            return False

        await bot.wait_for_responses(10, check_answer)

        eliminated = []

        if winner:
            for team, target in mentions.items():
                if target and winner in teams[team]:
                    if target != leaders["أزرق"] and target != leaders["أحمر"]:
                        eliminated.append(target)
                        await channel.send(f"{target} تم طرده من اللعبة.")
        else:
            await channel.send("ما أحد جاوب صح.")

        return points, eliminated
