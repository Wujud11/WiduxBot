import os
from models import Question, db

# Twitch configuration (غير مستخدمة في game_manager)
TWITCH_TOKEN = 'a7raf1pqlq3oey1qo903mzy08d9qq3'
TWITCH_CLIENT_ID = 'gp762nuuoqcoxypju8c569th9wz7q5'
TWITCH_CHANNEL = os.environ.get('TWITCH_CHANNEL', '')

# Game configuration
DEFAULT_QUESTION_COUNT = 10
MIN_QUESTIONS = 5
MAX_QUESTIONS_TEAM = 15
MAX_QUESTIONS_SOLO = 20
QUESTION_TIMEOUT = 10  # seconds
REGISTRATION_TIMEOUT_TEAM = 20  # seconds
REGISTRATION_TIMEOUT_CHALLENGE = 15  # seconds
LEADER_SELECTION_TIMEOUT = 10  # seconds
MIN_PLAYERS_CHALLENGE = 2
MIN_PLAYERS_TEAM = 3

# رسائل اللعبة
LOSER_MESSAGES = [
    "حظ أوفر المرة القادمة!",
    "لا تستسلم، حاول مرة أخرى!",
    "كان أداؤك جيداً، لكن يمكنك التحسن!"
]

WINNER_MESSAGES = [
    "أحسنت! أداء رائع!",
    "ما شاء الله عليك!",
    "مبروك على الفوز!"
]

LOSER_TEAM_MESSAGES = [
    "وش اللي صار؟ أحد ضغط زر الغباء الجماعي؟",
    "فريق مسوي نفسه حماسي، وطلع مجرد زحمة"
]

LOSER_LEADER_MESSAGES = [
    "الليدر؟ بالله هذا ليدر؟",
    "المشكلة؟ مو في الفريق، المشكلة في الثقة اللي عطوها لليدر"
]

LOW_SCORE_MESSAGES = [
    "يا ساتر، وش كنت تحاول تسوي؟",
    "واضح إنك كنت تتحدى نفسك تفشل... ونجحت"
]

# رسائل المدح الفردية (معدلة لهيكل القاموس)
INDIVIDUAL_PRAISE_MESSAGES = [
    {"game_mode": "solo", "min_score": 0, "text": "ممتاز! أداء رائع!"},
    {"game_mode": "all", "min_score": 10, "text": "واصل على هذا المستوى!"},
    {"game_mode": "solo", "min_score": 20, "text": "أنت نجم اليوم!"},
    {"game_mode": "all", "min_score": 30, "text": "عبقري!"},
    {"game_mode": "group", "min_score": 0, "text": "ما شاء الله عليك!"}
]

# رسائل مدح الفريق
TEAM_PRAISE_MESSAGES = [
    {"min_score": 100, "text": "فريق أسطوري! أداء خارق للعادة!"},
    {"min_score": 75, "text": "فريق متميز! تعاون رائع!"},
    {"min_score": 50, "text": "أداء جماعي ممتاز! استمروا!"},
    {"min_score": 25, "text": "فريق واعد! حافظوا على الحماس!"}
]

# رسائل أخرى (غير مستخدمة في game_manager)
DEFAULT_MENTION_RESPONSES = [
    "أهلاً! أنا بوت الألعاب والأسئلة. أكتب 'وج؟' لمعرفة كيفية اللعب.",
    "مرحباً! محتاج مساعدة؟ أكتب 'وج؟' لمعرفة التعليمات."
]

ELIMINATION_MESSAGES = [
    "اوووووت",
    "برررا",
    "تفرج بس"
]

def get_questions():
    """Get all active questions from the database"""
    questions = Question.query.filter_by(active=True).all()
    return [q.to_dict() for q in questions]