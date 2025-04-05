import os
import sys
import logging
from datetime import datetime

# Add the parent directory to the path so we can import app and models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Question, FunnyResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_question(text, answer, category="عام", question_type="normal", difficulty=1):
    """Add a question to the database"""
    try:
        # Check if question already exists
        existing = Question.query.filter_by(text=text).first()
        if existing:
            logger.info(f"Question already exists: {text}")
            return False
        
        # Create new question
        question = Question(
            text=text,
            answer=answer,
            category=category,
            question_type=question_type,
            difficulty=difficulty,
            created_at=datetime.utcnow()
        )
        
        # Add to database
        db.session.add(question)
        db.session.commit()
        logger.info(f"Added question: {text}")
        return True
    except Exception as e:
        logger.error(f"Error adding question: {e}")
        db.session.rollback()
        return False

def add_funny_response(text, min_score=0, max_score=50, is_team_response=False):
    """Add a funny response to the database"""
    try:
        # Check if response already exists
        existing = FunnyResponse.query.filter_by(text=text).first()
        if existing:
            logger.info(f"Funny response already exists: {text}")
            return False
        
        # Create new response
        response = FunnyResponse(
            text=text,
            min_score=min_score,
            max_score=max_score,
            is_team_response=is_team_response,
            created_at=datetime.utcnow()
        )
        
        # Add to database
        db.session.add(response)
        db.session.commit()
        logger.info(f"Added funny response: {text}")
        return True
    except Exception as e:
        logger.error(f"Error adding funny response: {e}")
        db.session.rollback()
        return False

def import_default_questions():
    """Import default questions to the database"""
    with app.app_context():
        # 60 أسئلة من المستخدم
        questions = [
            {"text": "15+7=", "answer": "22", "category": "رياضيات", "difficulty": 1},
            {"text": "كم عدد الكروموسومات في جسم الانسان ؟", "answer": "46", "category": "علوم", "difficulty": 2},
            {"text": "من إمام العلماء يوم القيامة؟", "answer": "معاذ بن جبل رضي الله عنه", "category": "دين", "difficulty": 2},
            {"text": "عنصر كيميائي رمزه Hg ؟", "answer": "الزئبق", "category": "علوم", "difficulty": 2},
            {"text": "ماهي عاصمة فرنسا ؟", "answer": "باريس", "category": "جغرافيا", "difficulty": 1},
            {"text": "متى بدأت الحرب العالمية الثانية ؟", "answer": "1939", "category": "تاريخ", "difficulty": 1},
            {"text": "ما هي الدولة التي تُعرف بأرض الشمس المشرقة؟", "answer": "اليابان", "category": "جغرافيا", "difficulty": 1},
            {"text": "ما هو اسم الجزء الملون من العين؟", "answer": "القزحية", "category": "طب", "difficulty": 2},
            {"text": "ما هو المصطلح الطبي المستخدم لوصف توقف القلب عن النبض؟", "answer": "السكتة القلبية", "category": "طب", "difficulty": 2},
            {"text": "ما هو اسم الجزء الخارجي الصلب من الأسنان؟", "answer": "المينا", "category": "طب", "difficulty": 2},
            {"text": "ماهي وحدة قياس الصوت؟", "answer": "الديسيبل", "category": "علوم", "difficulty": 2},
            {"text": "ماهو صوت الماء؟", "answer": "الخرير", "category": "عام", "difficulty": 1},
            {"text": "ما هي المدة التي تستغرقها الأرض للدوران حول نفسها؟", "answer": "24 ساعة", "category": "علوم", "difficulty": 1},
            {"text": "ماهي عملة سويسرا؟", "answer": "الفرنك", "category": "اقتصاد", "difficulty": 1},
            {"text": "ما هو اللون الذي يمتص معظم الأطوال الموجية للضوء ؟", "answer": "الأسود", "category": "علوم", "difficulty": 1},
            {"text": "من هو مؤسس شركة تسلا ؟", "answer": "ايلون ماسك", "category": "تكنولوجيا", "difficulty": 1},
            {"text": "ماهو أسرع طائر في العالم ؟", "answer": "الشاهين", "category": "حيوانات", "difficulty": 2},
            {"text": "من هو العالم الذي صاغ قانون الجاذبية ؟", "answer": "نيوتن", "category": "علوم", "difficulty": 1},
            {"text": "ماهو العنصر الكيميائي الذي يُعتبر الأساس في تكوين الألماس ؟", "answer": "الكربون", "category": "علوم", "difficulty": 2},
            {"text": "من هو اللاعب الذي سجل أكبر عدد من الأهداف في تاريخ كأس العالم ؟", "answer": "كريستيانو رونالدو", "category": "رياضة", "difficulty": 1},
            {"text": "أي فريق فاز بأكبر عدد من بطولات دوري أبطال أوروبا (Champions League) في تاريخ المسابقة؟", "answer": "ريال مدريد", "category": "رياضة", "difficulty": 1},
            {"text": "في أي سنة أُقيمت أول دورة ألعاب أولمبية حديثة؟", "answer": "1896", "category": "رياضة", "difficulty": 2},
            {"text": "من هو مؤلف رواية \"مئة عام من العزلة\" ؟", "answer": "غابرييل غارسيا ماركيز", "category": "أدب", "difficulty": 2},
            {"text": "أي المحيطات هو الأكبر في العالم؟", "answer": "المحيط الهادئ", "category": "جغرافيا", "difficulty": 1},
            {"text": "من هو أول رئيس للولايات المتحدة الأمريكية؟", "answer": "جورج واشنطن", "category": "سياسة", "difficulty": 1},
            {"text": "ما هو أطول نهر في العالم؟", "answer": "النيل", "category": "جغرافيا", "difficulty": 1},
            {"text": "ما هو الكوكب الذي يُعرف بـ \"الكوكب الأحمر\" ؟", "answer": "المريخ", "category": "علوم", "difficulty": 1},
            {"text": "من هو مؤسس شركة مايكروسوفت ؟", "answer": "بيل غيتس", "category": "تكنولوجيا", "difficulty": 1},
            {"text": "في أي سنة تولى الأمير محمد بن سلمان ولاية العهد في السعودية؟", "answer": "2017", "category": "سياسة", "difficulty": 1},
            {"text": "في أي سنة تأسست المملكة العربية السعودية ؟", "answer": "1932", "category": "تاريخ", "difficulty": 1},
            {"text": "ما هي عاصمة اليابان؟", "answer": "طوكيو", "category": "جغرافيا", "difficulty": 1},
            {"text": "ما هي أكبر دولة في العالم من حيث المساحة؟", "answer": "روسيا", "category": "جغرافيا", "difficulty": 1},
            {"text": "في أي قارة تقع دولة مصر ؟", "answer": "افريقيا", "category": "جغرافيا", "difficulty": 1},
            {"text": "ماهي عاصمة كندا ؟", "answer": "أوتاوا", "category": "جغرافيا", "difficulty": 1},
            {"text": "ماهي الدولة التي تقع في كلا القارتين الأوروبية والآسيوية؟", "answer": "تركيا", "category": "جغرافيا", "difficulty": 1},
            {"text": "ما هي أصغر دولة في العالم من حيث المساحة ؟", "answer": "الفاتيكان", "category": "جغرافيا", "difficulty": 1},
            {"text": "ما هي عاصمة البرازيل؟", "answer": "برازيليا", "category": "جغرافيا", "difficulty": 1},
            {"text": "من هو الهداف التاريخي لمنتخب البرازيل في كرة القدم ؟", "answer": "نيمار", "category": "رياضة", "difficulty": 2},
            {"text": "في أي عام فاز المنتخب الألماني ببطولة كأس العالم لأول مرة؟", "answer": "1954", "category": "رياضة", "difficulty": 2},
            {"text": "من هو اللاعب الذي فاز بجائزة الكرة الذهبية أكثر من أي لاعب آخر في تاريخ كرة القدم؟", "answer": "ميسي", "category": "رياضة", "difficulty": 1},
            {"text": "من هو مدرب منتخب فرنسا الذي قاد الفريق للفوز بكأس العالم 1998؟", "answer": "ديدييه ديشامب", "category": "رياضة", "difficulty": 2},
            {"text": "أي نادي فاز بدوري أبطال أوروبا موسم 2020-2021 ؟", "answer": "تشيلسي", "category": "رياضة", "difficulty": 1},
            {"text": "ما هو أكبر فوز في تاريخ كأس العالم في مباراة واحدة ؟", "answer": "10", "category": "رياضة", "difficulty": 2},
            {"text": "من هو اللاعب الذي سجل أول هدف في تاريخ كأس العالم؟", "answer": "هيرمان كادينسكي", "category": "رياضة", "difficulty": 3},
            {"text": "في أي سنة فاز نادي الهلال السعودي بأول بطولة دوري أبطال آسيا ؟", "answer": "1991", "category": "رياضة", "difficulty": 2},
            {"text": "من هو الملقب بالجوهرة السوداء في كرة القدم ؟", "answer": "بيليه", "category": "رياضة", "difficulty": 1},
            {"text": "ما هو أطول نهر في قارة آسيا ؟", "answer": "اليانغتسي", "category": "جغرافيا", "difficulty": 2},
            {"text": "ماهي عاصمة المغرب ؟", "answer": "الرباط", "category": "جغرافيا", "difficulty": 1},
            {"text": "كم كان عمر رسول الله -صلّى الله عليه وسلّم- عندما بعثه الله -تعالى- بالرسالة؟", "answer": "اربعين", "category": "دين", "difficulty": 1},
            {"text": "ما الشجرة الملعونة التى ذكرت فى القرآن الكريم ؟", "answer": "الزقوم", "category": "دين", "difficulty": 2},
            {"text": "ما أول أمر نزل فى القرآن الكريم ؟", "answer": "اقرأ", "category": "دين", "difficulty": 1},
            {"text": "ما هي عاصمة الإمارات العربية المتحدة؟", "answer": "ابو ظبي", "category": "جغرافيا", "difficulty": 1},
            {"text": "هو أكبر بحر في العالم من حيث المساحة؟", "answer": "قزوين", "category": "جغرافيا", "difficulty": 2},
            {"text": "ما هي الدولة العربية التي تشتهر بأنها \"أرض الأرز؟", "answer": "لبنان", "category": "جغرافيا", "difficulty": 1},
            {"text": "في أي دولة عربية يقع جبل طارق ؟", "answer": "المغرب", "category": "جغرافيا", "difficulty": 2},
            {"text": "من هو حاكم قطر الحالي؟", "answer": "تميم بن حمد", "category": "سياسة", "difficulty": 1},
            {"text": "من هو مؤسس دولة الكويت ؟", "answer": "الشيخ صباح الاول", "category": "تاريخ", "difficulty": 2},
            {"text": "في أي عام سقطت دولة الاتحاد السوفيتي؟", "answer": "1991", "category": "تاريخ", "difficulty": 1},
            {"text": "من هو الزعيم الذي تم اغتياله في 1965 وكان زعيم حركة الحقوق المدنية في الولايات المتحدة ؟", "answer": "مالكوم اكس", "category": "تاريخ", "difficulty": 2},
            {"text": "ما هو الكتاب المقدس في الديانة المسيحية ؟", "answer": "الانجيل", "category": "دين", "difficulty": 1},
        ]
        
        # أسئلة إضافية متنوعة في مختلف المجالات
        additional_questions = [
            # أسئلة دينية
            {"text": "من هم الخلفاء الراشدون الأربعة؟", "answer": "أبو بكر وعمر وعثمان وعلي", "category": "دين", "difficulty": 1},
            {"text": "ما هو أول مسجد بني في الإسلام؟", "answer": "مسجد قباء", "category": "دين", "difficulty": 2},
            {"text": "من هو أول من أذن في الإسلام؟", "answer": "بلال بن رباح", "category": "دين", "difficulty": 1},
            {"text": "ما هي السورة الوحيدة في القرآن التي لا تبدأ بالبسملة؟", "answer": "التوبة", "category": "دين", "difficulty": 2},
            {"text": "كم عدد سور القرآن الكريم؟", "answer": "114", "category": "دين", "difficulty": 1},
            
            # أسئلة سياسية
            {"text": "من هو الرئيس الأمريكي الذي استقال بسبب فضيحة ووترغيت؟", "answer": "ريتشارد نيكسون", "category": "سياسة", "difficulty": 2},
            {"text": "ما هي الثورة التي أطاحت بنظام الشاه في إيران؟", "answer": "الثورة الإسلامية", "category": "سياسة", "difficulty": 2},
            {"text": "متى تأسست منظمة الأمم المتحدة؟", "answer": "1945", "category": "سياسة", "difficulty": 1},
            {"text": "ما هي عاصمة كوريا الشمالية؟", "answer": "بيونغ يانغ", "category": "سياسة", "difficulty": 1},
            {"text": "من هو رئيس الاتحاد السوفيتي خلال أزمة الصواريخ الكوبية؟", "answer": "خروتشوف", "category": "سياسة", "difficulty": 2},
            
            # أسئلة ثقافية
            {"text": "من هو مؤلف مسرحية هاملت؟", "answer": "وليام شكسبير", "category": "ثقافة", "difficulty": 1},
            {"text": "ما هو أشهر مؤلفات نجيب محفوظ؟", "answer": "الثلاثية", "category": "ثقافة", "difficulty": 2},
            {"text": "من هو رسام لوحة الموناليزا؟", "answer": "ليوناردو دافنشي", "category": "ثقافة", "difficulty": 1},
            {"text": "ما هو أشهر لحن للموسيقار المصري محمد عبد الوهاب؟", "answer": "أنت عمري", "category": "ثقافة", "difficulty": 2},
            {"text": "من أشهر الفنانين العرب الذي غنى 'دي الليلة رجيت'؟", "answer": "عبد الحليم حافظ", "category": "ثقافة", "difficulty": 1},
            
            # أسئلة تاريخية
            {"text": "متى فتح المسلمون مكة؟", "answer": "8 هجرية", "category": "تاريخ", "difficulty": 1},
            {"text": "متى سقطت الخلافة العثمانية؟", "answer": "1924", "category": "تاريخ", "difficulty": 2},
            {"text": "من هو فاتح الأندلس؟", "answer": "طارق بن زياد", "category": "تاريخ", "difficulty": 1},
            {"text": "متى بدأت الحرب العالمية الأولى؟", "answer": "1914", "category": "تاريخ", "difficulty": 1},
            {"text": "من هو مكتشف قارة أمريكا؟", "answer": "كريستوفر كولومبوس", "category": "تاريخ", "difficulty": 1},
            
            # أسئلة رياضية
            {"text": "من هو الفريق الذي حقق أكبر عدد من بطولات كأس العالم في كرة القدم؟", "answer": "البرازيل", "category": "رياضة", "difficulty": 1},
            {"text": "من هو اللاعب الذي يلقب بالاسطورة في التنس؟", "answer": "روجر فيدرر", "category": "رياضة", "difficulty": 1},
            {"text": "كم عدد لاعبي فريق كرة السلة داخل الملعب؟", "answer": "5", "category": "رياضة", "difficulty": 1},
            {"text": "من هو النادي الذي يلقب بالمرينغي؟", "answer": "ريال مدريد", "category": "رياضة", "difficulty": 1},
            {"text": "من هو النادي الذي حقق الثلاثية التاريخية مرتين في تاريخ كرة القدم الأوروبية؟", "answer": "برشلونة", "category": "رياضة", "difficulty": 2},
            
            # أسئلة حياتية
            {"text": "ما هو العنصر الذي يساعد في بناء العظام والأسنان؟", "answer": "الكالسيوم", "category": "حياتية", "difficulty": 1},
            {"text": "ما هو الفيتامين الذي ينتجه الجسم عند التعرض لأشعة الشمس؟", "answer": "فيتامين د", "category": "حياتية", "difficulty": 1},
            {"text": "كم عدد أنواع فصائل الدم البشرية الرئيسية؟", "answer": "4", "category": "حياتية", "difficulty": 1},
            {"text": "ما هو الغذاء الرئيسي في آسيا والذي يعتبر من أهم محاصيل العالم؟", "answer": "الأرز", "category": "حياتية", "difficulty": 1},
            {"text": "ما هو المعدن الأكثر وفرة في القشرة الأرضية؟", "answer": "الألمنيوم", "category": "حياتية", "difficulty": 2},
        ]
        
        # إضافة الأسئلة الأساسية
        count = 0
        for q in questions:
            if add_question(q["text"], q["answer"], q["category"], "normal", q["difficulty"]):
                count += 1
        logger.info(f"Added {count} basic questions.")
        
        # إضافة الأسئلة الإضافية
        count = 0
        for q in additional_questions:
            if add_question(q["text"], q["answer"], q["category"], "normal", q["difficulty"]):
                count += 1
        logger.info(f"Added {count} additional questions.")
        
        # إضافة ردود الطقطقة
        funny_responses = [
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
        
        # إضافة ردود الطقطقة إلى قاعدة البيانات
        count = 0
        for response in funny_responses:
            if add_funny_response(response):
                count += 1
        logger.info(f"Added {count} funny responses.")

if __name__ == "__main__":
    print("Starting import of default questions...")
    import_default_questions()
    print("Import completed!")