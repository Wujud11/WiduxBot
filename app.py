
from flask import Flask, render_template, request

app = Flask(__name__)

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

# تعديل المنفذ ليعمل بشكل صحيح على Render
@app.route('/control-panel', methods=['GET', 'POST'])
def control_panel():
    if request.method == 'POST':
        # إضافة منطق لإدارة الإعدادات هنا
        pass
    return render_template('control_panel.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # تحديد المنفذ 5000
