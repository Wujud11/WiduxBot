
from flask import Flask
from twitchio.ext import commands
import os
import threading

# إعداد Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "WiduxBot is running!"

# إعداد TwitchIO
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

# تشغيل البوت والفلاسك معًا
if __name__ == "__main__":
    threading.Thread(target=bot.run).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
