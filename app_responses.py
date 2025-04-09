
from flask import Flask, request, render_template, redirect, url_for
import json
import os

from bot.settings import BotSettings

app = Flask(__name__)
settings = BotSettings()

@app.route('/responses')
def responses():
    return render_template('responses.html', settings=settings)

@app.route('/update-responses', methods=['POST'])
def update_responses():
    win_solo = request.form.get('win_solo')
    lose_team = request.form.get('lose_team')

    # تحديث الردود الخاصة
    responses = {
        "win_solo": win_solo,
        "lose_team": lose_team
    }
    settings.update_setting('custom_responses', responses)
    return redirect(url_for('responses'))

if __name__ == '__main__':
    app.run(debug=True)
