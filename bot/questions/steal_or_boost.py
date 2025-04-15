import asyncio
import random
from utils.responses import get_response

class StealOrBoostTeamQuestion:
    def __init__(self, question, correct_answer, alt_answers=None):
        self.question = question
        self.correct_answer = correct_answer.lower()
        self.alt_answers = [ans.lower() for ans in (alt_answers or [])]

    async def ask(self, channel, bot, teams, leaders, points):
        await channel.send("اكتب زرف أو زود للتسجيل! عندكم 10 ثواني!")

        decisions = {}

        def decision_check(msg):
            user = msg.author.name
            choice = msg.content.strip().lower()
            if user in teams['أزرق'] + teams['أحمر'] and user not in decisions:
                if choice in ["زرف", "زود"]:
                    decisions[user] = choice
            return False

        await bot.wait_for_responses(10, decision_check)

        await channel.send(f"السؤال: {self.question} (10 ثواني للإجابة!)")

        correct_user = None

        def answer_check(msg):
            nonlocal correct_user
            user = msg.author.name
            content = msg.content.strip().lower()
            if user in decisions and content in [self.correct_answer] + self.alt_answers:
                correct_user = user
            return False

        await bot.wait_for_responses(10, answer_check)

        if not correct_user:
            await channel.send("ما حد جاوب صح!")
            return points

        action = decisions[correct_user]
        user_team = "أزرق" if correct_user in teams["أزرق"] else "أحمر"
        opponent_team = "أحمر" if user_team == "أزرق" else "أزرق"

        if action == "زود":
            bonus = random.randint(10, 50)
            points[correct_user] = points.get(correct_user, 0) + bonus
            await channel.send(f"{correct_user} اختار زود! وتمت إضافة {bonus} نقطة له.")
            return points

        await channel.send(f"{correct_user} اختار زرف! منشن لاعب من الفريق {opponent_team} للسرقة.")

        target_player = None

        def mention_check(msg):
            nonlocal target_player
            user = msg.author.name
            if (
                (correct_user == leaders[user_team] and user == correct_user)
                or (correct_user != leaders[user_team] and user == leaders[user_team])
            ):
                mentions = [word[1:] for word in msg.content.split() if word.startswith("@")]
                for m in mentions:
                    if m in teams[opponent_team]:
                        target_player = m
                        return True
            return False

        await bot.wait_for_responses(10, mention_check)

        if not target_player:
            await channel.send("ما تم اختيار لاعب للسرقة!")
            return points

        stolen = points.get(target_player, 0)
        points[target_player] = 0
        for p in teams[user_team]:
            points[p] = points.get(p, 0) + stolen // len(teams[user_team])

        msg = get_response("stolen_responses", {"player": target_player})
        if msg:
            await channel.send(msg)

        return points


class ChallengeStealOrBoostQuestion:
    def __init__(self, question, correct_answer, alt_answers=None):
        self.question = question
        self.correct_answer = correct_answer.lower()
        self.alt_answers = [ans.lower() for ans in (alt_answers or [])]

    async def ask(self, channel, bot, players, points):
        await channel.send("اكتب زرف أو زود للتسجيل! عندكم 10 ثواني!")

        decisions = {}

        def decision_check(msg):
            user = msg.author.name
            choice = msg.content.strip().lower()
            if user in players and user not in decisions:
                if choice in ["زرف", "زود"]:
                    decisions[user] = choice
            return False

        await bot.wait_for_responses(10, decision_check)

        await channel.send(f"السؤال: {self.question} (10 ثواني للإجابة!)")

        correct_user = None

        def answer_check(msg):
            user = msg.author.name
            content = msg.content.strip().lower()
            if user in decisions and content in [self.correct_answer] + self.alt_answers:
                nonlocal correct_user
                correct_user = user
            return False

        await bot.wait_for_responses(10, answer_check)

        if not correct_user:
            await channel.send("ما حد جاوب صح!")
            return points

        action = decisions[correct_user]

        if action == "زود":
            bonus = random.randint(10, 50)
            points[correct_user] = points.get(correct_user, 0) + bonus
            await channel.send(f"{correct_user} اختار زود! وتمت إضافة {bonus} نقطة له.")
            return points

        # زرف - عشوائي
        potential_targets = [p for p in players if p != correct_user]
        if not potential_targets:
            await channel.send("ما فيه أحد تسرقه!")
            return points

        target = random.choice(potential_targets)
        stolen = points.get(target, 0)
        points[target] = 0
        points[correct_user] = points.get(correct_user, 0) + stolen

        msg = get_response("stolen_responses", {"player": target})
        if msg:
            await channel.send(msg)

        return points
