import os

# Twitch configuration
TWITCH_TOKEN = 'a7raf1pqlq3oey1qo903mzy08d9qq3'
TWITCH_CLIENT_ID = 'gp762nuuoqcoxypju8c569th9wz7q5'
TWITCH_CHANNEL = os.environ.get('TWITCH_CHANNEL', '')

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
    "حظ أوفر للفريق!",
    "المرة القادمة ستكون أفضل!",
    "استمروا في المحاولة!"
]

LOSER_LEADER_MESSAGES = [
    "القائد يحتاج إلى مزيد من التدريب!",
    "حاول تحسين استراتيجيتك!",
    "لا تفقد الأمل!"
]

# General bot responses for mentions
DEFAULT_MENTION_RESPONSES = [
    "أهلاً! أنا بوت الألعاب والأسئلة. أكتب 'وج؟' لمعرفة كيفية اللعب.",
    "مرحباً! محتاج مساعدة؟ أكتب 'وج؟' لمعرفة التعليمات.",
    "أنا هنا للترفيه! أكتب 'وج؟' للعب معي.",
    "أهلاً! تبي تلعب معي؟ أكتب 'وج؟' لنبدأ.",
    "مرحباً بك في بوت الألعاب! أكتب 'وج؟' لبدء اللعب."
]

# Game configuration
DEFAULT_QUESTION_COUNT = 10
MIN_QUESTIONS = 5
MAX_QUESTIONS_TEAM = 15
MAX_QUESTIONS_SOLO = 20
QUESTION_TIMEOUT = 10  # seconds
REGISTRATION_TIMEOUT_TEAM = 20  # seconds
REGISTRATION_TIMEOUT_CHALLENGE = 15  # seconds
LEADER_SELECTION_TIMEOUT = 10  # seconds
MIN_PLAYERS_CHALLENGE = 2  # Minimum players for challenge mode (at least 2)
MIN_PLAYERS_TEAM = 3  # Minimum players per team (at least 3)

# الردود والرسائل
ELIMINATION_MESSAGES = [
    "هذي اوووووت",
    "برررا",
    "تفرج بس",
    "محد قالك ماتجاوب"
]

LOSER_LEADER_MESSAGES = [
    "الليدر؟ بالله هذا ليدر؟",
    "المشكلة؟ مو في الفريق، المشكلة في الثقة اللي عطوها لليدر"
]

LOSER_TEAM_MESSAGES = [
    "وش اللي صار؟ أحد ضغط زر الغباء الجماعي؟",
    "فريق مسوي نفسه حماسي، وطلع مجرد زحمة"
]

LOW_SCORE_MESSAGES = [
    "يا ساتر، وش كنت تحاول تسوي؟",
    "واضح إنك كنت تتحدى نفسك تفشل... ونجحت"
]

WINNER_MESSAGES = [
    "ما شاء الله عليك! أنت نجم اليوم!",
    "عبقري!",
    "أداء مذهل!"
]