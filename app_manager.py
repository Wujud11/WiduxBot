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

        # إضافة تحديثات المنشن
        settings.update_setting("mention_guard_limit", int(request.form.get("mention_guard_limit", 2)))
        settings.update_setting("mention_guard_duration", int(request.form.get("mention_guard_duration", 5)))
        settings.update_setting("mention_guard_cooldown", int(request.form.get("mention_guard_cooldown", 86400)))
        settings.update_setting("mention_guard_warning_thresh", int(request.form.get("mention_guard_warning_thresh", 2)))
        settings.update_setting("mention_guard_warn_msg", request.form.get("mention_guard_warn_msg", "ترى ببلعك تايم أوت"))
        settings.update_setting("mention_guard_timeout_msg", request.form.get("mention_guard_timeout_msg", "القم! أنا حذرتك"))

        # تحديث الردود الخاصة
        mention_responses = request.form.get("special_mention_responses", "")
        special_responses = {key: value.split(",") for key, value in (mention_responses.items())}
        settings.update_setting("special_mention_responses", special_responses)

        return redirect("/settings")

    return render_template("settings.html", settings=settings.get_all_settings())

if __name__ == "__main__":
    app.run(debug=True)
