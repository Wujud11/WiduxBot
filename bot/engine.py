import asyncio
import random
from collections import defaultdict

from bot.questions.normal import TeamNormalQuestion
from bot.questions.golden import GoldenQuestion
from bot.questions.sabotage import SabotageQuestion
from bot.questions.doom import DoomQuestion
from bot.questions.fate import TestOfFate
from bot.questions.steal_or_boost import ChallengeStealOrBoostQuestion
from response import get_response

class WiduxEngine:
    def __init__(self, bot):
        self.bot = bot
        self.players = []
        self.blue_team = []
        self.red_team = []
        self.game_mode = None
        self.leader_selection = False
        self.blue_mentions = defaultdict(int)
        self.red_mentions = defaultdict(int)
        self.blue_leader = None
        self.red_leader = None
        self.main_player = None
        self.questions = []
        self.current_index = 0
        self.selected_game_mode = None
        self.waiting_for_normal_count = False

    async def handle_message(self, message):
        content = message.content.strip()
        sender = message.author.name

        if content == "ÙØ¬Ø":
            await message.channel.send("ÙÙØ§ ÙØ§ÙÙÙ! Ø¥Ø°Ø§ Ø¨ØªÙØ¹Ø¨ ÙØ­Ø§ÙÙ Ø§ÙØªØ¨ Ø³ÙÙÙØ Ø¥Ø°Ø§ Ø¶Ø¯ Ø§ÙÙÙ Ø§ÙØªØ¨ ØªØ­Ø¯ÙØ ÙØ¥Ø°Ø§ ÙØ¹ Ø±Ø¨Ø¹Ù Ø§ÙØªØ¨ ØªÙÙ.")
            return

        if content in ["Ø³ÙÙÙ", "ØªØ­Ø¯Ù", "ØªÙÙ"] and not self.game_mode and not self.waiting_for_normal_count:
            self.selected_game_mode = content
            self.main_player = sender
            self.waiting_for_normal_count = True
            await message.channel.send("Ø­Ø¯Ø¯ Ø¹Ø¯Ø¯ Ø§ÙØ£Ø³Ø¦ÙØ© Ø§ÙØ¹Ø§Ø¯ÙØ© ÙÙ 5 Ø¥ÙÙ 10.")
            return

        if self.waiting_for_normal_count and content.isdigit():
            count = int(content)
            if 5 <= count <= 10:
                self.waiting_for_normal_count = False
                self.game_mode = self.selected_game_mode

                if self.game_mode == "Ø³ÙÙÙ":
                    await message.channel.send("Ø¬Ø§Ø±Ù Ø¨Ø¯Ø¡ Ø§ÙÙØ¹Ø¨Ø©...")
                    await self.start_full_game(message.channel, count)

                elif self.game_mode == "ØªØ­Ø¯Ù":
                    await message.channel.send("Ø§ÙÙÙ Ø¨ÙÙØ¹Ø¨ ÙÙØªØ¨ 'R' ÙÙØªØ³Ø¬ÙÙ ÙØ¹ÙÙ 15 Ø«Ø§ÙÙØ©!")
                    await self.register_challenge_players(message.channel, count)

                elif self.game_mode == "ØªÙÙ":
                    await message.channel.send("ÙÙ ÙØ§Ø­Ø¯ ÙØ®ØªØ§Ø± ÙØ±ÙÙÙØ ÙÙØªØ¨ 'Ø£Ø²Ø±Ù' Ø£Ù 'Ø£Ø­ÙØ±' ÙØ¹ÙÙ 20 Ø«Ø§ÙÙØ©!")
                    await self.register_team_players(message.channel, count)
            else:
                await message.channel.send("Ø§ÙØ±Ø¬Ø§Ø¡ Ø§Ø®ØªÙØ§Ø± Ø±ÙÙ Ø¨ÙÙ 5 Ù10.")
            return

        if self.game_mode == "ØªØ­Ø¯Ù" and content.upper() == 'R' and sender not in self.players:
            self.players.append(sender)

        if self.game_mode == "ØªÙÙ" and not self.leader_selection:
            if content == 'Ø£Ø²Ø±Ù' and sender not in self.blue_team and sender not in self.red_team:
                self.blue_team.append(sender)
            elif content == 'Ø£Ø­ÙØ±' and sender not in self.red_team and sender not in self.blue_team:
                self.red_team.append(sender)

        if self.leader_selection and self.game_mode == "ØªÙÙ":
            mentioned_players = self.extract_mentions(content)
            for player in mentioned_players:
                if player in self.blue_team:
                    self.blue_mentions[player] += 1
                elif player in self.red_team:
                    self.red_mentions[player] += 1

    def extract_mentions(self, text):
        return [word[1:] for word in text.split() if word.startswith('@')]

    async def register_challenge_players(self, channel, normal_count):
        await asyncio.sleep(15)
        if len(self.players) < 2:
            await self.reset_game(channel, "ÙØ§ ÙÙÙ Ø¹Ø¯Ø¯ ÙØ§ÙÙ ÙØ¨Ø¯Ø£ ÙÙÙ Ø§ÙØªØ­Ø¯Ù.")
        else:
            await channel.send(f"ØªÙ ØªØ³Ø¬ÙÙ Ø§ÙÙØ§Ø¹Ø¨ÙÙ: {', '.join(self.players)}")
            await self.start_full_game(channel, normal_count)

    async def register_team_players(self, channel, normal_count):
        await asyncio.sleep(20)
        if len(self.blue_team) < 3 or len(self.red_team) < 3:
            await self.reset_game(channel, "ÙØ§Ø²Ù Ù£ ÙØ§Ø¹Ø¨ÙÙ Ø¹ÙÙ Ø§ÙØ£ÙÙ ÙÙ ÙÙ ÙØ±ÙÙ.")
        else:
            await channel.send(f"Ø§ÙÙØ±ÙÙ Ø§ÙØ£Ø²Ø±Ù: {', '.join(self.blue_team)}")
            await channel.send(f"Ø§ÙÙØ±ÙÙ Ø§ÙØ£Ø­ÙØ±: {', '.join(self.red_team)}")
            await self.select_team_leaders(channel, normal_count)

    async def select_team_leaders(self, channel, normal_count):
        self.leader_selection = True
        await channel.send("Ø§Ø®ØªØ§Ø±ÙØ§ Ø§ÙÙÙØ¯Ø±! ÙÙØ´ÙÙÙ Ø®ÙØ§Ù 10 Ø«ÙØ§ÙÙ.")
        await asyncio.sleep(10)

        self.blue_leader = max(self.blue_mentions.items(), key=lambda x: x[1])[0] if self.blue_mentions else random.choice(self.blue_team)
        self.red_leader = max(self.red_mentions.items(), key=lambda x: x[1])[0] if self.red_mentions else random.choice(self.red_team)

        await channel.send(f"ÙÙØ¯Ø± Ø§ÙØ£Ø²Ø±Ù: {self.blue_leader}")
        await channel.send(f"ÙÙØ¯Ø± Ø§ÙØ£Ø­ÙØ±: {self.red_leader}")
        await self.start_full_game(channel, normal_count)

    async def start_full_game(self, channel, normal_count):
        self.questions = []
        self.questions += [{"type": "normal"}] * normal_count
        self.questions.append({"type": "golden"})
        self.questions.append({"type": "steal_or_boost"})
        self.questions.append({"type": "sabotage"})
        self.questions.append({"type": "fate"})
        self.questions.append({"type": "doom"})

        self.current_index = 0
        await channel.send("Ø§ÙÙØ¹Ø¨Ø© Ø¨Ø¯Ø£Øª! Ø§Ø³ØªØ¹Ø¯ ÙÙØ³Ø¤Ø§Ù Ø§ÙØ£ÙÙ...")
        await self.ask_next_question(channel)

    async def ask_next_question(self, channel):
        if self.current_index >= len(self.questions):
            await channel.send("Ø§ÙØªÙØª Ø¬ÙÙØ¹ Ø§ÙØ£Ø³Ø¦ÙØ©!")

            if self.game_mode == "Ø³ÙÙÙ":
                winner = self.main_player
                msg = get_response("solo_win_responses", context={"player": winner})
                await channel.send(msg)

            elif self.game_mode == "ØªØ­Ø¯Ù":
                winner = self.players[0] if self.players else "ÙØ§Ø¹Ø¨"
                lose_msg = get_response("group_lose_responses")
                win_msg = get_response("group_win_responses", context={"player": winner})
                await channel.send(lose_msg)
                await channel.send(win_msg)

            elif self.game_mode == "ØªÙÙ":
                winning_team = "Ø£Ø²Ø±Ù"
                losing_team = "Ø£Ø­ÙØ±"
                win_msg = get_response("team_win_responses", context={"team": winning_team})
                lose_msg = get_response("team_lose_responses", context={"team": losing_team})
                await channel.send(win_msg)
                await channel.send(lose_msg)

            return

        q = self.questions[self.current_index]
        self.current_index += 1

        try:
            if q["type"] == "doom":
                qobj = DoomQuestion()
                await qobj.ask(channel)

            elif q["type"] == "fate":
                qobj = TestOfFate()
                await qobj.ask(channel)

            elif q["type"] == "sabotage":
                qobj = SabotageQuestion()
                await qobj.ask(channel)

            elif q["type"] == "steal_or_boost":
                qobj = ChallengeStealOrBoostQuestion()
                await qobj.ask(channel)

            elif q["type"] == "golden":
                qobj = GoldenQuestion()
                await qobj.ask(channel)

            elif q["type"] == "normal":
                qobj = TeamNormalQuestion()
                await qobj.ask(channel)

            else:
                await channel.send(f"ÙÙØ¹ Ø§ÙØ³Ø¤Ø§Ù ØºÙØ± ÙØ¹Ø±ÙÙ: {q['type']}")

        except Exception as e:
            await channel.send(f"Ø®Ø·Ø£ Ø£Ø«ÙØ§Ø¡ ØªÙÙÙØ° Ø§ÙØ³Ø¤Ø§Ù: {str(e)}")

    async def reset_game(self, channel=None, notice=None):
        if channel and notice:
            await channel.send(notice)

        self.players.clear()
        self.blue_team.clear()
        self.red_team.clear()
        self.game_mode = None
        self.leader_selection = False
        self.blue_mentions.clear()
        self.red_mentions.clear()
        self.blue_leader = None
        self.red_leader = None
        self.main_player = None
        self.questions = []
        self.current_index = 0
        self.selected_game_mode = None
        self.waiting_for_normal_count = False
