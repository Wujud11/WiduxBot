from utils.responses import get_response

async def taunt_lowest_leader(leaders, points, channel):
    lowest_leader = None
    lowest_score = float("inf")

    for team_name, leader in leaders.items():
        leader_score = points.get(leader, 0)
        if leader_score < lowest_score:
            lowest_score = leader_score
            lowest_leader = leader

    if lowest_leader:
        msg = get_response("taunts_leader", {"leader": lowest_leader})
        if msg:
            await channel.send(msg)