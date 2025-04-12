from flask import Flask, render_template, request, redirect
from bot.settings_manager import BotSettings

app = Flask(__name__)
settings = BotSettings()

@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    if request.method == "POST":
        settings.update_setting("current_channel", request.form.get("current_channel", ""))
        settings.update_setting("bot_username", request.form.get("bot_username", ""))
        settings.update_setting("access_token", request.form.get("access_token", ""))

        mention_raw = request.form.get("mention_responses", "")
        mention_list = [line.strip() for line in mention_raw.splitlines() if line.strip()]
        settings.update_setting("mention_responses", mention_list)

        return redirect("/settings")

    return render_template("settings.html", settings=settings.get_all_settings())

if __name__ == "__main__":
    app.run(debug=True)