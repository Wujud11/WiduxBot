
from flask import Flask, request, render_template, redirect, url_for
import json
import os

from bot.settings import BotSettings

app = Flask(__name__)
settings = BotSettings()

@app.route('/')
def index():
    return redirect(url_for('channels'))

@app.route('/channels')
def channels():
    return render_template('channels.html', settings=settings)

@app.route('/add-channel', methods=['POST'])
def add_channel():
    channel_name = request.form['channel_name']
    settings.update_setting(channel_name, {})
    return redirect(url_for('channels'))

@app.route('/delete-channel/<channel_name>')
def delete_channel(channel_name):
    settings.settings.pop(channel_name, None)
    settings.save_settings()
    return redirect(url_for('channels'))

if __name__ == '__main__':
    app.run(debug=True)
