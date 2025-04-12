import asyncio
from bot.questions.doom import DoomQuestion
from utils.responses import get_response

# نجهز قناة وهمية للتجربة
class MockChannel:
    async def send(self, msg):
        print("[Channel]:", msg)

# بوت وهمي فيه انتظار رسائل
class MockBot:
    async def wait_for_responses(self, seconds, check_fn):
        await asyncio.sleep(1)
        print(f"[Bot]: انتظر {seconds} ثانية (محاكاة)")
    
    async def wait_for_message(self, seconds, check_fn):
        await asyncio.sleep(1)
        print(f"[Bot]: انتظار رسالة من القائد (محاكاة)")

# دالة طقطقة القائد الأقل نقاط
async def taunt_lowest_leader(leaders, points, channel):
    lowest_leader = None
    lowest_score = float("inf")

    for team_name, leader in leaders.items():
        leader_score = points.get(leader, 0)
        if leader_score < lowest_score:
            lowest_score = leader_score
            lowest_leader = leader

    if lowest_leader:
        msg = get_response("lowest_leader_responses", {"leader": lowest_leader})
        if msg:
            await channel.send(msg)

# تجربة doom + طقطقة
async def run_game():
    channel = MockChannel()
    bot = MockBot()

    doom_q = DoomQuestion(
        question="من هو مؤسس بايثون؟",
        correct_answer="جيدو فان روسوم",
        alt_answers=["guido van rossum", "جيدو"]
    )

    leaders = {"أزرق": "سارة", "أحمر": "خالد"}
    teams = {
        "أزرق": ["سارة", "لولوة", "فيصل"],
        "أحمر": ["خالد", "عبدالله", "جوجو"]
    }
    points = {
        "سارة": 30,
        "لولوة": 60,
        "فيصل": 40,
        "خالد": 10,
        "عبدالله": 80,
        "جوجو": 50
    }

    await doom_q.ask(channel, bot, leaders, teams, points)

    # نطقطق على أضعف ليدر بعد سؤال doom
    await taunt_lowest_leader(leaders, points, channel)

# تشغيل الكود
if __name__ == "__main__":
    asyncio.run(run_game())