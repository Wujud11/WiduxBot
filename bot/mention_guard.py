import time
import random

class MentionGuard:
    def __init__(self):
        self.mention_counts = {}
        self.timeout_given = {}
        self.special_responses = {}
        self.general_roasts = []
        self.no_timeout_users = {}

        self.mention_limit = 3
        self.warning_threshold = 2
        self.timeout_duration = 5
        self.cooldown_period = 86400
        self.warning_message = "انتبه، باقي لك شوي وتبلع تايم"
        self.timeout_message = "لقم تايم أوت بسيط، مزحة من البوت"

    def set_config(self, limit, duration, cooldown, warning_thresh, warn_msg, timeout_msg):
        self.mention_limit = limit
        self.timeout_duration = duration
        self.cooldown_period = cooldown
        self.warning_threshold = warning_thresh
        self.warning_message = warn_msg
        self.timeout_message = timeout_msg

    def add_special_responses(self, username, responses):
        self.special_responses[username] = responses

    def handle_mention(self, user):
        now = time.time()

        # 1. إذا عنده ردود خاصة → دايمًا ياخذ طقطقة خاصة
        if user in self.special_responses:
            return {"action": "roast", "message": random.choice(self.special_responses[user])}

        # 2. إذا أخذ تايم أوت سابقًا → تحقق إذا مر يوم كامل
        if user in self.no_timeout_users:
            if now - self.no_timeout_users[user] < self.cooldown_period:
                return {"action": "roast", "message": random.choice(self.general_roasts)}
            else:
                del self.no_timeout_users[user]  # يمسح القديم ويرجع يعد من جديد

        # 3. زيد عدد المنشنات
        self.mention_counts[user] = self.mention_counts.get(user, 0) + 1
        count = self.mention_counts[user]

        # 4. إذا وصل للتحذير
        if count == self.warning_threshold:
            return {"action": "warn", "message": self.warning_message}

        # 5. إذا تجاوز الحد المسموح به للمنشن
        if count >= self.mention_limit:
            self.no_timeout_users[user] = now
            return {
                "action": "timeout",
                "message": self.timeout_message,
                "duration": self.timeout_duration
            }

        # 6. رد عادي قبل لا يوصل حد التايم أوت
        return {"action": "roast", "message": random.choice(self.general_roasts)}
