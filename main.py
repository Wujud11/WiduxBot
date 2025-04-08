
from flask import Flask
from twitchio.ext import commands
import os
import threading

print(">> [SYSTEM] Starting WiduxBot Debug V2...")

# إعداد Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "WiduxBot is running (Debug V2)!"

# إعداد TwitchIO
try:
    token = os.environ.get("TWITCH_ACCESS_TOKEN")
    channel = os.environ.get("TWITCH_CHANNEL")
    print(f">> [ENV] Token: {'OK' if token else 'MISSING'}, Channel: {channel}")
    
    bot = commands.Bot(
        token=token,
        prefix="!",
        initial_channels=[channel]
    )
    print(">> [BOT] Bot instance created successfully.")
except Exception as e:
    print(f">> [ERROR] Failed to create bot instance: {e}")

@bot.event
async def event_ready():
    try:
        print(f">> [BOT] Logged in as | {bot.nick}")
        print(f">> [BOT] Connected channels: {bot.connected_channels}")
    except Exception as e:
        print(f">> [ERROR] inside event_ready: {e}")

@bot.event
async def event_message(message):
    try:
        print(f">> [CHAT] Message from {message.author.name}: {message.content}")
        if message.echo:
            return

        msg = message.content.strip().lower()
        if msg == "وج؟":
            await message.channel.send("هلا والله، إذا بتلعب لحالك اكتب فردي، إذا ضد آخرين اكتب تحدي، إذا فريق اكتب تيم.")

        await bot.handle_commands(message)
    except Exception as e:
        print(f">> [ERROR] inside event_message: {e}")

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
