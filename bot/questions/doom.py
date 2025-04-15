import asyncio
from utils.responses import get_response
from utils.leader_utils import taunt_lowest_leader

class DoomQuestion:
    def __init__(self, question, correct_answer, alt_answers=None):
        self.question = question
        self.correct_answer = correct_answer.lower()
        self.alt_answers = [ans.lower() for ans in (alt_answers or [])]

    async def ask(self, channel, bot, leaders, teams, points):
        await channel.send("سؤال DOOM! القادة فقط يقررون... هل يقبلون التحدي؟")
        await channel.send("رد بـ 1 لقبول التحدي، أو 2 لرفضه خلال 15 ثانية.")

        accepted_leaders = []
        answered = []

        def check_decision(msg):
            user = msg.author.name
            content = msg.content.strip()
            if user in leaders.values() and user not in answered:
                answered.append(user)
                if content == "1":
                    accepted_leaders.append(user)
            return False

        await bot.wait_for_responses(15, check_decision)

        if not accepted_leaders:
            await channel.send("كل الليدرات رفضوا سؤال Doom… تم تجاوز الجولة.")
            await end_team_game(leaders, teams, points, channel)
            return points

        if len(accepted_leaders) == 1:
            leader = accepted_leaders[0]
            await channel.send(f"{leader} هو القائد الوحيد اللي قبل التحدي!")
            await channel.send(f"السؤال: {self.question} (10 ثواني!)")

            def check_answer(msg):
                if msg.author.name == leader:
                    response = msg.content.strip().lower()
                    all_answers = [self.correct_answer] + self.alt_answers
                    return response in all_answers
                return False

            try:
                await bot.wait_for_message(10, check_answer)
                await channel.send(f"{leader} جاوب صح! نقاط فريقه تتضاعف.")
                team = "أزرق" if leader in teams["أزرق"] else "أحمر"
                for player in teams[team]:
                    points[player] *= 2
            except asyncio.TimeoutError:
                await channel.send(f"{leader} ما جاوب في الوقت المحدد! نقاط فريقه صارت صفر.")
                team = "أزرق" if leader in teams["أزرق"] else "أحمر"
                for player in teams[team]:
                    points[player] = 0
                msg = get_response("doomed_leader_responses", {"leader": leader})
                if msg:
                    await channel.send(msg)

        elif len(accepted_leaders) == 2:
            await channel.send("الفريقين قبلوا التحدي! القادة فقط من يجاوب الآن.")
            await channel.send(f"السؤال: {self.question} (10 ثوانٍ!)")

            answered_by = None
            correct = None

            def check_any(msg):
                nonlocal answered_by, correct
                user = msg.author.name
                response = msg.content.strip().lower()
                all_answers = [self.correct_answer] + self.alt_answers
                if user in leaders.values() and answered_by is None:
                    answered_by = user
                    correct = response in all_answers
                return False

            await bot.wait_for_responses(10, check_any)

            if not answered_by:
                await channel.send("ما جاوب أحد… الفريقين خسروا!")
                for player in points:
                    points[player] = 0
                await end_team_game(leaders, teams, points, channel)
                return points

            winner_leader = answered_by
            loser_leader = [l for l in leaders.values() if l != winner_leader][0]

            winner_team = "أزرق" if winner_leader in teams["أزرق"] else "أحمر"
            loser_team = "أحمر" if winner_team == "أزرق" else "أزرق"

            if not correct:
                await channel.send(f"{winner_leader} جاوب خطأ! فريقه خسر الجولة.")
                for player in teams[winner_team]:
                    points[player] = 0
                msg = get_response("doomed_leader_responses", {"leader": winner_leader})
                if msg:
                    await channel.send(msg)
            else:
                score_winner = sum(points.get(p, 0) for p in teams[winner_team])
                score_loser = sum(points.get(p, 0) for p in teams[loser_team])

                if score_winner > score_loser:
                    for player in teams[winner_team]:
                        points[player] *= 2
                    await channel.send(f"{winner_leader} جاوب صح وفريقه تفوق بالنقاط! الفريق الثاني خسر الجولة.")
                    for player in teams[loser_team]:
                        points[player] = 0
                    msg = get_response("doomed_leader_responses", {"leader": loser_leader})
                    if msg:
                        await channel.send(msg)
                else:
                    await channel.send(f"{winner_leader} جاوب صح لكن فريقه أضعف بالنقاط! يخسر الجولة.")
                    for player in teams[winner_team]:
                        points[player] = 0
                    msg = get_response("doomed_leader_responses", {"leader": winner_leader})
                    if msg:
                        await channel.send(msg)

        await end_team_game(leaders, teams, points, channel)
        return points


async def end_team_game(leaders, teams, points, channel):
    team_scores = {"أزرق": 0, "أحمر": 0}
    for team in teams:
        team_scores[team] = sum(points.get(player, 0) for player in teams[team])

    winning_team = max(team_scores, key=team_scores.get)
    losing_team = min(team_scores, key=team_scores.get)

    win_msg = get_response("team_win", {"team": winning_team})
    if win_msg:
        await channel.send(win_msg)

    lose_msg = get_response("taunts_lose", {"team": losing_team})
    if lose_msg:
        await channel.send(lose_msg)

    # التحقق إذا القائد أضعف نقاط
    for team, leader in leaders.items():
        team_points = {p: points.get(p, 0) for p in teams[team]}
        if leader in team_points:
            if team_points[leader] == min(team_points.values()):
                msg = get_response("weak_leader_responses", {"leader": leader})
                if msg:
                    await channel.send(msg)

    await taunt_lowest_leader(leaders, points, channel)
