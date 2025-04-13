from flask import Flask, request, render_template, redirect, url_for
import json
import os

from bot.question_manager import QuestionManager

app = Flask(__name__)
manager = QuestionManager()

@app.route('/questions')
def questions():
    questions = manager.get_all_questions()
    return render_template('questions_management.html', questions=questions)

@app.route('/add-question', methods=['POST'])
def add_question():
    data = {
        "question": request.form['question'],
        "correct_answer": request.form['correct_answer'],
        "alt_answers": [ans.strip() for ans in request.form['alt_answers'].split(',')] if request.form['alt_answers'] else [],
        "category": request.form['category'],
        "type": request.form['type']
    }
    manager.add_question(data)
    return redirect(url_for('questions'))

@app.route('/edit-question/<int:index>', methods=['GET', 'POST'])
def edit_question(index):
    question = manager.get_all_questions()[index]
    if request.method == 'POST':
        updated_data = {
            "question": request.form['question'],
            "correct_answer": request.form['correct_answer'],
            "alt_answers": [ans.strip() for ans in request.form['alt_answers'].split(',')] if request.form['alt_answers'] else [],
            "category": request.form['category'],
            "type": request.form['type']
        }
        manager.update_question(index, updated_data)
        return redirect(url_for('questions'))
    return render_template('edit_question.html', question=question, index=index)

@app.route('/delete-question/<int:index>')
def delete_question(index):
    manager.delete_question(index)
    return redirect(url_for('questions'))

if __name__ == '__main__':
    app.run(debug=True)
