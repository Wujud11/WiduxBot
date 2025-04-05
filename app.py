import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///waj_bot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Configuration for the bot
class Config:
    def __init__(self):
        # تحقق من وجود المعلومات السرية في المتغيرات البيئية
        self.token = os.environ.get('TWITCH_TOKEN', '')
        self.client_id = os.environ.get('TWITCH_CLIENT_ID', '')
        
        # هذه قيم مؤقتة للتطوير فقط (تمت إزالتها لأمان أفضل)
        if not self.token or not self.client_id:
            logger.warning("الرمز المميز أو معرف العميل مفقود. يرجى تعيين متغيرات البيئة.")
        # قائمة القنوات النشطة (إذا كانت فارغة، سيتم استيرادها من الملف)
        self.active_channels = []
        self.questions = {}
        self.custom_messages = {
            'welcome_message': 'هلا والله! إذا بتلعب معي اكتب "اتحداك" إذا ضد فريق اكتب "تحدي" وإذا فريقين اكتب "تيم".',
            'winner_message': 'مبروك للفائز! 🎉',
            'loser_message': 'حظ أوفر في المرة القادمة! 😅',
            'low_score_message': 'زين باقي معك شوية عقل يمشي أمورك! 😂'
        }
        # تهيئة ردود الطقطقة
        self.funny_responses = [
            "أقل من 50؟ مبروك، جبت رقم قياسي! على الاغبياء",
            "أقل من 50؟ احسك تمزح مستحيل",
            "لو نايم مو ازين لك ولنا",
            "مبروك فزت معانا بدورة لتطوير",
            "يمكن المرة الجاية تظبط لاحظ انها (تظبط)",
            "50؟ عقلك محدووودالذكاء",
            "أقل من 50؟ أعتقد عقلك نايم",
            "50 نقطة؟ مايحتاج اتكلم",
            "واضح مااااافيه عقل",
            "أقل من 50؟ والله جبت أقل من توقعاتي... المرة الجاية اكيد تحت الصفر",
            "أقل من 50؟ بس بس كفاية اليوم!",
            "خلاص روح جرب ألعاب ثانية، هذي مو لك!",
            "عقلك مو معك ضدك!",
            "50 نقطة؟ ههههههههههههههههه",
            "لاحول ولا قوة الا بالله جبت أقل من 50؟ كيف فكرت في السؤال؟",
            "عقلك نايم روح كمل نوم معه",
            "زين باقي معك شوية عقل يمشي أمورك",
            "ماشاءالله وعدم الذكاء اللي عندك",
            "المرة الجاية بغششك لأن الغباء هذا كارثة",
            "أقل من 50؟ صدقني لو لاعب حقرة بقرة ازين لك"
        ]
    
    def save(self):
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'active_channels': self.active_channels,
                    'custom_messages': self.custom_messages,
                    'funny_responses': self.funny_responses
                }, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def load(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.active_channels = data.get('active_channels', [])
                    self.custom_messages = data.get('custom_messages', self.custom_messages)
                    if 'funny_responses' in data:
                        self.funny_responses = data.get('funny_responses')
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return False

# Initialize config
config = Config()
config.load()

# Import models after db initialization to avoid circular imports
with app.app_context():
    from models import Question, FunnyResponse, GameStats, Channel
    db.create_all()

@app.route('/')
def index():
    """Home page with information about the bot and an add to channel button"""
    # تشغيل البوت عند زيارة الصفحة الرئيسية (إذا لم يكن يعمل بالفعل)
    from main import start_bot_thread
    start_bot_thread()
    return render_template('index.html')

@app.route('/config', methods=['GET', 'POST'])
def configure():
    """Configuration page for the bot"""
    if request.method == 'POST':
        # Handle channel addition
        if 'add_channel' in request.form:
            channel = request.form.get('channel').strip().lower()
            if channel and channel not in config.active_channels:
                config.active_channels.append(channel)
                config.save()
                flash(f'Channel {channel} added successfully!', 'success')
            else:
                flash('Channel is already added or invalid.', 'danger')
        
        # Handle channel removal
        elif 'remove_channel' in request.form:
            channel = request.form.get('channel').strip().lower()
            if channel in config.active_channels:
                config.active_channels.remove(channel)
                config.save()
                flash(f'Channel {channel} removed successfully!', 'success')
            else:
                flash('Channel not found in active channels.', 'danger')
        
        # Handle custom message updates
        elif 'update_messages' in request.form:
            config.custom_messages['welcome_message'] = request.form.get('welcome_message', config.custom_messages['welcome_message'])
            config.custom_messages['winner_message'] = request.form.get('winner_message', config.custom_messages['winner_message'])
            config.custom_messages['loser_message'] = request.form.get('loser_message', config.custom_messages['loser_message'])
            config.custom_messages['low_score_message'] = request.form.get('low_score_message', config.custom_messages['low_score_message'])
            config.save()
            flash('Custom messages updated successfully!', 'success')
        
        return redirect(url_for('configure'))
    
    return render_template('config.html', 
                           active_channels=config.active_channels,
                           custom_messages=config.custom_messages)

@app.route('/add-to-channel/<channel>')
def add_to_channel(channel):
    """Add the bot to a specific channel"""
    if channel not in config.active_channels:
        config.active_channels.append(channel.lower())
        config.save()
        flash(f'Bot added to channel {channel}!', 'success')
    else:
        flash(f'Bot is already in channel {channel}.', 'info')
    return redirect(url_for('configure'))

@app.route('/auth-redirect')
def auth_redirect():
    """Handle Twitch OAuth redirection"""
    return redirect(url_for('configure'))

@app.route('/questions', methods=['GET', 'POST'])
def questions():
    """صفحة إدارة الأسئلة"""
    if request.method == 'POST':
        # إضافة سؤال جديد
        text = request.form.get('text')
        answer = request.form.get('answer')
        category = request.form.get('category')
        question_type = request.form.get('question_type')
        difficulty = int(request.form.get('difficulty', 1))
        
        question = Question(
            text=text,
            answer=answer,
            category=category,
            question_type=question_type,
            difficulty=difficulty
        )
        db.session.add(question)
        db.session.commit()
        
        flash('تمت إضافة السؤال بنجاح!', 'success')
        return redirect(url_for('questions'))
    
    # جلب جميع الأسئلة
    all_questions = Question.query.all()
    categories = db.session.query(Question.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    # حساب عدد الأسئلة في كل تصنيف
    category_counts = {}
    for cat in categories:
        count = Question.query.filter_by(category=cat).count()
        category_counts[cat] = count
    
    return render_template('questions.html', 
                          questions=all_questions, 
                          categories=categories,
                          category_counts=category_counts)

@app.route('/questions/run-script', methods=['POST'])
def run_questions_script():
    """تشغيل سكريبت إضافة الأسئلة"""
    try:
        from questions_script import add_user_questions, add_funny_responses
        with app.app_context():
            add_user_questions()
            add_funny_responses()
        flash('تم إضافة مكتبة الأسئلة بنجاح!', 'success')
    except Exception as e:
        logger.error(f"Error adding questions: {e}")
        flash(f'حدث خطأ أثناء إضافة الأسئلة: {str(e)}', 'danger')
    return redirect(url_for('questions'))

@app.route('/questions/edit/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    """تعديل سؤال"""
    question = Question.query.get_or_404(id)
    
    if request.method == 'POST':
        question.text = request.form.get('text')
        question.answer = request.form.get('answer')
        question.category = request.form.get('category')
        question.question_type = request.form.get('question_type')
        question.difficulty = int(request.form.get('difficulty', 1))
        
        db.session.commit()
        flash('تم تحديث السؤال بنجاح!', 'success')
        return redirect(url_for('questions'))
    
    categories = db.session.query(Question.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('edit_question.html', question=question, categories=categories)

@app.route('/questions/delete/<int:id>', methods=['POST'])
def delete_question(id):
    """حذف سؤال"""
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    flash('تم حذف السؤال بنجاح!', 'success')
    return redirect(url_for('questions'))

@app.route('/categories/add', methods=['POST'])
def add_category():
    """إضافة تصنيف جديد"""
    new_category = request.form.get('new_category')
    
    # التحقق من أن التصنيف غير موجود بالفعل
    categories = db.session.query(Question.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    if new_category in categories:
        flash('هذا التصنيف موجود بالفعل!', 'warning')
    else:
        # إضافة سؤال وهمي باستخدام التصنيف الجديد
        dummy_question = Question(
            text=f"سؤال تجريبي لتصنيف {new_category}",
            answer="إجابة تجريبية",
            category=new_category,
            question_type="normal",
            difficulty=1
        )
        db.session.add(dummy_question)
        db.session.commit()
        
        flash(f'تمت إضافة التصنيف {new_category} بنجاح!', 'success')
    
    return redirect(url_for('questions'))

@app.route('/manage-questions', methods=['GET', 'POST'])
def manage_questions():
    """Management page for questions"""
    if request.method == 'POST':
        # Handle adding a new question
        if 'add_question' in request.form:
            text = request.form.get('question_text')
            answer = request.form.get('answer')
            category = request.form.get('category', 'عام')
            question_type = request.form.get('question_type', 'normal')
            difficulty = int(request.form.get('difficulty', 1))
            
            question = Question(
                text=text,
                answer=answer,
                category=category,
                question_type=question_type,
                difficulty=difficulty
            )
            
            db.session.add(question)
            db.session.commit()
            flash('تمت إضافة السؤال بنجاح!', 'success')
            
        # Handle updating a question
        elif 'update_question' in request.form:
            question_id = request.form.get('question_id')
            question = Question.query.get(question_id)
            if question:
                question.text = request.form.get('question_text')
                question.answer = request.form.get('answer')
                question.category = request.form.get('category')
                question.question_type = request.form.get('question_type')
                question.difficulty = int(request.form.get('difficulty', 1))
                db.session.commit()
                flash('تم تحديث السؤال بنجاح!', 'success')
            else:
                flash('لم يتم العثور على السؤال!', 'danger')
                
        # Handle deleting a question
        elif 'delete_question' in request.form:
            question_id = request.form.get('question_id')
            question = Question.query.get(question_id)
            if question:
                db.session.delete(question)
                db.session.commit()
                flash('تم حذف السؤال بنجاح!', 'success')
            else:
                flash('لم يتم العثور على السؤال!', 'danger')
                
        # Handle deleting all questions
        elif 'delete_all_questions' in request.form:
            questions = Question.query.all()
            for question in questions:
                db.session.delete(question)
            db.session.commit()
            flash('تم حذف جميع الأسئلة بنجاح!', 'success')
            
        # Handle importing default questions
        elif 'import_default' in request.form:
            from scripts.import_questions import import_default_questions
            import_default_questions()
            flash('تم استيراد الأسئلة الافتراضية بنجاح!', 'success')
            
        # Handle updating funny responses
        elif 'update_funny_responses' in request.form:
            funny_responses_text = request.form.get('funny_responses', '')
            responses = [r.strip() for r in funny_responses_text.split('\n') if r.strip()]
            config.funny_responses = responses
            config.save()
            
            # Also update in database
            FunnyResponse.query.delete()
            for response in responses:
                db.session.add(FunnyResponse(text=response, min_score=0, max_score=50))
            db.session.commit()
            
            flash('تم تحديث ردود الطقطقة بنجاح!', 'success')
            
        return redirect(url_for('manage_questions'))
    
    # Fetch all questions for display
    questions = Question.query.all()
    return render_template('manage_questions.html', questions=questions, config=config)

@app.route('/export-questions')
def export_questions():
    """Export questions as JSON"""
    questions = Question.query.all()
    data = []
    for q in questions:
        data.append({
            'id': q.id,
            'text': q.text,
            'answer': q.answer,
            'category': q.category,
            'question_type': q.question_type,
            'difficulty': q.difficulty
        })
    
    response = jsonify(data)
    response.headers['Content-Disposition'] = 'attachment; filename=questions.json'
    return response

@app.route('/api/status')
def bot_status():
    """API endpoint to check bot status"""
    question_count = Question.query.count()
    return jsonify({
        'status': 'online',
        'active_channels': config.active_channels,
        'num_questions': question_count
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
