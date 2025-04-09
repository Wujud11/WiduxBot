
from flask import Flask, request, render_template, redirect, url_for
import json
import os

from bot.question_manager import QuestionManager

app = Flask(__name__)
manager = QuestionManager()

# قراءة التوكنات من البيئة
TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")

print(f"Twitch Access Token: {TWITCH_ACCESS_TOKEN}")
print(f"Twitch Client ID: {TWITCH_CLIENT_ID}")

@app.route('/')
def index():
    return redirect(url_for('questions'))

@app.route('/questions')
def questions():
    questions = manager.get_all_questions()
    return render_template('questions.html', questions=questions)

@app.route('/add-question', methods=['POST'])
def add_question():
    data = {
        "question": request.form.get("question"),
        "answer": request.form.get("answer"),
        "choices": request.form.get("choices")
    }
    manager.add_question(data)
    return redirect(url_for('questions'))
