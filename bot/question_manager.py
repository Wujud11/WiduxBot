
import json
import os

QUESTIONS_FILE = "questions_bank.json"

class QuestionManager:
    def __init__(self):
        self.questions = []
        self.load_questions()

    def load_questions(self):
        if os.path.exists(QUESTIONS_FILE):
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.questions = data.get("questions", [])
        else:
            self.questions = []

    def save_questions(self):
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump({"questions": self.questions}, f, ensure_ascii=False, indent=2)

    def add_question(self, question_data):
        self.questions.append(question_data)
        self.save_questions()

    def update_question(self, index, updated_data):
        if 0 <= index < len(self.questions):
            self.questions[index] = updated_data
            self.save_questions()

    def delete_question(self, index):
        if 0 <= index < len(self.questions):
            del self.questions[index]
            self.save_questions()

    def import_questions(self, new_questions, append=True):
        if append:
            self.questions.extend(new_questions)
        else:
            self.questions = new_questions
        self.save_questions()

    def get_all_questions(self):
        return self.questions
