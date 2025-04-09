
import time
import random

class MentionGuard:
    def __init__(self):
        self.mention_counts = {}       # {user: count}
        self.timeout_given = {}        # {user: timestamp}
        self.special_responses = {}    # {user: [custom replies]}
        self.general_roasts = [        # ردود الطقطقة العامة
            "وش تبي؟ مشغوووول!",
            "ترى منشنك قاعد يستهلك طاقتي.",
            "قلنا لا تمنشنني! كأني فاضي؟",
            "ترى البوت عنده دوام يا ورع!",
            "برجع لك بعد سنة إذا خلصت المنشنات اللي قبلك.",
            "شكلك بتبلع تايم أوت قريب... اسحب."
        ]
        self.warning_threshold = 1
        self.mention_limit = 2
        self.timeout_duration = 5  # ثواني
        self.cooldown_period = 86400  # يوم كامل
        self.warning_message = "ترى ببلعك تايم أوت"
        self.timeout_message = "القم! أنا حذرتك"

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

        self.mention_counts[user] = self.mention_counts.get(user, 0) + 1

        if self.mention_counts[user] == self.warning_threshold:
            return {"action": "warn", "message": self.warning_message}

        if self.mention_counts[user] >= self.mention_limit:
            if user not in self.timeout_given:
                self.timeout_given[user] = now
                return {
                    "action": "timeout",
                    "message": self.timeout_message,
                    "duration": self.timeout_duration
                }

            if now - self.timeout_given[user] >= self.cooldown_period:
                self.timeout_given[user] = now
                return {
                    "action": "timeout",
                    "message": self.timeout_message,
                    "duration": self.timeout_duration
                }

            if user in self.special_responses:
                return {"action": "roast", "message": random.choice(self.special_responses[user])}
            else:
                return {"action": "roast", "message": random.choice(self.general_roasts)}

        return {"action": "none"}
