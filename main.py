
from flask import Flask
from twitchio.ext import commands
import os
import threading

print(">> [SYSTEM] Starting WiduxBot...")

# إعداد Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "WiduxBot is running!"

# إعداد TwitchIO
try:
    bot = commands.Bot(
        token=os.environ.get("TWITCH_ACCESS_TOKEN"),
        prefix="!",
        initial_channels=[os.environ.get("TWITCH_CHANNEL")]
    )
    print(">> [BOT] Bot instance created successfully.")
except Exception as e:
    print(f">> [ERROR] Failed to create bot instance: {e}")

@bot.event
async def event_ready():
    print(f">> [BOT] Logged in as | {bot.nick}")
    print(f">> [BOT] Joined channels: {bot.connected_channels}")

@bot.event
async def event_message(message):
    print(f">> [CHAT] Received message: {message.content} from {message.author.name}")
    if message.echo:
        return

    msg = message.content.strip().lower()

    if msg == "وج؟":
        await message.channel.send("هلا والله، إذا بتلعب لحالك اكتب فردي، إذا ضد آخرين اكتب تحدي، إذا فريق اكتب تيم.")

    await bot.handle_commands(message)

def run_bot():
    try:
        print(">> [THREAD] Running bot...")
        bot.run()
    except Exception as e:
        print(f">> [ERROR] Bot failed to run: {e}")

# تشغيل البوت والفلاسك معًا
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    print(">> [FLASK] Running Flask app...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
