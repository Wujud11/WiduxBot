from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__, template_folder="templates")

SETTINGS_FILE = "bot_settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/settings", methods=["GET"])
def show_settings():
    settings = load_settings()
    return render_template("settings.html", settings=settings)

@app.route("/update-settings", methods=["POST"])
def update_settings():
    fields = [
        "solo_win_responses",
        "group_win_responses",
        "team_win_responses",
        "low_score_responses",
        "doom_leader_fail_responses",
        "lowest_leader_responses",
        "team_lose_responses",
        "solo_lose_responses",
        "group_individual_lose_responses",
        "mention_guard_limit",
        "mention_guard_duration",
        "mention_guard_cooldown",
        "mention_guard_warning_thresh",
        "mention_guard_warn_msg",
        "mention_guard_timeout_msg",
        "special_mention_responses",  # تم إضافة هذا الحقل
    ]

    new_settings = load_settings()

    for field in fields:
        data = request.form.get(field, "")
        new_settings[field] = [line.strip() for line in data.splitlines() if line.strip()]

    # تحديث twitch info
    new_settings["current_channel"] = request.form.get("current_channel", "").strip()
    new_settings["bot_username"] = request.form.get("bot_username", "").strip()
    new_settings["access_token"] = request.form.get("access_token", "").strip()

    save_settings(new_settings)
    return redirect("/settings")

if __name__ == "__main__":
    app.run(debug=True)
