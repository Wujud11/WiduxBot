
from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# مكان حفظ الأسئلة
QUESTIONS_FILE_PATH = "questions_bank.json"

# قراءة الأسئلة من ملف JSON
def load_questions():
    if os.path.exists(QUESTIONS_FILE_PATH):
        with open(QUESTIONS_FILE_PATH, 'r', encoding='utf-8') as file:
            return json.load(file).get("questions", [])
    return []

# إضافة سؤال جديد إلى الملف
def add_question_to_file(question_data):
    questions = load_questions()
    questions.append(question_data)
    with open(QUESTIONS_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump({"questions": questions}, file, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return redirect(url_for('questions'))

@app.route('/questions')
def questions():
    questions = load_questions()
    return render_template('control_panel_questions.html', questions=questions)

@app.route('/add-question', methods=['POST'])
def add_question():
    question = request.form.get("question")
    correct_answer = request.form.get("correct_answer")
    choices = request.form.get("choices").split(',')
    category = request.form.get("category")
    question_type = request.form.get("question_type")
    
    new_question = {
        "question": question,
        "answer": correct_answer,
        "choices": choices,
        "category": category,
        "question_type": question_type
    }
    
    add_question_to_file(new_question)
    return redirect(url_for('questions'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # تحديد المنفذ 5000
