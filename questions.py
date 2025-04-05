import random
import json
import os
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Default questions in Arabic
DEFAULT_QUESTIONS = [
    {"question": "ما هي عاصمة المملكة العربية السعودية؟", "answer": "الرياض", "category": "جغرافيا"},
    {"question": "من هو مؤسس شركة مايكروسوفت؟", "answer": "بيل غيتس", "category": "تكنولوجيا"},
    {"question": "كم عدد لاعبي كرة القدم في الملعب؟", "answer": "11", "category": "رياضة"},
    {"question": "ما هو العنصر الكيميائي الذي رمزه O؟", "answer": "أكسجين", "category": "علوم"},
    {"question": "من هو مؤلف كتاب الأمير؟", "answer": "ميكافيلي", "category": "أدب"},
    {"question": "متى تأسست الأمم المتحدة؟", "answer": "1945", "category": "تاريخ"},
    {"question": "من هو أول رائد فضاء وصل إلى القمر؟", "answer": "نيل أرمسترونغ", "category": "فضاء"},
    {"question": "ما هو أطول نهر في العالم؟", "answer": "النيل", "category": "جغرافيا"},
    {"question": "ما اسم العملة المستخدمة في اليابان؟", "answer": "ين", "category": "اقتصاد"},
    {"question": "من هو مخترع المصباح الكهربائي؟", "answer": "توماس إديسون", "category": "اختراعات"},
    {"question": "ما هي أكبر قارة في العالم؟", "answer": "آسيا", "category": "جغرافيا"},
    {"question": "ما هو الحيوان الذي يلقب بملك الغابة؟", "answer": "الأسد", "category": "حيوانات"},
    {"question": "كم عدد أحرف اللغة العربية؟", "answer": "28", "category": "لغة"},
    {"question": "ما هي لغة البرمجة الأكثر استخداماً في العالم؟", "answer": "جافاسكريبت", "category": "برمجة"},
    {"question": "ما هو أسرع حيوان في العالم؟", "answer": "الفهد", "category": "حيوانات"},
    {"question": "من هو مخترع الإنترنت؟", "answer": "تيم بيرنرز لي", "category": "تكنولوجيا"},
    {"question": "ما هي أكبر دولة في العالم من حيث المساحة؟", "answer": "روسيا", "category": "جغرافيا"},
    {"question": "ما اسم أكبر محيط في العالم؟", "answer": "المحيط الهادي", "category": "جغرافيا"},
    {"question": "ما هي عملة دولة الإمارات العربية المتحدة؟", "answer": "درهم", "category": "اقتصاد"},
    {"question": "من هو مؤلف رواية الحرب والسلام؟", "answer": "تولستوي", "category": "أدب"},
    {"question": "ما هو العنصر الأكثر وفرة في القشرة الأرضية؟", "answer": "الأكسجين", "category": "علوم"},
    {"question": "من رسم لوحة الموناليزا؟", "answer": "ليوناردو دافنشي", "category": "فن"},
    {"question": "ما هو أكبر عضو في جسم الإنسان؟", "answer": "الجلد", "category": "طب"},
    {"question": "ما هي أكبر دولة عربية من حيث عدد السكان؟", "answer": "مصر", "category": "جغرافيا"},
    {"question": "ما هو البحر الذي لا يوجد له سواحل؟", "answer": "بحر سرغاسو", "category": "جغرافيا"},
    {"question": "من هو مخترع الهاتف؟", "answer": "ألكسندر جراهام بيل", "category": "اختراعات"},
    {"question": "كم عدد أضلاع المثمن؟", "answer": "8", "category": "رياضيات"},
    {"question": "ما هي أصغر قارة في العالم؟", "answer": "أستراليا", "category": "جغرافيا"},
    {"question": "من هو أول رئيس للولايات المتحدة الأمريكية؟", "answer": "جورج واشنطن", "category": "تاريخ"},
    {"question": "ما هو اسم صغير الأسد؟", "answer": "شبل", "category": "حيوانات"}
]

def load_questions_from_file(filename):
    """Load questions from a JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                logger.info(f"Loaded {len(questions)} questions from {filename}")
                return questions
        return []
    except Exception as e:
        logger.error(f"Error loading questions from {filename}: {e}")
        return []

def save_questions_to_file(questions, filename):
    """Save questions to a JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved {len(questions)} questions to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving questions to {filename}: {e}")
        return False

def load_default_questions():
    """Load default questions plus any from file"""
    # First try to load from file
    custom_questions = load_questions_from_file('questions.json')
    
    # If no custom questions, save the default ones to file
    if not custom_questions:
        save_questions_to_file(DEFAULT_QUESTIONS, 'questions.json')
        return DEFAULT_QUESTIONS
    
    # Combine default and custom questions
    all_questions = DEFAULT_QUESTIONS.copy()
    all_questions.extend(custom_questions)
    
    return all_questions

def get_random_question():
    """Get a random question from the loaded questions"""
    questions = load_default_questions()
    if not questions:
        # If no questions available, return a default one
        return {
            "question": "ما هي عاصمة المملكة العربية السعودية؟", 
            "answer": "الرياض", 
            "category": "جغرافيا"
        }
    
    return random.choice(questions)

def add_question(question, answer, category="عام"):
    """Add a new question to the question bank"""
    try:
        # Load existing questions
        questions = load_questions_from_file('questions.json')
        
        # Add new question
        questions.append({
            "question": question,
            "answer": answer,
            "category": category
        })
        
        # Save back to file
        save_questions_to_file(questions, 'questions.json')
        logger.info(f"Added new question: {question}")
        return True
    except Exception as e:
        logger.error(f"Error adding question: {e}")
        return False

def get_questions_by_category(category):
    """Get all questions in a specific category"""
    questions = load_default_questions()
    return [q for q in questions if q.get("category", "عام").lower() == category.lower()]

def get_question_categories():
    """Get list of all unique categories"""
    questions = load_default_questions()
    categories = set(q.get("category", "عام") for q in questions)
    return list(categories)
