import requests
import random

class QuestionManager:
    def __init__(self):
        self.api_url = "http://localhost:9001/api/questions"
        self.questions_by_type = {
            "Normal": [],
            "Golden": [],
            "Steal": [],
            "Sabotage": [],
            "Doom": [],
            "Fate": []
        }

    def load_questions(self):
        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                questions = response.json()
                for q in questions:
                    qtype = q["type"]
                    if qtype in self.questions_by_type:
                        self.questions_by_type[qtype].append(q)
            else:
                print("فشل في جلب الأسئلة من API")
        except Exception as e:
            print(f"خطأ في الاتصال بـ API: {e}")

    def get_questions_by_type(self, qtype, count=None):
        if not self.questions_by_type[qtype]:
            self.load_questions()

        questions = self.questions_by_type[qtype]

        if count:
            return random.sample(questions, min(count, len(questions)))
        return questions

    def get_random_question(self, qtype):
        if not self.questions_by_type[qtype]:
            self.load_questions()

        questions = self.questions_by_type[qtype]
        return random.choice(questions) if questions else None
