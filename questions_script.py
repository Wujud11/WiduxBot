from app import app, db
from models import Question, FunnyResponse, PraiseResponse
import random

# تهيئة الأسئلة من الملف الذي قدمه المستخدم
def add_user_questions():
    questions = [
        {"text": "15+7=", "answer": "22", "category": "رياضيات", "difficulty": 1},
        {"text": "كم عدد الكروموسومات في جسم الانسان ؟", "answer": "46", "category": "علوم", "difficulty": 2},
        {"text": "من إمام العلماء يوم القيامة؟", "answer": "معاذ بن جبل رضي الله عنه", "category": "ديني", "difficulty": 2},
        {"text": "عنصر كيميائي رمزه Hg ؟", "answer": "الزئبق", "category": "علوم", "difficulty": 2},
        {"text": "ماهي عاصمة فرنسا ؟", "answer": "باريس", "category": "جغرافيا", "difficulty": 1},
        {"text": "متى بدأت الحرب العالمية الثانية ؟", "answer": "1939", "category": "تاريخ", "difficulty": 2},
        {"text": "ما هي الدولة التي تُعرف بأرض الشمس المشرقة؟", "answer": "اليابان", "category": "ثقافة عامة", "difficulty": 1},
        {"text": "ما هو اسم الجزء الملون من العين؟", "answer": "القزحية", "category": "علوم", "difficulty": 1},
        {"text": "ما هو المصطلح الطبي المستخدم لوصف توقف القلب عن النبض؟", "answer": "السكتة القلبية", "category": "طب", "difficulty": 2},
        {"text": "ما هو اسم الجزء الخارجي الصلب من الأسنان؟", "answer": "المينا", "category": "طب", "difficulty": 2},
        {"text": "ماهي وحدة قياس الصوت؟", "answer": "الديسيبل", "category": "فيزياء", "difficulty": 2},
        {"text": "ماهو صوت الماء؟", "answer": "الخرير", "category": "ثقافة عامة", "difficulty": 1},
        {"text": "ما هي المدة التي تستغرقها الأرض للدوران حول نفسها؟", "answer": "24 ساعة", "category": "علوم", "difficulty": 1},
        {"text": "ماهي عملة سويسرا؟", "answer": "الفرنك", "category": "ثقافة عامة", "difficulty": 1},
        {"text": "ما هو اللون الذي يمتص معظم الأطوال الموجية للضوء ؟", "answer": "اسود", "category": "فيزياء", "difficulty": 2},
        {"text": "من هو مؤسس شركة تسلا ؟", "answer": "ايلون ماسك", "category": "تكنولوجيا", "difficulty": 1},
        {"text": "ماهو أسرع طائر في العالم ؟", "answer": "الشاهين", "category": "حيوانات", "difficulty": 2},
        {"text": "من هو العالم الذي صاغ قانون الجاذبية ؟", "answer": "نيوتن", "category": "علوم", "difficulty": 1},
        {"text": "ماهو العنصر الكيميائي الذي يُعتبر الأساس في تكوين الألماس ؟", "answer": "الكربون", "category": "كيمياء", "difficulty": 2},
        {"text": "من هو اللاعب الذي سجل أكبر عدد من الأهداف في تاريخ كأس العالم ؟", "answer": "كريستيانو رونالدو", "category": "رياضة", "difficulty": 1},
        {"text": "أي فريق فاز بأكبر عدد من بطولات دوري أبطال أوروبا (Champions League) في تاريخ المسابقة؟", "answer": "ريال مدريد", "category": "رياضة", "difficulty": 2},
        {"text": "في أي سنة أُقيمت أول دورة ألعاب أولمبية حديثة؟", "answer": "1896", "category": "رياضة", "difficulty": 3},
        {"text": "من هو مؤلف رواية 'مئة عام من العزلة' ؟", "answer": "غابرييل غارسيا ماركيز", "category": "أدب", "difficulty": 3},
        {"text": "ما هو أكبر محيط في العالم؟", "answer": "المحيط الهادئ", "category": "جغرافيا", "difficulty": 1},
        {"text": "من هو أول رئيس للولايات المتحدة الأمريكية؟", "answer": "جورج واشنطن", "category": "تاريخ", "difficulty": 1},
        {"text": "ما هو أطول نهر في العالم؟", "answer": "النيل", "category": "جغرافيا", "difficulty": 1},
        {"text": "ما هو الكوكب الذي يُعرف بـ 'الكوكب الأحمر' ؟", "answer": "المريخ", "category": "فلك", "difficulty": 1},
        {"text": "من هو مؤسس شركة مايكروسوفت ؟", "answer": "بيل غيتس", "category": "تكنولوجيا", "difficulty": 1},
        {"text": "في أي سنة تولى الأمير محمد بن سلمان ولاية العهد في السعودية؟", "answer": "2017", "category": "سياسة", "difficulty": 2},
        {"text": "في أي سنة تأسست المملكة العربية السعودية ؟", "answer": "1932", "category": "تاريخ", "difficulty": 2},
        {"text": "ما هي عاصمة اليابان؟", "answer": "طوكيو", "category": "جغرافيا", "difficulty": 1},
        {"text": "ما هي أكبر دولة في العالم من حيث المساحة؟", "answer": "روسيا", "category": "جغرافيا", "difficulty": 1},
        {"text": "في أي قارة تقع دولة مصر ؟", "answer": "افريقيا", "category": "جغرافيا", "difficulty": 1},
        {"text": "ماهي عاصمة كندا ؟", "answer": "أوتاوا", "category": "جغرافيا", "difficulty": 2},
        {"text": "ماهي الدولة التي تقع في كلا القارتين الأوروبية والآسيوية؟", "answer": "تركيا", "category": "جغرافيا", "difficulty": 2},
        {"text": "ما هي أصغر دولة في العالم من حيث المساحة ؟", "answer": "الفاتيكان", "category": "جغرافيا", "difficulty": 2},
        {"text": "ما هي عاصمة البرازيل؟", "answer": "برازيليا", "category": "جغرافيا", "difficulty": 2},
        {"text": "من هو الهداف التاريخي لمنتخب البرازيل في كرة القدم ؟", "answer": "نيمار", "category": "رياضة", "difficulty": 2},
        {"text": "في أي عام فاز المنتخب الألماني ببطولة كأس العالم لأول مرة؟", "answer": "1954", "category": "رياضة", "difficulty": 3},
        {"text": "من هو اللاعب الذي فاز بجائزة الكرة الذهبية أكثر من أي لاعب آخر في تاريخ كرة القدم؟", "answer": "ميسي", "category": "رياضة", "difficulty": 1},
        {"text": "من هو مدرب منتخب فرنسا الذي قاد الفريق للفوز بكأس العالم 1998؟", "answer": "ديدييه ديشامب", "category": "رياضة", "difficulty": 3},
        {"text": "أي نادي فاز بدوري أبطال أوروبا موسم 2020-2021 ؟", "answer": "تشيلسي", "category": "رياضة", "difficulty": 2},
        {"text": "ما هو أكبر فوز في تاريخ كأس العالم في مباراة واحدة ؟", "answer": "10", "category": "رياضة", "difficulty": 3},
        {"text": "من هو اللاعب الذي سجل أول هدف في تاريخ كأس العالم؟", "answer": "هيرمان كادينسكي", "category": "رياضة", "difficulty": 3},
        {"text": "في أي سنة فاز نادي الهلال السعودي بأول بطولة دوري أبطال آسيا ؟", "answer": "1991", "category": "رياضة", "difficulty": 2},
        {"text": "من هو الملقب بالجوهرة السوداء في كرة القدم ؟", "answer": "بيليه", "category": "رياضة", "difficulty": 1},
        {"text": "ما هو أطول نهر في قارة آسيا ؟", "answer": "اليانغتسي", "category": "جغرافيا", "difficulty": 3},
        {"text": "ماهي عاصمة المغرب ؟", "answer": "الرباط", "category": "جغرافيا", "difficulty": 2},
        {"text": "كم كان عمر رسول الله -صلّى الله عليه وسلّم- عندما بعثه الله -تعالى- بالرسالة؟", "answer": "اربعين", "category": "ديني", "difficulty": 1},
        {"text": "ما الشجرة الملعونة التى ذكرت فى القرآن الكريم ؟", "answer": "الزقوم", "category": "ديني", "difficulty": 2},
        {"text": "ما أول أمر نزل فى القرآن الكريم ؟", "answer": "اقرأ", "category": "ديني", "difficulty": 1},
        {"text": "ما هي عاصمة الإمارات العربية المتحدة؟", "answer": "ابو ظبي", "category": "جغرافيا", "difficulty": 1},
        {"text": "هو أكبر بحر في العالم من حيث المساحة؟", "answer": "قزوين", "category": "جغرافيا", "difficulty": 3},
        {"text": "ما هي الدولة العربية التي تشتهر بأنها 'أرض الأرز؟", "answer": "لبنان", "category": "ثقافة عامة", "difficulty": 1},
        {"text": "في أي دولة عربية يقع جبل طارق ؟", "answer": "المغرب", "category": "جغرافيا", "difficulty": 2},
        {"text": "من هو حاكم قطر الحالي؟", "answer": "تميم بن حمد", "category": "سياسة", "difficulty": 1},
        {"text": "من هو مؤسس دولة الكويت ؟", "answer": "الشيخ صباح الاول", "category": "تاريخ", "difficulty": 2},
        {"text": "في أي عام سقطت دولة الاتحاد السوفيتي؟", "answer": "1991", "category": "تاريخ", "difficulty": 2},
        {"text": "من هو الزعيم الذي تم اغتياله في 1965 وكان زعيم حركة الحقوق المدنية في الولايات المتحدة ؟", "answer": "مالكوم اكس", "category": "تاريخ", "difficulty": 3},
        {"text": "ما هو الكتاب المقدس في الديانة المسيحية ؟", "answer": "الانجيل", "category": "ديني", "difficulty": 1},
    ]
    
    # إضافة الأسئلة إلى قاعدة البيانات
    for q in questions:
        question = Question(
            text=q["text"],
            answer=q["answer"],
            category=q["category"],
            difficulty=q["difficulty"],
            question_type="normal"
        )
        db.session.add(question)
    
    # Golden Question - سؤال الذهب
    gold_questions = [
        {"text": "ما هو اسم أعمق نقطة في المحيط؟", "answer": "خندق ماريانا", "category": "جغرافيا", "difficulty": 3},
        {"text": "ما هو أكبر عضو في جسم الإنسان؟", "answer": "الجلد", "category": "طب", "difficulty": 2},
        {"text": "ما هي أطول كلمة في اللغة العربية؟", "answer": "أفاستسقيناكموها", "category": "لغة", "difficulty": 3}
    ]
    
    for q in gold_questions:
        question = Question(
            text=q["text"],
            answer=q["answer"],
            category=q["category"],
            difficulty=q["difficulty"],
            question_type="golden"
        )
        db.session.add(question)
    
    # Steal Question - سؤال الزرف
    steal_questions = [
        {"text": "كم عدد قلوب الأخطبوط؟", "answer": "3", "category": "علوم", "difficulty": 3},
        {"text": "ما اسم أكبر صحراء جليدية في العالم؟", "answer": "انتاركتيكا", "category": "جغرافيا", "difficulty": 3},
        {"text": "ما هو أكثر عنصر وفرة في القشرة الأرضية؟", "answer": "الأكسجين", "category": "كيمياء", "difficulty": 3}
    ]
    
    for q in steal_questions:
        question = Question(
            text=q["text"],
            answer=q["answer"],
            category=q["category"],
            difficulty=q["difficulty"],
            question_type="steal"
        )
        db.session.add(question)
    
    # Doom Question - سؤال الدووم
    doom_questions = [
        {"text": "من هو مخترع المصباح الكهربائي؟", "answer": "توماس إديسون", "category": "تاريخ", "difficulty": 2},
        {"text": "ما هي أقوى عضلة في جسم الإنسان؟", "answer": "عضلة الفك", "category": "طب", "difficulty": 3},
        {"text": "ما هو أقدم نظام كتابة في العالم؟", "answer": "الكتابة المسمارية", "category": "تاريخ", "difficulty": 3}
    ]
    
    for q in doom_questions:
        question = Question(
            text=q["text"],
            answer=q["answer"],
            category=q["category"],
            difficulty=q["difficulty"],
            question_type="doom"
        )
        db.session.add(question)
    
    # أسئلة إضافية متنوعة
    additional_questions = [
        # أسئلة سياسية
        {"text": "في أي عام تأسست الأمم المتحدة؟", "answer": "1945", "category": "سياسة", "difficulty": 2},
        {"text": "من هو أول رئيس وزراء للمملكة العربية السعودية؟", "answer": "الملك فيصل", "category": "سياسة", "difficulty": 2},
        {"text": "ما هي عاصمة كوريا الشمالية؟", "answer": "بيونغ يانغ", "category": "سياسة", "difficulty": 2},
        {"text": "من هو مؤسس دولة الإمارات العربية المتحدة؟", "answer": "الشيخ زايد", "category": "سياسة", "difficulty": 1},
        {"text": "ما اسم المعاهدة التي أنهت الحرب العالمية الأولى؟", "answer": "فرساي", "category": "سياسة", "difficulty": 2},
        
        # أسئلة دينية
        {"text": "كم عدد سور القرآن الكريم؟", "answer": "114", "category": "ديني", "difficulty": 1},
        {"text": "من هو أول من جمع القرآن الكريم؟", "answer": "أبو بكر الصديق", "category": "ديني", "difficulty": 2},
        {"text": "كم عدد الحواريين في المسيحية؟", "answer": "12", "category": "ديني", "difficulty": 2},
        {"text": "ما هو شهر الصيام عند المسلمين؟", "answer": "رمضان", "category": "ديني", "difficulty": 1},
        {"text": "ما هو الكتاب المقدس في الديانة اليهودية؟", "answer": "التوراة", "category": "ديني", "difficulty": 1},
        
        # أسئلة ثقافية
        {"text": "من هو مؤلف كتاب الأمير؟", "answer": "ميكافيلي", "category": "ثقافة", "difficulty": 3},
        {"text": "ما هو اللون الناتج عن مزج اللونين الأحمر والأزرق؟", "answer": "البنفسجي", "category": "ثقافة عامة", "difficulty": 1},
        {"text": "ما هو أشهر مسرح في لندن؟", "answer": "مسرح جلوب", "category": "ثقافة", "difficulty": 3},
        {"text": "من هو مؤلف سيمفونية القدر؟", "answer": "بيتهوفن", "category": "ثقافة", "difficulty": 2},
        {"text": "ما هي أطول سلسلة جبال في العالم؟", "answer": "جبال الأنديز", "category": "ثقافة عامة", "difficulty": 2},
        
        # أسئلة تاريخية
        {"text": "في أي عام وقعت معركة بدر الكبرى؟", "answer": "2 هجري", "category": "تاريخ", "difficulty": 2},
        {"text": "من هو الخليفة الرابع في الدولة الإسلامية؟", "answer": "علي بن أبي طالب", "category": "تاريخ", "difficulty": 2},
        {"text": "ما هي أول دولة استخدمت العملة الورقية؟", "answer": "الصين", "category": "تاريخ", "difficulty": 3},
        {"text": "من هو فاتح القسطنطينية؟", "answer": "محمد الفاتح", "category": "تاريخ", "difficulty": 2},
        {"text": "في أي عام سقطت غرناطة آخر معاقل المسلمين في الأندلس؟", "answer": "1492", "category": "تاريخ", "difficulty": 3},
        
        # أسئلة رياضية
        {"text": "من هو اللاعب الملقب بالظاهرة في كرة القدم؟", "answer": "رونالدو", "category": "رياضة", "difficulty": 2},
        {"text": "كم عدد لاعبي فريق كرة السلة؟", "answer": "5", "category": "رياضة", "difficulty": 1},
        {"text": "في أي رياضة يستخدم مصطلح الهاتريك؟", "answer": "كرة القدم", "category": "رياضة", "difficulty": 1},
        {"text": "ما هي الدولة التي استضافت أول كأس عالم لكرة القدم؟", "answer": "الأوروجواي", "category": "رياضة", "difficulty": 3},
        {"text": "كم مرة فاز منتخب البرازيل بكأس العالم؟", "answer": "5", "category": "رياضة", "difficulty": 2},
        
        # أسئلة حياتية
        {"text": "ما هو الفيتامين المستخلص من أشعة الشمس؟", "answer": "د", "category": "حياتية", "difficulty": 1},
        {"text": "كم ساعة يحتاج الإنسان للنوم يومياً؟", "answer": "8", "category": "حياتية", "difficulty": 1},
        {"text": "ما هي أكثر لغة منطوقة في العالم من حيث عدد المتحدثين الأصليين؟", "answer": "الماندرين", "category": "حياتية", "difficulty": 2},
        {"text": "ما هي الفاكهة التي تسمى ملكة الفواكه؟", "answer": "المانجو", "category": "حياتية", "difficulty": 2},
        {"text": "كم عدد العظام في جسم الإنسان البالغ؟", "answer": "206", "category": "حياتية", "difficulty": 2},
        
        # أسئلة تكنولوجية
        {"text": "ما هو العام الذي تم فيه إطلاق أول آيفون؟", "answer": "2007", "category": "تكنولوجيا", "difficulty": 2},
        {"text": "ما هو اسم مؤسس فيسبوك؟", "answer": "مارك زوكربيرج", "category": "تكنولوجيا", "difficulty": 1},
        {"text": "ما هي اللغة الأساسية المستخدمة في تطوير صفحات الويب؟", "answer": "HTML", "category": "تكنولوجيا", "difficulty": 2},
        {"text": "أي شركة ابتكرت نظام التشغيل أندرويد؟", "answer": "جوجل", "category": "تكنولوجيا", "difficulty": 1},
        {"text": "ما هي وحدة قياس سرعة الإنترنت؟", "answer": "ميجابت في الثانية", "category": "تكنولوجيا", "difficulty": 2},

        # أسئلة غريبة وغير متوقعة
        {"text": "ما هو الحيوان الذي له ثلاثة قلوب وثمانية أذرع؟", "answer": "الأخطبوط", "category": "غرائب", "difficulty": 2},
        {"text": "ما هو الحيوان الوحيد الذي لا يستطيع القفز؟", "answer": "الفيل", "category": "غرائب", "difficulty": 2},
        {"text": "ما هو الشيء الذي يرتفع كلما قل وزنه؟", "answer": "البالون", "category": "ألغاز", "difficulty": 2},
        {"text": "ما هو الجبل الذي يطلق عليه سقف العالم؟", "answer": "إفرست", "category": "جغرافيا", "difficulty": 1},
        {"text": "ما هو الطائر الذي لا يطير؟", "answer": "البطريق", "category": "حيوانات", "difficulty": 1},
        {"text": "ما هو الحيوان الذي يرى بأذنيه؟", "answer": "الخفاش", "category": "حيوانات", "difficulty": 1},
        {"text": "ما هو أكثر حيوان سام في العالم؟", "answer": "قنديل البحر المربع", "category": "حيوانات", "difficulty": 3},
        {"text": "ما هو الفرق بين الزرافة الذكر والزرافة الأنثى؟", "answer": "لا يوجد فرق", "category": "غرائب", "difficulty": 3},
        {"text": "أين يتواجد أكبر مخزون للذهب في العالم؟", "answer": "المحيطات", "category": "غرائب", "difficulty": 3},
        {"text": "ما هو أكثر الفواكه استهلاكاً في العالم؟", "answer": "الموز", "category": "غرائب", "difficulty": 2},
    ]
    
    for q in additional_questions:
        question = Question(
            text=q["text"],
            answer=q["answer"],
            category=q["category"],
            difficulty=q["difficulty"],
            question_type="normal"
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
        "أقل من 50؟ لاتعليق",
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


def add_praise_responses():
    """إضافة ردود المدح والثناء للفائزين"""
    
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
        {"text": "نحتاج عقول مثلك في العالم! 🌍 استمر في التفوق", "min_score": 150, "game_mode": "all"},
        
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
    
    return "تمت إضافة ردود المدح والثناء بنجاح!"

if __name__ == "__main__":
    with app.app_context():
        add_user_questions()
        add_funny_responses()
        add_praise_responses()
        print("تمت إضافة جميع الأسئلة وردود التفاعل بنجاح!")