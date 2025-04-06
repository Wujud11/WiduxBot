"""
مكتبة أسئلة متنوعة ليدووم بوت
تشمل أسئلة في مختلف المجالات: رياضة، سياسة، حيوانات، علوم، دين، ثقافة عامة، ألغاز وغيرها
"""

SAMPLE_QUESTIONS = [
    # كرة القدم
    {
        "question": "من هو الفائز بكأس العالم 2022 لكرة القدم؟",
        "correct_answer": "الأرجنتين", 
        "alternative_answers": "argentina,ارجنتين,الارجنتين",
        "category": "كرة قدم",
        "difficulty": "normal"
    },
    {
        "question": "ما هو النادي الذي يلعب له كريستيانو رونالدو؟",
        "correct_answer": "النصر",
        "alternative_answers": "al nassr,الناصر,نصر",
        "category": "كرة قدم",
        "difficulty": "normal"
    },
    {
        "question": "من هو هداف الدوري السعودي التاريخي؟",
        "correct_answer": "ماجد عبدالله",
        "alternative_answers": "ماجد,عبدالله,majed abdullah",
        "category": "كرة قدم",
        "difficulty": "normal"
    },
    {
        "question": "من هو لاعب كرة القدم الملقب بالأسطورة البرازيلي؟",
        "correct_answer": "بيليه",
        "alternative_answers": "بيليه,pele,بيله",
        "category": "كرة قدم",
        "difficulty": "normal"
    },
    {
        "question": "أي نادي سعودي فاز بأكبر عدد من بطولات دوري أبطال آسيا لكرة القدم؟",
        "correct_answer": "الهلال",
        "alternative_answers": "نادي الهلال,al hilal,هلال",
        "category": "كرة قدم",
        "difficulty": "normal"
    },
    {
        "question": "كم مرة فازت البرازيل بكأس العالم لكرة القدم؟",
        "correct_answer": "5",
        "alternative_answers": "خمس,خمسة,5 مرات,خمس مرات",
        "category": "كرة قدم",
        "difficulty": "normal"
    },
    {
        "question": "من هو أكثر لاعب تسجيلاً للأهداف في تاريخ كأس العالم؟",
        "correct_answer": "ميروسلاف كلوزه",
        "alternative_answers": "كلوزه,miroslav klose,ميروسلاف",
        "category": "كرة قدم",
        "difficulty": "normal"
    },
    {
        "question": "أي فريق فاز بأول نسخة من كأس العالم لكرة القدم عام 1930؟",
        "correct_answer": "الأوروغواي",
        "alternative_answers": "uruguay,اوروغواي,اوروجواي,الاوروغواي",
        "category": "كرة قدم",
        "difficulty": "golden"
    },
    
    # رياضات متنوعة
    {
        "question": "ما هي الرياضة التي اشتهر بها محمد علي كلاي؟",
        "correct_answer": "الملاكمة",
        "alternative_answers": "boxing,ملاكمة",
        "category": "رياضة",
        "difficulty": "normal"
    },
    {
        "question": "ما هو عدد لاعبي فريق كرة السلة داخل الملعب؟",
        "correct_answer": "5",
        "alternative_answers": "خمسة,خمس,5 لاعبين,خمسة لاعبين",
        "category": "رياضة",
        "difficulty": "normal"
    },
    {
        "question": "من هو السباح الأمريكي الذي حصد 23 ميدالية ذهبية أولمبية؟",
        "correct_answer": "مايكل فيلبس",
        "alternative_answers": "فيلبس,michael phelps",
        "category": "رياضة",
        "difficulty": "normal"
    },
    {
        "question": "ما هي الرياضة التي تستخدم فيها المضرب والريشة؟",
        "correct_answer": "الريشة الطائرة",
        "alternative_answers": "badminton,الريشه,ريشة طائرة,بادمنتون",
        "category": "رياضة",
        "difficulty": "normal"
    },
    {
        "question": "ما هي أطول سباقات الجري في الألعاب الأولمبية؟",
        "correct_answer": "الماراثون",
        "alternative_answers": "marathon,ماراثون",
        "category": "رياضة",
        "difficulty": "normal"
    },
    
    # سياسة وتاريخ
    {
        "question": "من هو أول رئيس للولايات المتحدة الأمريكية؟",
        "correct_answer": "جورج واشنطن",
        "alternative_answers": "واشنطن,george washington",
        "category": "سياسة وتاريخ",
        "difficulty": "normal"
    },
    {
        "question": "في أي عام تأسست المملكة العربية السعودية الحديثة؟",
        "correct_answer": "1932",
        "alternative_answers": "١٩٣٢,عام 1932",
        "category": "سياسة وتاريخ",
        "difficulty": "normal"
    },
    {
        "question": "من هو مؤسس المملكة العربية السعودية الحديثة؟",
        "correct_answer": "الملك عبدالعزيز آل سعود",
        "alternative_answers": "عبدالعزيز,الملك عبدالعزيز,عبد العزيز آل سعود",
        "category": "سياسة وتاريخ",
        "difficulty": "normal"
    },
    {
        "question": "ما هي عاصمة جمهورية مصر العربية؟",
        "correct_answer": "القاهرة",
        "alternative_answers": "cairo,القاهره",
        "category": "سياسة وتاريخ",
        "difficulty": "normal"
    },
    {
        "question": "من هو الرئيس المصري الحالي؟",
        "correct_answer": "عبدالفتاح السيسي",
        "alternative_answers": "السيسي,عبد الفتاح السيسي,sisi",
        "category": "سياسة وتاريخ",
        "difficulty": "normal"
    },
    {
        "question": "متى كانت الحرب العالمية الثانية؟",
        "correct_answer": "1939-1945",
        "alternative_answers": "1939-45,١٩٣٩-١٩٤٥,1939 الى 1945",
        "category": "سياسة وتاريخ",
        "difficulty": "normal"
    },
    {
        "question": "من هو الملك الأول للمملكة العربية السعودية؟",
        "correct_answer": "الملك عبدالعزيز",
        "alternative_answers": "عبدالعزيز,عبد العزيز,king abdulaziz",
        "category": "سياسة وتاريخ",
        "difficulty": "normal"
    },
    
    # حيوانات
    {
        "question": "ما هو أسرع حيوان بري على وجه الأرض؟",
        "correct_answer": "الفهد",
        "alternative_answers": "cheetah,فهد",
        "category": "حيوانات",
        "difficulty": "normal"
    },
    {
        "question": "ما هو أكبر حيوان في العالم؟",
        "correct_answer": "الحوت الأزرق",
        "alternative_answers": "blue whale,حوت ازرق,الحوت",
        "category": "حيوانات",
        "difficulty": "normal"
    },
    {
        "question": "كم قلب للأخطبوط؟",
        "correct_answer": "3",
        "alternative_answers": "ثلاثة,ثلاث,3 قلوب,ثلاثة قلوب",
        "category": "حيوانات",
        "difficulty": "golden"
    },
    {
        "question": "أي حيوان يمكنه النظر في اتجاهين مختلفين في نفس الوقت؟",
        "correct_answer": "الحرباء",
        "alternative_answers": "chameleon,حرباء",
        "category": "حيوانات",
        "difficulty": "normal"
    },
    {
        "question": "أي حيوان لديه بصمة لسان فريدة مثل بصمة الإصبع عند البشر؟",
        "correct_answer": "الكلب",
        "alternative_answers": "dog,كلب,الكلاب",
        "category": "حيوانات",
        "difficulty": "steal"
    },
    
    # علوم وتكنولوجيا
    {
        "question": "ما هو العنصر الكيميائي الأكثر وفرة في الكون؟",
        "correct_answer": "الهيدروجين",
        "alternative_answers": "hydrogen,هيدروجين",
        "category": "علوم",
        "difficulty": "normal"
    },
    {
        "question": "ما هو أكبر كوكب في المجموعة الشمسية؟",
        "correct_answer": "المشتري",
        "alternative_answers": "jupiter,جوبيتر,كوكب المشتري",
        "category": "علوم",
        "difficulty": "normal"
    },
    {
        "question": "ما هي أقرب مجرة إلى مجرتنا؟",
        "correct_answer": "اندروميدا",
        "alternative_answers": "andromeda,مجرة اندروميدا",
        "category": "علوم",
        "difficulty": "normal"
    },
    {
        "question": "من اخترع المصباح الكهربائي؟",
        "correct_answer": "توماس إديسون",
        "alternative_answers": "اديسون,edison,thomas edison",
        "category": "علوم",
        "difficulty": "normal"
    },
    {
        "question": "ما هي وحدة قياس القوة؟",
        "correct_answer": "نيوتن",
        "alternative_answers": "newton",
        "category": "علوم",
        "difficulty": "normal"
    },
    {
        "question": "ما هو الغاز الأكثر وفرة في الغلاف الجوي للأرض؟",
        "correct_answer": "النيتروجين",
        "alternative_answers": "nitrogen,نيتروجين",
        "category": "علوم",
        "difficulty": "normal"
    },
    {
        "question": "ما هي درجة غليان الماء بمقياس سيلسيوس عند مستوى سطح البحر؟",
        "correct_answer": "100",
        "alternative_answers": "١٠٠,100 درجة,مئة",
        "category": "علوم",
        "difficulty": "normal"
    },
    
    # دين وثقافة إسلامية
    {
        "question": "كم عدد أركان الإسلام؟",
        "correct_answer": "5",
        "alternative_answers": "خمسة,خمس,٥",
        "category": "دين",
        "difficulty": "normal"
    },
    {
        "question": "من هو أول الخلفاء الراشدين؟",
        "correct_answer": "أبو بكر الصديق",
        "alternative_answers": "ابو بكر,الصديق",
        "category": "دين",
        "difficulty": "normal"
    },
    {
        "question": "ما هي أطول سورة في القرآن الكريم؟",
        "correct_answer": "البقرة",
        "alternative_answers": "سورة البقرة,al baqarah",
        "category": "دين",
        "difficulty": "normal"
    },
    {
        "question": "من هو النبي الملقب بأبي الأنبياء؟",
        "correct_answer": "إبراهيم",
        "alternative_answers": "ابراهيم,ibrahim,سيدنا إبراهيم",
        "category": "دين",
        "difficulty": "normal"
    },
    {
        "question": "كم عدد سور القرآن الكريم؟",
        "correct_answer": "114",
        "alternative_answers": "١١٤,مئة وأربعة عشر",
        "category": "دين",
        "difficulty": "normal"
    },
    
    # ثقافة عامة
    {
        "question": "من هو مؤلف رواية الف ليلة وليلة؟",
        "correct_answer": "غير معروف",
        "alternative_answers": "مجهول,لا يوجد,مؤلفون مجهولون",
        "category": "ثقافة عامة",
        "difficulty": "steal"
    },
    {
        "question": "ما هي عملة المملكة العربية السعودية؟",
        "correct_answer": "الريال",
        "alternative_answers": "riyal,ريال,الريال السعودي",
        "category": "ثقافة عامة",
        "difficulty": "normal"
    },
    {
        "question": "ما هي أطول سلسلة جبال في العالم؟",
        "correct_answer": "جبال الأنديز",
        "alternative_answers": "الانديز,andes,جبال انديز",
        "category": "ثقافة عامة",
        "difficulty": "normal"
    },
    {
        "question": "ما هي أكبر صحراء في العالم؟",
        "correct_answer": "الصحراء الكبرى",
        "alternative_answers": "sahara,صحراء الكبرى,الصحراء",
        "category": "ثقافة عامة",
        "difficulty": "normal"
    },
    {
        "question": "ما هي اللغة الأكثر انتشاراً في العالم من حيث عدد المتحدثين بها كلغة أم؟",
        "correct_answer": "الصينية",
        "alternative_answers": "chinese,صينية,اللغة الصينية,الماندرين",
        "category": "ثقافة عامة",
        "difficulty": "normal"
    },
    {
        "question": "في أي عام تأسست شركة أبل؟",
        "correct_answer": "1976",
        "alternative_answers": "١٩٧٦,عام 1976",
        "category": "ثقافة عامة",
        "difficulty": "normal"
    },
    
    # أسئلة ذكاء وألغاز
    {
        "question": "ماهو الشيء الذي يمكن كسره دون أن تلمسه؟",
        "correct_answer": "الوعد",
        "alternative_answers": "وعد,promise,الصمت,silence",
        "category": "ألغاز",
        "difficulty": "normal"
    },
    {
        "question": "ما هو الشيء الذي يقع مرة واحدة في الدقيقة، ومرتين في اللحظة، ولا يقع أبداً في الساعة؟",
        "correct_answer": "حرف الميم",
        "alternative_answers": "م,حرف م,الميم",
        "category": "ألغاز",
        "difficulty": "sabotage"
    },
    {
        "question": "أنا ملك ليس لي مملكة، ولي تاج ولست بإنسان، فمن أنا؟",
        "correct_answer": "الأناناس",
        "alternative_answers": "اناناس,pineapple",
        "category": "ألغاز",
        "difficulty": "doom"
    },
    {
        "question": "ما هو الشيء الذي كلما زاد نقص؟",
        "correct_answer": "العمر",
        "alternative_answers": "عمر,age,السن",
        "category": "ألغاز",
        "difficulty": "normal"
    },
    {
        "question": "إذا كان عندك 10 سمكات وغرقت 3، كم سمكة بقيت؟",
        "correct_answer": "10",
        "alternative_answers": "عشرة,١٠,عشر",
        "category": "ألغاز",
        "difficulty": "golden"
    },
    
    # أسئلة صعبة ومتنوعة للTest of Fate
    {
        "question": "ما هو أصغر كوكب في المجموعة الشمسية؟",
        "correct_answer": "عطارد",
        "alternative_answers": "mercury,مركوري",
        "category": "علوم",
        "difficulty": "normal"
    },
    {
        "question": "في أي عام اكتشف كريستوفر كولومبوس القارة الأمريكية؟",
        "correct_answer": "1492",
        "alternative_answers": "١٤٩٢,عام 1492",
        "category": "تاريخ",
        "difficulty": "normal"
    },
    {
        "question": "من هو مخترع الطباعة في أوروبا؟",
        "correct_answer": "يوهانس غوتنبرغ",
        "alternative_answers": "gutenberg,غوتنبرغ",
        "category": "ثقافة عامة",
        "difficulty": "normal"
    },
    {
        "question": "ما هو العنصر الكيميائي الذي رمزه Au؟",
        "correct_answer": "الذهب",
        "alternative_answers": "gold,ذهب",
        "category": "علوم",
        "difficulty": "normal"
    },
    {
        "question": "ما هي البحيرة الأعمق في العالم؟",
        "correct_answer": "بحيرة بايكال",
        "alternative_answers": "بايكال,lake baikal",
        "category": "جغرافيا",
        "difficulty": "normal"
    },
    {
        "question": "من هو مؤلف كتاب 'الحرب والسلام'؟",
        "correct_answer": "ليو تولستوي",
        "alternative_answers": "تولستوي,tolstoy,leo tolstoy",
        "category": "أدب",
        "difficulty": "normal"
    },
    {
        "question": "ما هي المدينة التي تلقب بمدينة الضباب؟",
        "correct_answer": "لندن",
        "alternative_answers": "london",
        "category": "جغرافيا",
        "difficulty": "normal"
    },
    {
        "question": "كم عدد أضلاع مسدس مكعب روبيك القياسي؟",
        "correct_answer": "6",
        "alternative_answers": "ستة,٦,6 اضلاع",
        "category": "ألعاب",
        "difficulty": "normal"
    },
    {
        "question": "ما هي الدولة العربية التي لها حدود مع 7 دول؟",
        "correct_answer": "السعودية",
        "alternative_answers": "المملكة العربية السعودية,ksa,saudi",
        "category": "جغرافيا",
        "difficulty": "normal"
    },
    {
        "question": "ما هو الحيوان الذي ينام بعين واحدة مفتوحة؟",
        "correct_answer": "الدلفين",
        "alternative_answers": "dolphin,دلفين",
        "category": "حيوانات",
        "difficulty": "steal"
    },
    {
        "question": "ما هو أطول نهر في العالم؟",
        "correct_answer": "النيل",
        "alternative_answers": "nile,نهر النيل",
        "category": "جغرافيا",
        "difficulty": "normal"
    },
    {
        "question": "ما هو اسم صغير الأسد؟",
        "correct_answer": "الشبل",
        "alternative_answers": "شبل,cub",
        "category": "حيوانات",
        "difficulty": "normal"
    },
    {
        "question": "ما هي عاصمة استراليا؟",
        "correct_answer": "كانبرا",
        "alternative_answers": "canberra,كانبيرا",
        "category": "جغرافيا",
        "difficulty": "normal"
    },
    {
        "question": "كم عدد العظام في جسم الإنسان البالغ؟",
        "correct_answer": "206",
        "alternative_answers": "٢٠٦,206 عظمة",
        "category": "علوم حياتية",
        "difficulty": "doom"
    },
    {
        "question": "ما هي الدولة المستضيفة لكأس العالم 2026 لكرة القدم؟",
        "correct_answer": "أمريكا وكندا والمكسيك",
        "alternative_answers": "الولايات المتحدة وكندا والمكسيك,usa canada mexico,امريكا كندا المكسيك",
        "category": "كرة قدم",
        "difficulty": "normal"
    }
]

def get_sample_questions():
    """
    Return the sample questions list
    """
    return SAMPLE_QUESTIONS