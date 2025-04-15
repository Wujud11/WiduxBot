import asyncio
import random
from utils.responses import get_response

class SabotageQuestion:
    def __init__(self, question, correct_answer, alt_answers=None):
        self.question = question
        self.correct_answer = correct_answer.lower()
        self.alt_answers = [ans.lower() for ans in (alt_answers or [])]

    async def ask(self, channel, bot, teams, leaders, points, game_mode):
        await channel.send("كل فريق يكتب منشن لواحد من الخصم يبغى يطرده (ماعدا القائد)، معكم 15 ثانية!")

        mentions = {"أزرق": None, "أحمر": None}
        individual_mentions = {}

        def check_mentions(msg):
            user = msg.author.name
            content = msg.content
            if game_mode == "تيم":
                if user in teams["أزرق"] and not mentions["أزرق"]:
                    if msg.mentions and msg.mentions[0].name in teams["أحمر"] and msg.mentions[0].name != leaders["أحمر"]:
                        mentions["أزرق"] = msg.mentions[0].name
                elif user in teams["أحمر"] and not mentions["أحمر"]:
                    if msg.mentions and msg.mentions[0].name in teams["أزرق"] and msg.mentions[0].name != leaders["أزرق"]:
                        mentions["أحمر"] = msg.mentions[0].name
            elif game_mode == "تحدي":
                if msg.mentions and msg.mentions[0].name in points:
                    individual_mentions[user] = msg.mentions[0].name
            return False

        await bot.wait_for_responses(15, check_mentions)

        await channel.send("السؤال الجاي للجميع، أول واحد يجاوب صح ينفذ اختياره:")
        await channel.send(f"{self.question} (10 ثواني!)")

        winner = None

        def check_response(msg):
            nonlocal winner
            response = msg.content.strip().lower()
            if response in [self.correct_answer] + self.alt_answers and msg.author.name in points and winner is None:
                winner = msg.author.name
            return False

        await bot.wait_for_responses(10, check_response)

        if not winner:
            await channel.send("ما جاوب أحد! ما فيه طرد.")
            return points

        if game_mode == "تيم":
            team = "أزرق" if winner in teams["أزرق"] else "أحمر"
            target = mentions[team]
        elif game_mode == "تحدي":
            target = individual_mentions.get(winner)

        if not target or target in [leaders.get("أزرق"), leaders.get("أحمر")]:
            await channel.send("ما تقدر تطرد القائد أو ما تم تحديد ضحية بشكل صحيح.")
            return points

        await channel.send(f"{winner} جاوب أول! {target} تم طرده من اللعبة.")

        msg = get_response("kicked_responses", {"player": target})
        if msg:
            await channel.send(msg)

        if target in points:
            del points[target]

        return points
