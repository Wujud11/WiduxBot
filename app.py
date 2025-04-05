import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import threading
from config import DATABASE_URL

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create SQLAlchemy base
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "widuxbot-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with app
db.init_app(app)

# Bot instances for active channels
bot_instances = {}

with app.app_context():
    # Import models to ensure they're included for table creation
    from models import Channel, Question, GameSession
    
    # Create all tables
    db.create_all()

    # Add default questions if none exist
    from models import Question, FunnyResponse, PraiseResponse, EliminationMessage
    if Question.query.count() == 0:
        def add_user_questions():
            # العديد من الأسئلة المتنوعة
            questions = [
                {"text": "15+7=", "answers": "22", "category": "رياضيات", "difficulty": 1},
                {"text": "كم عدد الكروموسومات في جسم الانسان ؟", "answers": "46", "category": "علوم", "difficulty": 2},
                {"text": "من إمام العلماء يوم القيامة؟", "answers": "معاذ بن جبل رضي الله عنه", "category": "ديني", "difficulty": 2},
                {"text": "عنصر كيميائي رمزه Hg ؟", "answers": "الزئبق", "category": "علوم", "difficulty": 2},
                {"text": "ماهي عاصمة فرنسا ؟", "answers": "باريس", "category": "جغرافيا", "difficulty": 1},
                {"text": "متى بدأت الحرب العالمية الثانية ؟", "answers": "1939", "category": "تاريخ", "difficulty": 2},
                {"text": "ما هي الدولة التي تُعرف بأرض الشمس المشرقة؟", "answers": "اليابان", "category": "ثقافة عامة", "difficulty": 1},
                {"text": "ما هو اسم الجزء الملون من العين؟", "answers": "القزحية", "category": "علوم", "difficulty": 1},
                {"text": "ما هو المصطلح الطبي المستخدم لوصف توقف القلب عن النبض؟", "answers": "السكتة القلبية", "category": "طب", "difficulty": 2},
                {"text": "ما هو اسم الجزء الخارجي الصلب من الأسنان؟", "answers": "المينا", "category": "طب", "difficulty": 2},
                {"text": "ماهي وحدة قياس الصوت؟", "answers": "الديسيبل", "category": "فيزياء", "difficulty": 2},
                {"text": "ماهو صوت الماء؟", "answers": "الخرير", "category": "ثقافة عامة", "difficulty": 1},
                {"text": "ما هي المدة التي تستغرقها الأرض للدوران حول نفسها؟", "answers": "24 ساعة", "category": "علوم", "difficulty": 1},
                {"text": "ماهي عملة سويسرا؟", "answers": "الفرنك", "category": "ثقافة عامة", "difficulty": 1},
                {"text": "ما هو اللون الذي يمتص معظم الأطوال الموجية للضوء ؟", "answers": "اسود", "category": "فيزياء", "difficulty": 2},
                {"text": "من هو مؤسس شركة تسلا ؟", "answers": "ايلون ماسك", "category": "تكنولوجيا", "difficulty": 1},
                {"text": "ماهو أسرع طائر في العالم ؟", "answers": "الشاهين", "category": "حيوانات", "difficulty": 2},
                {"text": "من هو العالم الذي صاغ قانون الجاذبية ؟", "answers": "نيوتن", "category": "علوم", "difficulty": 1},
                {"text": "ماهو العنصر الكيميائي الذي يُعتبر الأساس في تكوين الألماس ؟", "answers": "الكربون", "category": "كيمياء", "difficulty": 2},
                {"text": "من هو اللاعب الذي سجل أكبر عدد من الأهداف في تاريخ كأس العالم ؟", "answers": "ميروسلاف كلوزه", "category": "رياضة", "difficulty": 2}
            ]
            
            # أسئلة كرة القدم
            football_questions = [
                {"text": "من هو الفريق الفائز بكأس العالم 2022؟", "answers": "الأرجنتين,منتخب الأرجنتين", "category": "كرة القدم", "difficulty": 1},
                {"text": "من هو هداف دوري أبطال أوروبا التاريخي؟", "answers": "كريستيانو رونالدو,رونالدو", "category": "كرة القدم", "difficulty": 1},
                {"text": "كم عدد مرات فوز البرازيل بكأس العالم؟", "answers": "5,خمس,خمسة", "category": "كرة القدم", "difficulty": 1},
                {"text": "من هو اللاعب الفائز بأكبر عدد من الكرات الذهبية في التاريخ؟", "answers": "ميسي,ليونيل ميسي", "category": "كرة القدم", "difficulty": 1},
                {"text": "من هو مدرب ريال مدريد الحالي (2023)؟", "answers": "كارلو أنشيلوتي,انشيلوتي", "category": "كرة القدم", "difficulty": 1},
                {"text": "ما هو النادي الذي فاز بأكبر عدد من بطولات دوري أبطال أوروبا؟", "answers": "ريال مدريد", "category": "كرة القدم", "difficulty": 1},
                {"text": "من هو الحارس الفائز بجائزة ياشين عام 2023؟", "answers": "دييغو مارتينيز,ديبو مارتينيز", "category": "كرة القدم", "difficulty": 2},
                {"text": "من هو اللاعب الوحيد الذي فاز بكأس العالم ثلاث مرات كلاعب؟", "answers": "بيليه", "category": "كرة القدم", "difficulty": 2},
                {"text": "متى كان أول كأس عالم في تاريخ كرة القدم؟", "answers": "1930", "category": "كرة القدم", "difficulty": 2},
                {"text": "أي نادٍ فاز بالثلاثية التاريخية (الدوري، الكأس، دوري الأبطال) مرتين؟", "answers": "برشلونة", "category": "كرة القدم", "difficulty": 2},
                {"text": "من هو الهداف التاريخي للمنتخب السعودي؟", "answers": "سامي الجابر", "category": "كرة القدم", "difficulty": 2},
                {"text": "من هو أول لاعب عربي يفوز بدوري أبطال أوروبا؟", "answers": "أشرف حكيمي", "category": "كرة القدم", "difficulty": 3},
                {"text": "ما هو النادي الذي لعب له زين الدين زيدان قبل انتقاله لريال مدريد؟", "answers": "يوفنتوس", "category": "كرة القدم", "difficulty": 2},
                {"text": "من هو مسجل أسرع هدف في تاريخ كأس العالم؟", "answers": "هاكان شوكور", "category": "كرة القدم", "difficulty": 3},
                {"text": "من هو اللاعب الوحيد الذي فاز بالكرة الذهبية خلال لعبه في الدوري الإيطالي منذ عام 2000؟", "answers": "كاكا", "category": "كرة القدم", "difficulty": 3},
                {"text": "من هو الفريق الذي فاز بلقب الدوري الإنجليزي الممتاز لأول مرة في 2016؟", "answers": "ليستر سيتي", "category": "كرة القدم", "difficulty": 2},
                {"text": "ما هو النادي الذي فاز بأول نسخة من دوري أبطال أوروبا بشكله الحديث؟", "answers": "مارسيليا", "category": "كرة القدم", "difficulty": 3},
                {"text": "من هو أكثر لاعب حقق ألقاب في تاريخ كرة القدم؟", "answers": "داني ألفيس", "category": "كرة القدم", "difficulty": 2},
                {"text": "ما هو أكبر فوز في تاريخ كأس العالم؟", "answers": "31-0,استراليا ساموا الأمريكية 31-0", "category": "كرة القدم", "difficulty": 3},
                {"text": "من هو الفريق الفائز بأول كأس عالم للأندية؟", "answers": "كورينثيانز", "category": "كرة القدم", "difficulty": 3}
            ]
            
            # إضافة أسئلة كرة القدم إلى قائمة الأسئلة العامة
            questions.extend(football_questions)
            
            # إضافة الأسئلة إلى قاعدة البيانات
            for q in questions:
                question = Question(
                    text=q["text"],
                    answers=q["answers"],
                    category=q["category"],
                    difficulty=q["difficulty"],
                    question_type="normal"
                )
                db.session.add(question)
            
            # Golden Question - سؤال الذهب
            gold_questions = [
                {"text": "ما هو اسم أعمق نقطة في المحيط؟", "answers": "خندق ماريانا", "category": "جغرافيا", "difficulty": 3},
                {"text": "ما هو أكبر عضو في جسم الإنسان؟", "answers": "الجلد", "category": "طب", "difficulty": 2},
                {"text": "ما هي أطول كلمة في اللغة العربية؟", "answers": "أفاستسقيناكموها", "category": "لغة", "difficulty": 3}
            ]
            
            for q in gold_questions:
                question = Question(
                    text=q["text"],
                    answers=q["answers"],
                    category=q["category"],
                    difficulty=q["difficulty"],
                    question_type="golden"
                )
                db.session.add(question)
            
            # Steal Question - سؤال الزرف
            steal_questions = [
                {"text": "كم عدد قلوب الأخطبوط؟", "answers": "3", "category": "علوم", "difficulty": 3},
                {"text": "ما اسم أكبر صحراء جليدية في العالم؟", "answers": "انتاركتيكا", "category": "جغرافيا", "difficulty": 3},
                {"text": "ما هو أكثر عنصر وفرة في القشرة الأرضية؟", "answers": "الأكسجين", "category": "كيمياء", "difficulty": 3}
            ]
            
            for q in steal_questions:
                question = Question(
                    text=q["text"],
                    answers=q["answers"],
                    category=q["category"],
                    difficulty=q["difficulty"],
                    question_type="steal"
                )
                db.session.add(question)
            
            db.session.commit()
            return "تمت إضافة جميع الأسئلة بنجاح!"
        
        # إضافة ردود الطقطقة
        def add_funny_responses():
            responses = [
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
                "ماودي اجرحك بس انت غبي وهطف",
                "ماشاءالله وعدم الذكاء اللي عندك",
                "المرة الجاية بغششك لأن الغباء هذا كارثة",
                "أقل من 50؟ صدقني لو لاعب حقرة بقرة ازين لك"
            ]
            
            for response in responses:
                funny_resp = FunnyResponse(
                    text=response,
                    min_score=0,
                    max_score=50,
                    is_team_response=False
                )
                db.session.add(funny_resp)
            
            # ردود طقطقة للفرق
            team_responses = [
                "فريق الخسرانين، مبروك! انضميتوا لنادي الفاشلين",
                "فريق مين ذا؟ ههههههه وش هالمستوى",
                "طبعا كان متوقع هالنتيجة، ليدر اهبل وفريق أهبل",
                "أقل من 50 بالتيم؟ حسبي الله ونعم الوكيل على هالغباء الجماعي",
                "لو دخلتوا مدرسة متعلمتوش شي",
                "فريق مسوي نفسه شطور، طلع ما يفهم شي",
                "وقت فراغ... مو لعب"
            ]
            
            for response in team_responses:
                team_resp = FunnyResponse(
                    text=response,
                    min_score=0,
                    max_score=50,
                    is_team_response=True
                )
                db.session.add(team_resp)
            
            db.session.commit()
            return "تمت إضافة جميع ردود الطقطقة بنجاح!"
        
        # إضافة ردود المدح والثناء للفائزين
        def add_praise_responses():
            # ردود مدح للأفراد (للأوضاع: solo, group)
            individual_responses = [
                # ردود عامة لجميع المستويات
                {"text": "أسطوووورة! 🔥 مستوى عالي من الذكاء والسرعة!", "min_score": 80, "game_mode": "all"},
                {"text": "ما شاء الله عليك! 👏 عقل راجح وإجابات دقيقة", "min_score": 80, "game_mode": "all"},
                {"text": "أنت مو بس لاعب، أنت معلم! 👑 مبروك النقاط العالية", "min_score": 90, "game_mode": "all"},
                {"text": "العب معنا كل يوم! 🌟 أفضل لاعب شفناه هالأسبوع", "min_score": 100, "game_mode": "all"},
                {"text": "عبقري! 🧠 حرفياً أذكى من ٩٥٪؜ من المشاركين", "min_score": 100, "game_mode": "all"},
                {"text": "فوز ساحق! 🏆 مستواك لا يعلى عليه", "min_score": 120, "game_mode": "all"},
                {"text": "أنت شخص موسوعي! 📚 معلوماتك رهيبة", "min_score": 120, "game_mode": "all"},
                {"text": "نحتاج عقول مثلك في بلادنا! 🌍 استمر في التفوق", "min_score": 150, "game_mode": "all"},
                
                # ردود خاصة لوضع اتحداك (solo)
                {"text": "انتصرت على البوت! 🤖 هذا إنجاز حقيقي", "min_score": 80, "game_mode": "solo"},
                {"text": "تحديت البوت وانتصرت! 💪 أنت أسطورة", "min_score": 100, "game_mode": "solo"},
                {"text": "أثبت أن الذكاء البشري لا يزال متفوقاً! 🥇", "min_score": 120, "game_mode": "solo"},
                
                # ردود خاصة لوضع التحدي (group)
                {"text": "ملك الإجابات السريعة! ⚡ تفوقت على الجميع", "min_score": 80, "game_mode": "group"},
                {"text": "نجم القروب! 🌟 أثبت جدارتك على المنافسين", "min_score": 100, "game_mode": "group"},
                {"text": "تستاهل الفوز! 🎯 ردودك كانت أسرع وأدق من الجميع", "min_score": 120, "game_mode": "group"}
            ]
            
            for response in individual_responses:
                praise_resp = PraiseResponse(
                    text=response["text"],
                    min_score=response["min_score"],
                    game_mode=response["game_mode"],
                    is_team_response=False
                )
                db.session.add(praise_resp)
            
            # ردود مدح للفرق (لوضع التيم)
            team_responses = [
                {"text": "فريق الأبطال! 🏆 تعاون مثالي وإجابات ذكية", "min_score": 80},
                {"text": "فريق مرعب! 👊 قوة جماعية لا تُقهر", "min_score": 100},
                {"text": "أفضل فريق شفناه! 🌟 تنسيق عالي المستوى", "min_score": 120},
                {"text": "قوة عقول جماعية! 🧠 الفريق المثالي", "min_score": 120},
                {"text": "أسطورة الفرق! 🔥 تستحقون بطولة خاصة", "min_score": 150},
                {"text": "فريق يدخل التاريخ! 📜 أداء لا يُنسى", "min_score": 170},
                {"text": "مجموعة عباقرة! 💯 مستوى لا يصدق", "min_score": 200}
            ]
            
            for response in team_responses:
                team_praise = PraiseResponse(
                    text=response["text"],
                    min_score=response["min_score"],
                    game_mode="team",
                    is_team_response=True
                )
                db.session.add(team_praise)
            
            db.session.commit()
            return "تمت إضافة ردود المدح بنجاح!"
            
        # إضافة رسائل الاستبعاد من اللعبة
        def add_elimination_messages():
            messages = [
                "اوووووت",
                "برررا",
                "تفرج بس",
                "محد قالك ماتجاوب",
                "الفكررر ياانسان",
                "يلا خيره",
                "تستاهل",
                "الققممم",
                "عسسل على قلبي",
                "شلوووتي",
                "لاتكثر كلام",
                "تفنش واااء",
                "انتهى وقتك",
                "الله يعين",
                "مع السلامة",
                "اللعب احلى بدونك",
                "فشلنا في إنقاذك",
                "هههههههه",
                "اقضب الباب",
                "كاااك",
                "يفهههم اللي طلعك"
            ]
            
            for message in messages:
                elim_msg = EliminationMessage(
                    text=message
                )
                db.session.add(elim_msg)
                
            db.session.commit()
            return "تمت إضافة رسائل الاستبعاد بنجاح!"
        
        # تنفيذ الدوال لإضافة جميع البيانات
        add_user_questions()
        add_funny_responses()
        add_praise_responses()
        add_elimination_messages()
        
        print("Added questions, funny responses, praise messages, and elimination messages to the database!")

# Import bot after models are defined
from bot import create_bot_instance

@app.route('/')
def index():
    channels = Channel.query.all()
    from datetime import datetime
    return render_template('index.html', channels=channels, now=datetime.now())

@app.route('/questions')
def questions():
    from datetime import datetime
    questions = Question.query.all()
    return render_template('questions.html', questions=questions, now=datetime.now())

@app.route('/questions/add', methods=['POST'])
def add_question():
    text = request.form.get('text', '').strip()
    answers = request.form.get('answers', '').strip()
    category = request.form.get('category', 'general').strip()
    difficulty = request.form.get('difficulty', '2').strip()
    question_type = request.form.get('question_type', 'normal').strip()
    
    if not text or not answers:
        flash('يرجى ملء جميع الحقول المطلوبة', 'danger')
        return redirect(url_for('questions'))
    
    try:
        difficulty = int(difficulty)
    except ValueError:
        difficulty = 2  # Default medium difficulty
    
    new_question = Question(
        text=text,
        answers=answers,
        category=category,
        difficulty=difficulty,
        question_type=question_type
    )
    
    try:
        db.session.add(new_question)
        db.session.commit()
        flash('تم إضافة السؤال بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding question: {e}")
        flash(f'حدث خطأ أثناء إضافة السؤال: {str(e)}', 'danger')
    
    return redirect(url_for('questions'))

@app.route('/questions/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    try:
        db.session.delete(question)
        db.session.commit()
        flash('تم حذف السؤال بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting question: {e}")
        flash(f'حدث خطأ أثناء حذف السؤال: {str(e)}', 'danger')
    
    return redirect(url_for('questions'))

@app.route('/questions/import', methods=['POST'])
def import_questions():
    questions_text = request.form.get('questions_text', '').strip()
    
    if not questions_text:
        flash('يرجى إدخال الأسئلة للاستيراد', 'danger')
        return redirect(url_for('questions'))
    
    # Process questions
    lines = questions_text.split('\n')
    questions_added = 0
    
    for line in lines:
        line = line.strip()
        if not line or '|' not in line:
            continue
        
        parts = line.split('|', 1)
        if len(parts) != 2:
            continue
        
        text = parts[0].strip()
        answers = parts[1].strip()
        
        if not text or not answers:
            continue
        
        try:
            difficulty_val = int(2)  # Default medium difficulty
        except ValueError:
            difficulty_val = 2
            
        new_question = Question(
            text=text,
            answers=answers,
            category='general',
            difficulty=difficulty_val,
            question_type='normal'
        )
        
        try:
            db.session.add(new_question)
            questions_added += 1
        except Exception as e:
            logger.error(f"Error importing question: {e}")
    
    if questions_added > 0:
        try:
            db.session.commit()
            flash(f'تم استيراد {questions_added} سؤال بنجاح', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error committing imported questions: {e}")
            flash(f'حدث خطأ أثناء حفظ الأسئلة المستوردة: {str(e)}', 'danger')
    else:
        flash('لم يتم استيراد أي أسئلة. تأكد من تنسيق البيانات المدخلة', 'warning')
    
    return redirect(url_for('questions'))

@app.route('/register', methods=['POST'])
def register_channel():
    channel_name = request.form.get('channel_name', '').strip().lower()
    
    if not channel_name:
        flash('يرجى إدخال اسم القناة', 'danger')
        return redirect(url_for('index'))
    
    # Check if channel already exists
    existing_channel = Channel.query.filter_by(name=channel_name).first()
    if existing_channel:
        flash(f'القناة {channel_name} مفعلة بالفعل', 'warning')
        return redirect(url_for('index'))
    
    # Create new channel
    new_channel = Channel(name=channel_name, is_active=True)
    db.session.add(new_channel)
    
    try:
        db.session.commit()
        
        # Start bot for this channel
        try:
            start_bot_for_channel(channel_name)
            flash(f'تم تفعيل البوت في قناة {channel_name} بنجاح', 'success')
        except Exception as e:
            logger.error(f"Error starting bot for channel {channel_name}: {e}")
            flash(f'تم إضافة القناة ولكن حدث خطأ في تشغيل البوت: {str(e)}', 'warning')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error: {e}")
        flash(f'حدث خطأ أثناء تسجيل القناة: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/toggle/<int:channel_id>', methods=['POST'])
def toggle_channel(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    channel.is_active = not channel.is_active
    
    try:
        db.session.commit()
        
        if channel.is_active:
            # Start bot for this channel
            start_bot_for_channel(channel.name)
            flash(f'تم تفعيل البوت في قناة {channel.name}', 'success')
        else:
            # Stop bot for this channel
            stop_bot_for_channel(channel.name)
            flash(f'تم إيقاف البوت في قناة {channel.name}', 'info')
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling channel status: {e}")
        flash(f'حدث خطأ أثناء تغيير حالة القناة: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/delete/<int:channel_id>', methods=['POST'])
def delete_channel(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    channel_name = channel.name
    
    try:
        # Stop bot if it's running
        if channel.is_active:
            stop_bot_for_channel(channel_name)
        
        # Delete channel from database
        db.session.delete(channel)
        db.session.commit()
        
        flash(f'تم حذف القناة {channel_name} بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting channel: {e}")
        flash(f'حدث خطأ أثناء حذف القناة: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

def start_bot_for_channel(channel_name):
    """Start a Twitch bot instance for the specified channel"""
    if channel_name in bot_instances and bot_instances[channel_name].is_running:
        logger.info(f"Bot already running for channel {channel_name}")
        return
    
    logger.info(f"Starting bot for channel {channel_name}")
    bot = create_bot_instance([channel_name])
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=bot.run)
    bot_thread.daemon = True
    bot_thread.start()
    
    bot_instances[channel_name] = bot
    logger.info(f"Bot started for channel {channel_name}")

def stop_bot_for_channel(channel_name):
    """Stop a running Twitch bot instance for the specified channel"""
    if channel_name not in bot_instances:
        logger.info(f"No bot instance found for channel {channel_name}")
        return
    
    logger.info(f"Stopping bot for channel {channel_name}")
    
    try:
        bot_instances[channel_name].close()
        del bot_instances[channel_name]
        logger.info(f"Bot stopped for channel {channel_name}")
    except Exception as e:
        logger.error(f"Error stopping bot for channel {channel_name}: {e}")
        raise

# Initialize bots for all active channels on application startup
def init_bots():
    with app.app_context():
        active_channels = Channel.query.filter_by(is_active=True).all()
        for channel in active_channels:
            try:
                start_bot_for_channel(channel.name)
            except Exception as e:
                logger.error(f"Failed to start bot for channel {channel.name}: {e}")

# In Flask 2.0+, before_first_request is deprecated
# Instead, we'll call init_bots after the app context is created
@app.before_request
def before_request_func():
    if not hasattr(app, '_got_first_request'):
        app._got_first_request = True
        init_bots()
