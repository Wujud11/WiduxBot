
import asyncio
from twitchio.ext import commands
import os

# إعداد البوت
bot = commands.Bot(
    token=os.environ.get("TWITCH_ACCESS_TOKEN"),
    prefix="!",
    initial_channels=[os.environ.get("TWITCH_CHANNEL")]
)

@bot.event
async def event_ready():
    print(f"Logged in as | {bot.nick}")

@bot.event
async def event_message(message):
    if message.echo:
        return

    msg = message.content.strip().lower()

    if msg == "وج؟":
        await message.channel.send("هلا والله، إذا بتلعب لحالك اكتب فردي، إذا ضد آخرين اكتب تحدي، إذا فريق اكتب تيم.")

    await bot.handle_commands(message)

if __name__ == "__main__":
    bot.run()
