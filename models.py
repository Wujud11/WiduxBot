class MentionSettings:
    def __init__(self, mention_enabled=True, max_mentions=5, timeout_duration=300,
                 warning_threshold=3, warning_message='', timeout_message='', cooldown_period=86400):
        self.mention_enabled = mention_enabled
        self.max_mentions = max_mentions
        self.timeout_duration = timeout_duration
        self.warning_threshold = warning_threshold
        self.warning_message = warning_message
        self.timeout_message = timeout_message
        self.cooldown_period = cooldown_period

class CustomReply:
    def __init__(self, username, reply):
        self.username = username
        self.reply = reply

class Question:
    def __init__(self, question, correct_answer, alternative_answers=None, 
                 category='General', question_type='Normal', time_limit=30):
        self.question = question
        self.correct_answer = correct_answer
        self.alternative_answers = alternative_answers or []
        self.category = category
        self.question_type = question_type
        # تعيين الوقت المخصص للإجابة حسب نوع السؤال
        if question_type == 'Normal':
            self.time_limit = time_limit  # استخدام الوقت المحدد من لوحة التحكم
        else:
            # أوقات ثابتة للأسئلة الخاصة
            default_times = {
                'Golden': 7,
                'Steal': 5,
                'Sabotage': 5,
                'The Test of Fate': 10,
                'Doom': 7
            }
            self.time_limit = default_times.get(question_type, 30)

class PraiseTeasing:
    def __init__(self):
        self.win_solo = []
        self.win_group = []
        self.win_team = []
        self.leader_doom_loss = []
        self.leader_lowest_points = []
        self.solo_loser = []
        self.team_loser = []
        self.points_below_50 = []

class Channel:
    def __init__(self, channel_name, platform='twitch', is_enabled=True):
        """
        تمثيل قناة يمكن للبوت العمل فيها
        
        :param channel_name: اسم القناة
        :param platform: منصة القناة (twitch)
        :param is_enabled: هل القناة مفعلة
        """
        self.channel_name = channel_name
        self.platform = platform
        self.is_enabled = is_enabled
        
class PointsSettings:
    def __init__(self, quick_answer_points=10, normal_answer_points=5, late_answer_points=0,
                 quick_answer_time=5, normal_answer_time=10, streak_enabled=True,
                 streak_threshold=3, streak_bonus_points=10, streak_messages=None):
        """
        إعدادات نظام النقاط والمكافآت
        
        :param quick_answer_points: نقاط الإجابة السريعة (أقل من 5 ثوانٍ)
        :param normal_answer_points: نقاط الإجابة العادية (5-10 ثوانٍ)
        :param late_answer_points: نقاط الإجابة المتأخرة (أكثر من 10 ثوانٍ)
        :param quick_answer_time: الوقت المحدد للإجابة السريعة (بالثواني)
        :param normal_answer_time: الوقت المحدد للإجابة العادية (بالثواني)
        :param streak_enabled: تفعيل نظام السلسلة (الستريك)
        :param streak_threshold: عدد الإجابات المتتالية لتفعيل المكافأة
        :param streak_bonus_points: نقاط مكافأة السلسلة
        :param streak_messages: رسائل مكافأة السلسلة
        """
        self.quick_answer_points = quick_answer_points
        self.normal_answer_points = normal_answer_points
        self.late_answer_points = late_answer_points
        self.quick_answer_time = quick_answer_time
        self.normal_answer_time = normal_answer_time
        self.streak_enabled = streak_enabled
        self.streak_threshold = streak_threshold
        self.streak_bonus_points = streak_bonus_points
        self.streak_messages = streak_messages or [
            "استمر! أنت على سلسلة إجابات صحيحة!",
            "رائع! سلسلة الإجابات الصحيحة مستمرة!",
            "أنت على نار! سلسلة الإجابات الصحيحة تزداد!"
        ]
