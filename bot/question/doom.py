
import asyncio
import random

class DoomQuestion:
    def __init__(self, question, correct_answer):
        self.question = question
        self.correct_answer = correct_answer.lower()
        self.accepted = {}

    async def get_leader_responses(self, channel, bot, leaders):
        await channel.send("هذا سؤال Doom، عندك القرار تجاوب أو تنسحب. إذا جاوبت إجابة خاطئة أو انتهى الوقت، يخسر فريقك كل النقاط. اختار 1 للقبول أو 2 للرفض (15 ثانية).")
        self.accepted = {}

        def check(msg):
            user = msg.author.name
            if user in leaders.values() and msg.content.strip() in ["1", "2"]:
                self.accepted[user] = msg.content.strip()
            return False

        await bot.wait_for_responses(15, check)

    async def ask(self, channel, bot, teams, leaders, points):
        await self.get_leader_responses(channel, bot, leaders)

        accepted_leaders = [user for user, val in self.accepted.items() if val == "1"]

        if len(accepted_leaders) == 0:
            await channel.send("كل الليدرات رفضوا سؤال Doom… تم تجاوز الجولة.")
            return points

        if len(accepted_leaders) == 1:
            leader = accepted_leaders[0]
            await channel.send(f"{leader} قبل التحدي! السؤال عليه الآن.")

            answered = []

            def check_answer(msg):
                if msg.author.name == leader and msg.author.name not in answered:
                    answered.append(msg.author.name)
                    return True
                return False

            await channel.send(f"السؤال: {self.question} (10 ثواني!)")
            msg = await bot.wait_for_message(10, check_answer)

            if msg and msg.content.strip().lower() == self.correct_answer:
                team = "أزرق" if leader == leaders["أزرق"] else "أحمر"
                for player in teams[team]:
                    points[player] = points.get(player, 0) * 2
                await channel.send(f"{leader} جاوب صح! نقاط فريقه تضاعفت!")
            else:
                team = "أزرق" if leader == leaders["أزرق"] else "أحمر"
                for player in teams[team]:
                    points[player] = 0
                await channel.send(f"{leader} جاوب غلط أو ما جاوب… فريقه خسر كل نقاطه!")
            return points

        await channel.send("الفريقين قبلوا التحدي! أول من يجاوب هو اللي يحسم مصير فريقه!")
        await channel.send(f"السؤال: {self.question} (10 ثواني!)")

        answered_by = None

        def check_any(msg):
            nonlocal answered_by
            if msg.content.strip().lower() == self.correct_answer and msg.author.name in points:
                answered_by = msg.author.name
            return False

        await bot.wait_for_responses(10, check_any)

        if not answered_by:
            await channel.send("ما جاوب أحد… الفريقين خسروا!")
            for player in points:
                points[player] = 0
            return points

        player_team = None
        for team, members in teams.items():
            if answered_by in members:
                player_team = team
                break

        team_total = sum(points[p] for p in teams[player_team])
        other_team = "أزرق" if player_team == "أحمر" else "أحمر"
        other_total = sum(points[p] for p in teams[other_team])

        if team_total > other_total:
            await channel.send(f"{answered_by} جاوب صح وفريقه أعلى نقاط… فازوا!")
        else:
            await channel.send(f"{answered_by} جاوب صح لكن فريقه أقل أو الإجابة خاطئة… خسر فريقه!")
            for player in teams[player_team]:
                points[player] = 0
        return points
