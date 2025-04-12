
from flask import Flask, request, render_template, redirect, url_for
import json
import os

from bot.settings import BotSettings

app = Flask(__name__)
settings = BotSettings()

@app.route('/channel/<channel_name>')
def channel_settings(channel_name):
    channel_settings = settings.get_setting(channel_name)
    return render_template('channel_settings.html', channel_name=channel_name, channel_settings=channel_settings)

@app.route('/update-channel-settings/<channel_name>', methods=['POST'])
def update_channel_settings(channel_name):
    timeout_duration = request.form.get('timeout_duration', type=int)
    mention_limit = request.form.get('mention_limit', type=int)
    warning_message = request.form.get('warning_message', type=str)
    timeout_message = request.form.get('timeout_message', type=str)

    # تحديث الإعدادات للقناة
    channel_settings = {
        "mention_limit": mention_limit,
        "timeout_duration": timeout_duration,
        "warning_message": warning_message,
        "timeout_message": timeout_message
    }
    settings.update_setting(channel_name, channel_settings)
    return redirect(url_for('channel_settings', channel_name=channel_name))

if __name__ == '__main__':
    app.run(debug=True)
