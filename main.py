import time
import random

        # تم إضافة قائمة المستخدمين الذين تم إلغاء التايم أوت عليهم
        self.no_timeout_users = set()

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
        # إذا كان المستخدم في قائمة المستخدمين الذين تم إلغاء التايم أوت عليهم، يتم الرد مباشرة دون تطبيق التايم أوت
        if user in self.no_timeout_users:
            if user in self.special_responses:
                return {"action": "roast", "message": random.choice(self.special_responses[user])}
            else:
                return {"action": "roast", "message": random.choice(self.general_roasts)}

        now = time.time()

        # زيادة عدد المرات التي ذكر فيها المستخدم
        self.mention_counts[user] = self.mention_counts.get(user, 0) + 1

        # إذا تجاوز الحد المسموح به للمنشن
        if self.mention_counts[user] == self.warning_threshold:
            return {"action": "warn", "message": self.warning_message}

        # إذا تجاوز الحد المسموح للمنشن، يتم تطبيق التايم أوت
        if self.mention_counts[user] >= self.mention_limit:
            if user not in self.timeout_given:
                self.timeout_given[user] = now
                return {
                    "action": "timeout",
                    "message": self.timeout_message,
                    "duration": self.timeout_duration
                }

            # إذا كانت المدة التهدئة انتهت، يتم إزالة التايم أوت
            if now - self.timeout_given[user] >= self.cooldown_period:
                self.timeout_given[user] = now
                self.reset_timeout(user)  # إلغاء التايم أوت بعد فترة التهدئة
                return {
                    "action": "timeout",
                    "message": self.timeout_message,
                    "duration": self.timeout_duration
                }

            # الرد على المستخدم برسائل عشوائية في حال كان لديه ردود خاصة أو لا
            if user in self.special_responses:
                return {"action": "roast", "message": random.choice(self.special_responses[user])}
            else:
                return {"action": "roast", "message": random.choice(self.general_roasts)}

        return {"action": "none"}

    # هذه الدالة تقوم بإلغاء التايم أوت بعد انقضاء فترة التهدئة
    def reset_timeout(self, user):
        self.no_timeout_users.add(user)
from bot.mention_guard import MentionGuard
