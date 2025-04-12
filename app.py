from flask import Flask, render_template, request, redirect, url_for
from settings_manager import SettingsManager
from bot.question_manager import QuestionManager

app = Flask(__name__)

settings = SettingsManager()
manager = QuestionManager()


@app.route('/')
def index():
    return render_template("settings.html", settings=settings.settings)


# ----------------- إعدادات البوت العامة -----------------
@app.route('/update-settings', methods=['POST'])
def update_settings():
    settings.update_bot_settings(request.form)
    return redirect('/')


# ----------------- إدارة القنوات -----------------
@app.route('/channels')
def channels():
    return render_template("channels.html", settings=settings)


@app.route('/add-channel', methods=['POST'])
def add_channel():
    channel_name = request.form.get("channel_name")
    settings.add_channel(channel_name)
    return redirect("/channels")


@app.route('/delete-channel/<channel_name>')
def delete_channel(channel_name):
    settings.delete_channel(channel_name)
    return redirect("/channels")


@app.route('/channel-settings/<channel_name>')
def channel_settings(channel_name):
    channel_settings = settings.get_channel_settings(channel_name)
    return render_template("channel_settings.html", channel_name=channel_name, channel_settings=channel_settings)


@app.route('/update-channel-settings/<channel_name>', methods=['POST'])
def update_channel_settings(channel_name):
    settings.update_channel_settings(channel_name, request.form)
    return redirect("/channels")


# ----------------- إدارة الأسئلة -----------------
@app.route('/questions')
def questions():
    return render_template("questions_management.html", questions=manager.get_all_questions())


@app.route('/add-question', methods=['POST'])
def add_question():
    manager.add_question(request.form)
    return redirect("/questions")


@app.route('/edit-question/<int:index>')
def edit_question(index):
    q = manager.get_question(index)
    return render_template("edit_question.html", question=q, index=index)


@app.route('/edit-question/<int:index>', methods=['POST'])
def update_question(index):
    manager.edit_question(index, request.form)
    return redirect("/questions")


@app.route('/delete-question/<int:index>')
def delete_question(index):
    manager.delete_question(index)
    return redirect("/questions")


# ----------------- إدارة الردود -----------------
@app.route('/responses')
def responses():
    custom_responses = settings.get_setting("custom_responses") or {}
    return render_template("responses.html", responses=custom_responses)


@app.route('/save_responses', methods=["POST"])
def save_responses():
    settings.update_custom_responses(request.form)
    return redirect("/responses")


if __name__ == '__main__':
    app.run(debug=True)