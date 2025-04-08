import json
import random
import os
from datetime import datetime

class QuestionManager:
    """
    مدير الأسئلة للعبة WiduxBot
    يتعامل مع تحميل الأسئلة واختيارها عشوائيًا وفقًا للتصنيف والنوع
    """

    def __init__(self, questions_file_path='data/questions.json', recent_questions_limit=10):
        """
        تهيئة مدير الأسئلة

        :param questions_file_path: مسار ملف الأسئلة (JSON)
        :param recent_questions_limit: عدد الأسئلة التي يتم تجنبها لمنع التكرار
        """
        self.questions_file_path = questions_file_path
        self.questions = []
        # قائمة الأسئلة المستخدمة مؤخراً لتجنب التكرار
        self.recently_used_questions = []
        # عدد الأسئلة التي يتم تجنبها
        self.recent_questions_limit = recent_questions_limit
        self.load_questions()

    def load_questions(self):
        """
        تحميل الأسئلة من ملف JSON
        """
        try:
            if os.path.exists(self.questions_file_path):
                with open(self.questions_file_path, 'r', encoding='utf-8') as f:
                    self.questions = json.load(f)
            else:
                self.questions = []
        except Exception as e:
            print(f"خطأ في تحميل الأسئلة: {str(e)}")
            self.questions = []

    def get_questions_sequence(self, num_normal_questions=5):
        """
        إنشاء تسلسل ثابت للأسئلة يتضمن الأسئلة العادية والخاصة

        :param num_normal_questions: عدد الأسئلة العادية (الحد الأقصى 15)
        :return: قائمة بالأسئلة مرتبة حسب النمط المطلوب
        """
        # التأكد من أن عدد الأسئلة العادية لا يتجاوز 15
        num_normal_questions = min(num_normal_questions, 15)

        # إنشاء قائمة الأسئلة بالترتيب المطلوب
        sequence = []

        # إضافة الأسئلة العادية
        normal_questions = [q for q in self.questions if q.get('question_type') == 'Normal']
        if normal_questions:
            sequence.extend(random.sample(normal_questions, min(num_normal_questions, len(normal_questions))))

        # إضافة الأسئلة الخاصة بالترتيب المطلوب
        special_types = ['Golden', 'Steal', 'Sabotage', 'The Test of Fate', 'Doom']
        for q_type in special_types:
            type_questions = [q for q in self.questions if q.get('question_type') == q_type]
            if type_questions:
                sequence.append(random.choice(type_questions))

        return sequence

    def get_random_question(self, question_type=None, category=None, avoid_recent=True):
        """
        الحصول على سؤال عشوائي بناءً على النوع والتصنيف مع تجنب الأسئلة المستخدمة مؤخراً

        :param question_type: نوع السؤال (Normal, Golden, Steal, الخ)
        :param category: تصنيف السؤال (اختياري)
        :param avoid_recent: ما إذا كان يجب تجنب الأسئلة المستخدمة مؤخراً (افتراضي: نعم)
        :return: السؤال المختار عشوائيًا أو None إذا لم يتم العثور على سؤال مناسب
        """
        filtered_questions = self.questions

        # تصفية حسب النوع إذا تم تحديده
        if question_type:
            filtered_questions = [q for q in filtered_questions if q.get('question_type') == question_type]

        # تصفية حسب التصنيف إذا تم تحديده
        if category:
            filtered_questions = [q for q in filtered_questions if q.get('category') == category]

        # إذا كان هناك طلب لتجنب الأسئلة المستخدمة مؤخراً
        if avoid_recent and self.recently_used_questions:
            # استبعاد الأسئلة المستخدمة مؤخراً من القائمة المصفاة
            # استخدام معرف السؤال أو السؤال نفسه للمقارنة
            filtered_questions = [q for q in filtered_questions if self._question_identifier(q) not in self.recently_used_questions]

        # اختيار سؤال عشوائي من القائمة المصفاة
        if filtered_questions:
            selected_question = random.choice(filtered_questions)

            # إضافة السؤال للقائمة المستخدمة مؤخراً
            self._add_to_recently_used(selected_question)

            return selected_question

        # إذا لم يتم العثور على أسئلة بعد التصفية، حاول مرة أخرى بدون تجنب الأسئلة المستخدمة مؤخراً
        if avoid_recent and not filtered_questions:
            return self.get_random_question(question_type, category, avoid_recent=False)

        return None

    def _question_identifier(self, question):
        """
        إنشاء معرف فريد للسؤال لتتبع الأسئلة المستخدمة مؤخراً

        :param question: السؤال
        :return: معرف فريد للسؤال (يمكن استخدام السؤال نفسه أو معرف فريد آخر)
        """
        # يمكن استخدام السؤال نفسه أو معرف فريد إذا كان موجودًا
        if 'id' in question:
            return question['id']
        # أو استخدام مزيج من السؤال والإجابة الصحيحة كمعرف
        return f"{question.get('question', '')}-{question.get('correct_answer', '')}"

    def handle_doom_question(self, username, message, game_state):
        """
        معالجة سؤال Doom

        :param username: اسم المستخدم
        :param message: الرسالة المستلمة
        :param game_state: حالة اللعبة الحالية
        :return: (النتيجة، الرسالة، معلومات_إضافية)
        """
        # التحقق من أن المستخدم هو ليدر
        if not game_state.get('is_leader', {}).get(username, False):
            return False, "هذا السؤال للقادة فقط!", {}

        # مرحلة القبول
        if game_state.get('doom_phase') == 'acceptance':
            if message.strip() == '1':
                game_state['accepting_leaders'] = game_state.get('accepting_leaders', [])
                game_state['accepting_leaders'].append(username)

                # التحقق مما إذا كان جميع القادة قد قبلوا
                all_leaders = game_state.get('all_leaders', [])
                if len(game_state['accepting_leaders']) == len(all_leaders):
                    return True, "الإجابة في هذه الحالة إجبارية. عند عدم الإجابة، يخسر كلا الفريقين. سيتم أخذ الإجابة الأولى فقط.", {"phase": "mandatory"}

                return True, f"تم قبول التحدي من قبل {username}!", {"phase": "waiting"}

            return False, "تم رفض التحدي.", {"phase": "rejected"}

        # مرحلة الإجابة
        elif game_state.get('doom_phase') == 'answering':
            # التحقق من أن السؤال لم تتم الإجابة عليه بعد
            if game_state.get('doom_answered'):
                return False, "تم الإجابة على السؤال مسبقاً.", {}

            is_correct = self.check_answer(self.current_question, message)
            game_state['doom_answered'] = True
            game_state['doom_answerer'] = username

            if is_correct:
                return True, f"إجابة صحيحة! سيتم مضاعفة نقاط فريق {username}!", {"result": "double"}
            else:
                return False, f"إجابة خاطئة! سيخسر فريق {username} جميع نقاطه!", {"result": "lose_all"}

        return False, "خطأ في مرحلة سؤال Doom.", {}

    def handle_sabotage_question(self, username, message, game_state):
        """معالجة سؤال التخريب"""
        if game_state.get('sabotage_phase') == 'selection':
            mentioned_player = self._extract_mentioned_player(message)
            if not mentioned_player:
                return False, "يرجى منشن لاعب من الفريق المنافس"

            is_valid, message = self._is_valid_sabotage_target(mentioned_player, username, game_state)
            if not is_valid:
                return False, message

            if 'selected_players' not in game_state:
                game_state['selected_players'] = {}
            game_state['selected_players'][username] = mentioned_player

            return True, f"تم اختيار {mentioned_player} للاستبعاد"

        elif game_state.get('sabotage_phase') == 'answering':
            # التحقق من أنه لم يتم استبعاد أحد بعد
            if game_state.get('elimination_done'):
                return True, "تم تنفيذ الاستبعاد مسبقاً"

            is_correct = self.check_answer(self.current_question, message)
            if is_correct:
                eliminated_player = game_state['selected_players'].get(username)
                if eliminated_player:
                    # تعليم أن الاستبعاد تم تنفيذه
                    game_state['elimination_done'] = True
                    return True, self._get_elimination_message(eliminated_player)
                return True, "إجابة صحيحة!"

            return is_correct, "إجابة غير صحيحة"

        return False, "خطأ في مرحلة سؤال التخريب"

    def _extract_mentioned_player(self, message):
        """استخراج اسم اللاعب من المنشن"""
        # يمكن تحسين هذه الدالة حسب تنسيق المنشن في تويتش
        import re
        mention_match = re.search(r'@(\w+)', message)
        return mention_match.group(1) if mention_match else None

    def _is_valid_sabotage_target(self, player, current_player, game_state):
        """التحقق من صحة اختيار اللاعب للاستبعاد في سؤال التخريب"""
        if 'teams' not in game_state:
            return False, "خطأ في حالة الفرق"

        current_team = None
        player_team = None
        is_current_leader = False
        is_target_leader = False

        # البحث عن الفريق والتحقق من حالة القيادة
        for team_name, team_info in game_state['teams'].items():
            members = team_info.get('members', [])
            leader = team_info.get('leader')

            if current_player in members:
                current_team = team_name
                is_current_leader = (current_player == leader)
            if player in members:
                player_team = team_name
                is_target_leader = (player == leader)

        # التحقق من القواعد
        if not (current_team and player_team):
            return False, "خطأ في تحديد الفرق"

        if current_team == player_team:
            return False, "لا يمكن استبعاد لاعب من نفس الفريق"

        if is_current_leader:
            # الليدر لا يمكنه استبعاد الليدر الآخر
            if is_target_leader:
                return False, "لا يمكن للقائد استبعاد القائد الآخر"
            return True, "اختيار صحيح"

        else:
            # اللاعب العادي لا يمكنه استبعاد أي ليدر
            if is_target_leader:
                return False, "لا يمكن للاعب العادي استبعاد القائد"
            return True, "اختيار صحيح"

    def _get_elimination_message(self, player):
        """الحصول على رسالة الاستبعاد"""
        elimination_messages = [
            f"آسف {player}، للأسف تم استبعادك! ولكن لا تحزن، الفرصة في المرة القادمة!",
            f"يا للخسارة {player}! تم استبعادك من اللعبة. استعد للجولة القادمة!",
            f"وداعاً {player}! تم استبعادك، لكن أداءك كان رائعاً!"
        ]
        return random.choice(elimination_messages)

    def _add_to_recently_used(self, question):
        """
        إضافة سؤال إلى قائمة الأسئلة المستخدمة مؤخراً

        :param question: السؤال المستخدم
        """
        # الحصول على معرف السؤال
        question_id = self._question_identifier(question)

        # إضافة معرف السؤال إلى بداية القائمة
        self.recently_used_questions.insert(0, question_id)

        # الاحتفاظ فقط بالعدد المحدد من الأسئلة المستخدمة مؤخراً
        if len(self.recently_used_questions) > self.recent_questions_limit:
            self.recently_used_questions = self.recently_used_questions[:self.recent_questions_limit]

    def reset_recently_used_questions(self):
        """
        إعادة تعيين قائمة الأسئلة المستخدمة مؤخراً
        مفيد عند بدء جولة جديدة
        """
        self.recently_used_questions = []

    def check_answer(self, question, user_answer):
        """
        التحقق من صحة الإجابة

        :param question: السؤال الذي تتم مقارنة الإجابة به
        :param user_answer: إجابة المستخدم
        :return: True إذا كانت الإجابة صحيحة، False إذا كانت خاطئة
        """
        if not question or not user_answer:
            return False

        # تنظيف إجابة المستخدم من المسافات الزائدة وتحويلها للأحرف الصغيرة
        user_answer = user_answer.strip().lower()

        # التحقق من الإجابة الرئيسية
        correct_answer = question.get('correct_answer', '').strip().lower()
        if user_answer == correct_answer:
            return True

        # معالجة إضافية: التحقق إذا كانت الإجابة جزءًا من الإجابة الصحيحة أو العكس
        if user_answer in correct_answer or correct_answer in user_answer:
            similarity_ratio = min(len(user_answer), len(correct_answer)) / max(len(user_answer), len(correct_answer))
            # إذا كان التشابه أكثر من 80%، اعتبرها إجابة صحيحة
            if similarity_ratio > 0.8:
                return True

        # التحقق من الإجابات البديلة بشكل مرن
        alternative_answers = question.get('alternative_answers', [])
        for alt_answer in alternative_answers:
            alt_answer = alt_answer.strip().lower()
            if user_answer == alt_answer:
                return True

            # التحقق من التشابه الجزئي مع الإجابات البديلة
            if user_answer in alt_answer or alt_answer in user_answer:
                similarity_ratio = min(len(user_answer), len(alt_answer)) / max(len(user_answer), len(alt_answer))
                if similarity_ratio > 0.8:
                    return True

        return False

    def get_questions_by_type(self, question_type):
        """
        الحصول على جميع الأسئلة من نوع معين

        :param question_type: نوع السؤال
        :return: قائمة بالأسئلة من النوع المحدد
        """
        return [q for q in self.questions if q.get('question_type') == question_type]

    def get_questions_by_category(self, category):
        """
        الحصول على جميع الأسئلة من تصنيف معين

        :param category: تصنيف السؤال
        :return: قائمة بالأسئلة من التصنيف المحدد
        """
        return [q for q in self.questions if q.get('category') == category]

    def get_available_categories(self):
        """
        الحصول على قائمة بجميع التصنيفات المتاحة

        :return: قائمة بالتصنيفات المتوفرة
        """
        categories = set()
        for question in self.questions:
            category = question.get('category')
            if category:
                categories.add(category)

        return sorted(list(categories))

    def get_available_question_types(self):
        """
        الحصول على قائمة بجميع أنواع الأسئلة المتاحة

        :return: قائمة بأنواع الأسئلة المتوفرة
        """
        question_types = set()
        for question in self.questions:
            q_type = question.get('question_type')
            if q_type:
                question_types.add(q_type)

        return sorted(list(question_types))


class ResponseManager:
    """
    مدير الردود للعبة WiduxBot
    يتعامل مع ردود المدح والطقطقة بناءً على نتائج الإجابة
    """

    def __init__(self, praise_teasing_file_path='data/praise_teasing.json'):
        """
        تهيئة مدير الردود

        :param praise_teasing_file_path: مسار ملف ردود المدح والطقطقة (JSON)
        """
        self.praise_teasing_file_path = praise_teasing_file_path
        self.responses = {}
        self.load_responses()

    def load_responses(self):
        """
        تحميل ردود المدح والطقطقة من ملف JSON
        """
        try:
            if os.path.exists(self.praise_teasing_file_path):
                with open(self.praise_teasing_file_path, 'r', encoding='utf-8') as f:
                    self.responses = json.load(f)
            else:
                self.responses = {}
        except Exception as e:
            print(f"خطأ في تحميل ردود المدح والطقطقة: {str(e)}")
            self.responses = {}

    def get_win_response(self, win_type='solo'):
        """
        الحصول على رد مدح عشوائي بناءً على نوع الفوز

        :param win_type: نوع الفوز (solo, group, team)
        :return: رد مدح عشوائي
        """
        response_key = f'win_{win_type}'
        responses = self.responses.get(response_key, [])

        if responses:
            return random.choice(responses)

        return "أحسنت!"  # رد افتراضي

    def get_leader_response(self, response_type='doom_loss'):
        """
        الحصول على رد خاص لليدر

        :param response_type: نوع الرد (doom_loss, lowest_points)
        :return: رد عشوائي
        """
        response_key = f'leader_{response_type}'
        responses = self.responses.get(response_key, [])

        if responses:
            return random.choice(responses)

        return "حظ أوفر!"  # رد افتراضي

    def get_loser_response(self, loser_type='solo'):
        """
        الحصول على رد طقطقة للخاسر

        :param loser_type: نوع الخاسر (solo, team)
        :return: رد طقطقة عشوائي
        """
        response_key = f'{loser_type}_loser'
        responses = self.responses.get(response_key, [])

        if responses:
            return random.choice(responses)

        return "حاول مرة أخرى!"  # رد افتراضي

    def get_points_below_50_response(self):
        """
        الحصول على رد طقطقة لمن جاب نقاط أقل من 50

        :return: رد طقطقة عشوائي
        """
        responses = self.responses.get('points_below_50', [])

        if responses:
            return random.choice(responses)

        return "حاول تحسين أدائك!"  # رد افتراضي


class PointsManager:
    """
    مدير النقاط والستريك للعبة WiduxBot
    يتعامل مع حساب النقاط وسلسلة الإجابات الصحيحة المتتالية
    """

    def __init__(self, points_settings_file_path='data/points_settings.json'):
        """
        تهيئة مدير النقاط

        :param points_settings_file_path: مسار ملف إعدادات النقاط (JSON)
        """
        self.points_settings_file_path = points_settings_file_path
        self.settings = {}
        self.user_streaks = {}
        self.correct_answers = []  # لتتبع ترتيب الإجابات الصحيحة
        self.team_answers = {}  # لتتبع إجابات الفرق
        self.load_settings()

    def calculate_points(self, is_correct, time_elapsed, username, question_type='Normal', team=None, action=None, is_leader=False):
        """
        حساب النقاط بناءً على نوع السؤال والوقت والفريق

        :param is_correct: هل الإجابة صحيحة
        :param time_elapsed: الوقت المستغرق
        :param username: اسم المستخدم
        :param question_type: نوع السؤال
        :param team: اسم الفريق (اختياري)
        :param action: نوع الإجراء ('زرف' أو 'زود')
        :param is_leader: هل المستخدم هو قائد الفريق
        :return: (النقاط، الرسالة، معلومات_إضافية)
        """
        if not is_correct:
            self.user_streaks[username] = 0
            return 0, "إجابة خاطئة!", {}

        base_points = self._calculate_base_points(time_elapsed)
        extra_info = {}

        # معالجة سؤال السرقة في مختلف الأوضاع
        if self.current_question.get('question_type') == 'Steal':
            if not game_mode:  # وضع فردي
                return base_points, "لا يمكن استخدام سؤال السرقة في الوضع الفردي", {}

            if game_mode == 'challenge':  # وضع التحدي
                if action == 'زرف':
                    # اختيار لاعب عشوائي من المسجلين
                    extra_info['steal_type'] = 'random'
                    return base_points, "تم اختيار لاعب عشوائي لخصم نقاطه", extra_info
                elif action == 'زود':
                    bonus_points = random.randint(0, 30)
                    return base_points + bonus_points, f"إجابة صحيحة! +{bonus_points} نقطة إضافية!", {'bonus': bonus_points}

            elif game_mode == 'team':  # وضع الفريق
                if action == 'زود':
                    bonus_points = random.randint(0, 30)
                    return base_points + bonus_points, f"إجابة صحيحة! +{bonus_points} نقطة إضافية!", {'bonus': bonus_points}
                elif action == 'زرف':
                    # يُسمح لأي لاعب باختيار زرف، لكن التنفيذ يتم من خلال الليدر
                    extra_info['needs_leader_action'] = True
                    extra_info['steal_type'] = 'team'
                    return base_points, "إجابة صحيحة! في انتظار اختيار الليدر للاعب من الفريق المنافس", extra_info
        if not is_correct:
            self.user_streaks[username] = 0
            return 0, "إجابة خاطئة!"

        if question_type == 'Golden':
            return self._calculate_golden_points(username, time_elapsed, team)
        elif question_type == 'Solo':
            return self._calculate_solo_points(username, time_elapsed)
        elif question_type == 'Challenge':
            return self._calculate_challenge_points(username, time_elapsed)

        # للأسئلة العادية
        return self._calculate_normal_points(username, time_elapsed)

    def _calculate_golden_points(self, username, time_elapsed, team=None):
        """حساب نقاط السؤال الذهبي"""
        settings = self.settings.get('golden_question', {})
        time_limit = settings.get('time_limit', 7)

        if time_elapsed > time_limit:
            return 0, "انتهى الوقت!"

        if team:
            # التحقق من إجابات الفريق
            if team not in self.team_answers:
                self.team_answers[team] = []
            self.team_answers[team].append(username)

            # إذا كان أول مجيب من الفريق
            if len(self.team_answers[team]) == 1:
                position = len([ans for ans in self.correct_answers if ans['time'] < time_elapsed])
                if position == 0:
                    self.correct_answers.append({'username': username, 'team': team, 'time': time_elapsed})
                    return settings.get('first_answer_points', 50), "أول إجابة صحيحة! 🌟"
                elif position == 1:
                    self.correct_answers.append({'username': username, 'team': team, 'time': time_elapsed})
                    return settings.get('second_answer_points', 25), "ثاني إجابة صحيحة! ✨"
            return 0, "تم احتساب إجابة زميلك في الفريق"

        # وضع فردي
        position = len(self.correct_answers)
        self.correct_answers.append({'username': username, 'time': time_elapsed})
        if position == 0:
            return settings.get('first_answer_points', 50), "أول إجابة صحيحة! 🌟"
        elif position == 1:
            return settings.get('second_answer_points', 25), "ثاني إجابة صحيحة! ✨"
        return 0, "إجابة صحيحة ولكن متأخرة"

    def _calculate_solo_points(self, username, time_elapsed):
        """حساب نقاط الوضع الفردي"""
        settings = self.settings.get('solo_mode', {})
        if time_elapsed <= settings.get('time_limit', 7):
            return settings.get('quick_answer_points', 50), "إجابة سريعة! 🚀"
        elif time_elapsed <= settings.get('normal_answer_time', 10):
            return settings.get('normal_answer_points', 25), "إجابة جيدة! ✨"
        return settings.get('late_answer_points', 0), "إجابة متأخرة"

    def _calculate_challenge_points(self, username, time_elapsed):
        """حساب نقاط وضع التحدي"""
        settings = self.settings.get('challenge_mode', {})
        if time_elapsed > settings.get('time_limit', 7):
            return 0, "انتهى الوقت!"

        position = len(self.correct_answers)
        self.correct_answers.append({'username': username, 'time': time_elapsed})
        if position == 0:
            return settings.get('first_answer_points', 50), "أول إجابة صحيحة! 🏆"
        elif position == 1:
            return settings.get('second_answer_points', 25), "ثاني إجابة صحيحة! 🥈"
        return 0, "إجابة صحيحة ولكن متأخرة"

    def reset_question(self):
        """إعادة تعيين تتبع الإجابات للسؤال الجديد"""
        self.correct_answers = []
        self.team_answers = {}

    def load_settings(self):
        """
        تحميل إعدادات النقاط من ملف JSON
        """
        try:
            if os.path.exists(self.points_settings_file_path):
                with open(self.points_settings_file_path, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                # إعدادات افتراضية في حالة عدم وجود الملف
                self.settings = {
                    'quick_answer_points': 10,
                    'normal_answer_points': 5,
                    'late_answer_points': 0,
                    'quick_answer_time': 5,
                    'normal_answer_time': 10,
                    'streak_enabled': True,
                    'streak_threshold': 3,
                    'streak_bonus_points': 10,
                    'streak_increase_enabled': False,  # هل تزداد قيمة مكافأة الستريك مع الاستمرار
                    'streak_messages': [
                        'استمر! أنت على سلسلة إجابات صحيحة!',
                        'رائع! سلسلة الإجابات الصحيحة مستمرة!',
                        'أنت على نار! سلسلة الإجابات الصحيحة تزداد!'
                    ]
                }
        except Exception as e:
            print(f"خطأ في تحميل إعدادات النقاط: {str(e)}")
            # إعدادات افتراضية في حالة حدوث خطأ
            self.settings = {
                'quick_answer_points': 10,
                'normal_answer_points': 5,
                'late_answer_points': 0,
                'quick_answer_time': 5,
                'normal_answer_time': 10,
                'streak_enabled': True,
                'streak_threshold': 3,
                'streak_bonus_points': 10,
                'streak_increase_enabled': False,  # هل تزداد قيمة مكافأة الستريك مع الاستمرار
                'streak_messages': [
                    'استمر! أنت على سلسلة إجابات صحيحة!',
                    'رائع! سلسلة الإجابات الصحيحة مستمرة!',
                    'أنت على نار! سلسلة الإجابات الصحيحة تزداد!'
                ]
            }

    def calculate_points(self, is_correct, time_elapsed, username, question_type='Normal'):
        """
        حساب النقاط بناءً على صحة الإجابة ووقت الإجابة ونوع السؤال

        :param is_correct: هل الإجابة صحيحة
        :param time_elapsed: الوقت المستغرق بالثواني
        :param username: اسم المستخدم لتتبع الستريك
        :param question_type: نوع السؤال للتعديلات المحتملة
        :return: (عدد النقاط، رسالة التعليقات، هل هناك ستريك)
        """
        if not is_correct:
            # إعادة تعيين الستريك عند الإجابة الخاطئة
            self.user_streaks[username] = 0
            return 0, "إجابة خاطئة!", False

        # الحصول على إعدادات الوقت
        quick_answer_time = self.settings.get('quick_answer_time', 5)
        normal_answer_time = self.settings.get('normal_answer_time', 10)

        # حساب النقاط بناءً على نوع السؤال
        if question_type == 'Normal':
            # للأسئلة العادية فقط - استخدام إعدادات الوقت والنقاط
            if time_elapsed <= quick_answer_time:
                base_points = self.settings.get('quick_answer_points', 10)
                time_message = f"إجابة سريعة! +{base_points} نقطة"
            elif time_elapsed <= normal_answer_time:
                base_points = self.settings.get('normal_answer_points', 5)
                time_message = f"إجابة جيدة! +{base_points} نقطة"
            else:
                base_points = self.settings.get('late_answer_points', 0)
                time_message = f"إجابة متأخرة! +{base_points} نقطة"
        else:
            # للأسئلة الخاصة - نقاط ثابتة حسب نوع السؤال
            base_points = self._get_special_question_points(question_type)
            time_message = f"نقاط السؤال: +{base_points}"

        # تعديلات بناءً على نوع السؤال (يمكن توسيعها مستقبلاً)
        question_multiplier = 1.0
        if question_type == 'Golden':
            question_multiplier = 2.0  # مضاعفة النقاط للأسئلة الذهبية
        elif question_type == 'Doom':
            question_multiplier = 0.5  # تقليل النقاط للأسئلة الخطيرة

        # تطبيق مضاعف نوع السؤال
        points = int(base_points * question_multiplier)

        # معالجة الستريك (الإجابات المتتالية)
        has_streak = False
        streak_bonus = 0
        streak_message = ""

        if self.settings.get('streak_enabled', True):
            # زيادة سلسلة الإجابات الصحيحة للمستخدم
            current_streak = self.user_streaks.get(username, 0) + 1
            self.user_streaks[username] = current_streak

            streak_threshold = self.settings.get('streak_threshold', 3)

            # التحقق مما إذا كان المستخدم قد وصل إلى الحد الأدنى للستريك
            if current_streak >= streak_threshold:
                # حساب مكافأة الستريك بناءً على الإعدادات
                if self.settings.get('streak_increase_enabled', False):
                    # نظام مضاعفة: كل مستوى جديد يزيد مقدار المكافأة نفسها (10 ثم 20 ثم 30...)
                    streak_level = (current_streak - streak_threshold) // streak_threshold + 1
                    streak_bonus = self.settings.get('streak_bonus_points', 10) * streak_level
                else:
                    # نظام ثابت: كل مستوى يضيف نفس القيمة الثابتة (10 ثم 10+10 ثم 10+10+10...)
                    streak_multiplier = (current_streak - streak_threshold) // streak_threshold + 1
                    streak_bonus = self.settings.get('streak_bonus_points', 10) * streak_multiplier

                # اختيار رسالة ستريك عشوائية
                streak_messages = self.settings.get('streak_messages', ["استمر!"])
                streak_message = random.choice(streak_messages)

                has_streak = True

        # إجمالي النقاط مع مكافأة الستريك
        total_points = points + streak_bonus

        # إنشاء رسالة كاملة
        full_message = time_message
        if has_streak:
            full_message = f"{time_message} + ستريك {streak_bonus} نقطة! {streak_message}"

        return total_points, full_message, has_streak

    def reset_streak(self, username):
        """
        إعادة تعيين سلسلة الإجابات الصحيحة المتتالية للمستخدم

        :param username: اسم المستخدم
        """
        self.user_streaks[username] = 0

    def reset_all_streaks(self):
        """
        إعادة تعيين سلسلة الإجابات الصحيحة لجميع المستخدمين
        """
        self.user_streaks = {}

    def _get_special_question_points(self, question_type):
        """
        تحديد النقاط الثابتة للأسئلة الخاصة

        :param question_type: نوع السؤال
        :return: عدد النقاط المخصصة
        """
        points_map = {
            'Golden': 50,      # السؤال الذهبي
            'Steal': 30,      # سؤال السرقة
            'Sabotage': 25,   # سؤال التخريب
            'The Test of Fate': 40,  # اختبار المصير
            'Doom': 60        # سؤال المصير
        }
        return points_map.get(question_type, 20)  # 20 نقطة كقيمة افتراضية


class GameLogic:
    """
    منطق اللعبة الأساسي لـ WiduxBot
    يجمع بين إدارة الأسئلة والردود والنقاط
    """

    def __init__(self):
        """
        تهيئة منطق اللعبة
        """
        self.question_manager = QuestionManager()
        self.response_manager = ResponseManager()
        self.points_manager = PointsManager()
        self.current_question = None
        self.question_asked_time = None

    def start_game(self):
        """
        بدء اللعبة وتهيئة المديرين
        """
        self.question_manager.load_questions()
        self.response_manager.load_responses()
        self.points_manager.load_settings()

    def ask_random_question(self, question_type=None, category=None):
        """
        اختيار وإرسال سؤال عشوائي

        :param question_type: نوع السؤال (اختياري)
        :param category: تصنيف السؤال (اختياري)
        :return: السؤال المختار وتفاصيله
        """
        self.current_question = self.question_manager.get_random_question(question_type, category)
        self.question_asked_time = datetime.now()

        return self.current_question

    def check_user_answer(self, user_answer, username=None, custom_time_limit=None, time_extension=0):
        """
        التحقق من إجابة المستخدم والوقت المستغرق وحساب النقاط

        :param user_answer: إجابة المستخدم
        :param username: اسم المستخدم (لتتبع الستريك)
        :param custom_time_limit: وقت مخصص للإجابة (اختياري) - يستخدم للتحكم في الوقت من واجهة المستخدم
        :param time_extension: وقت إضافي يمكن إضافته مباشرة (مثلاً كمكافأة) بالثواني
        :return: (نتيجة الإجابة، الوقت المستغرق بالثواني، النقاط، رسالة التعليقات، معلومات إضافية)
        """
        if not self.current_question or not self.question_asked_time:
            return False, 0, 0, "", {}

        # استخدام اسم مستخدم افتراضي إذا لم يتم تقديمه
        username = username or "user"

        # حساب الوقت المستغرق
        time_elapsed = (datetime.now() - self.question_asked_time).total_seconds()

        # التحقق من الوقت المحدد للإجابة
        # استخدام الوقت المخصص من واجهة المستخدم إذا تم تحديده
        base_time_limit = custom_time_limit if custom_time_limit is not None else self.current_question.get('time_limit', 30)

        # إضافة أي وقت إضافي (مكافأة أو تعديل من الواجهة)
        total_time_limit = base_time_limit + time_extension

        # فحص إذا كان الوقت قد انتهى
        if time_elapsed > total_time_limit:
            # نوع خاص من الأسئلة - يمكن خلاله منح فرصة ثانية
            if self.current_question and self.current_question.get('question_type') == 'The Test of Fate':
                # في "اختبار المصير" يمكن أن نكون أكثر تسامحًا مع الوقت
                if time_elapsed <= (total_time_limit * 1.5):  # مثلاً: 50% وقت إضافي
                    is_correct = self.question_manager.check_answer(self.current_question, user_answer)
                    # إذا كانت الإجابة صحيحة، نقبلها رغم تجاوز الوقت الأصلي
                    if is_correct:
                        points, message, has_streak = self.points_manager.calculate_points(
                            is_correct, time_elapsed, username, self.current_question.get('question_type', 'Normal')
                        )
                        return True, time_elapsed, points, message, {"bonus": "fate_test_passed"}

            # إعادة تعيين الستريك للإجابة المتأخرة
            self.points_manager.reset_streak(username)
            return False, time_elapsed, 0, "انتهى الوقت!", {}

        # التحقق من صحة الإجابة إذا لم يتجاوز الوقت
        is_correct = self.question_manager.check_answer(self.current_question, user_answer)

        # حساب النقاط والتحقق من الستريك
        points, message, has_streak = self.points_manager.calculate_points(
            is_correct, time_elapsed, username, self.current_question.get('question_type', 'Normal')
        )

        # معالجة خاصة لأنواع الأسئلة المختلفة
        extra_info = {}
        if self.current_question and is_correct:
            question_type = self.current_question.get('question_type')

            # معالجة خاصة للأسئلة الذهبية - إذا كانت الإجابة صحيحة وسريعة
            if question_type == 'Golden' and time_elapsed <= self.points_manager.settings.get('quick_answer_time', 5):
                extra_info["bonus"] = "golden_quick_answer"

            # إضافة معلومات عن الستريك
            if has_streak:
                extra_info["streak"] = self.points_manager.user_streaks.get(username, 0)

        return is_correct, time_elapsed, points, message, extra_info

    def get_response_for_result(self, is_correct, player_type='solo', is_leader=False, points=None, all_player_points=None):
        """
        الحصول على رد مناسب بناءً على نتيجة الإجابة

        :param is_correct: هل الإجابة صحيحة
        :param player_type: نوع اللاعب (solo, group, team)
        :param is_leader: هل اللاعب هو ليدر
        :param points: عدد النقاط الحالية للاعب (اختياري)
        :param all_player_points: قائمة نقاط جميع اللاعبين للمقارنة (اختياري)
        :return: الرد المناسب
        """
        # تحديد نوع السؤال الحالي لمعالجة أكثر دقة
        question_type = self.current_question.get('question_type', 'Normal') if self.current_question else 'Normal'

        # إجابة صحيحة - إرسال رد المدح حسب نوع اللاعب
        if is_correct:
            # إضافة معالجة خاصة لأنواع الأسئلة المختلفة
            if question_type == 'Golden':
                # رد خاص للأسئلة الذهبية - قد تكون ذات نقاط مضاعفة
                return f"🏆 {self.response_manager.get_win_response(player_type)}"
            elif question_type == 'The Test of Fate':
                # رد خاص للأسئلة المصيرية
                return f"✨ {self.response_manager.get_win_response(player_type)}"
            else:
                # رد عادي للأسئلة العادية
                return self.response_manager.get_win_response(player_type)

        # في حالة الإجابة الخاطئة - تحديد نوع الرد حسب عدة عوامل

        # حالة خاصة للقائد عند خسارة سؤال Doom
        if is_leader and question_type == 'Doom':
            return self.response_manager.get_leader_response('doom_loss')

        # حالة خاصة للقائد عندما يكون الأقل نقاطًا
        if is_leader and all_player_points and points is not None:
            if points == min(all_player_points):
                return self.response_manager.get_leader_response('lowest_points')

        # حالة خاصة لأسئلة Steal و Sabotage
        if question_type == 'Steal':
            return f"للأسف فقدت فرصة سرقة النقاط! {self.response_manager.get_loser_response(player_type)}"

        if question_type == 'Sabotage':
            return f"محاولة التخريب فشلت! {self.response_manager.get_loser_response(player_type)}"

        # حالة عندما تكون النقاط أقل من 50
        if points is not None and points < 50:
            return self.response_manager.get_points_below_50_response()

        # الحالة العامة للخاسر
        return self.response_manager.get_loser_response(player_type)

# استخدام المثال:
"""
# إنشاء كائن منطق اللعبة
game = GameLogic()
game.start_game()

# ==== مثال للاستخدام الأساسي ====
print("\n= مثال للاستخدام الأساسي =")
# طلب سؤال عشوائي من نوع معين
question = game.ask_random_question(question_type='Normal')
if question:
    print(f"السؤال: {question['question']}")
    print(f"الوقت المحدد للإجابة: {question['time_limit']} ثانية")

    # في حالة تلقي إجابة من المستخدم
    user_answer = "الإجابة المفترضة"
    # يمكن تحديد وقت مخصص من واجهة المستخدم
    custom_time_limit = 45  # مثال: 45 ثانية
    result = game.check_user_answer(user_answer, custom_time_limit)

    # التعامل مع النتيجة
    if len(result) == 3:  # حالة وجود مكافأة
        is_correct, time_elapsed, bonus_info = result
        print(f"مكافأة! {bonus_info['bonus']}")
    else:
        is_correct, time_elapsed = result

    if is_correct:
        print(f"إجابة صحيحة! استغرقت {time_elapsed:.2f} ثانية")
        # يمكن تمرير معلومات إضافية مثل نوع اللاعب وحالة اللاعب ونقاط جميع اللاعبين
        response = game.get_response_for_result(
            is_correct=True,
            player_type='team',  # أو 'solo' أو 'group'
            is_leader=True,  # إذا كان اللاعب هو القائد
            points=75,  # نقاط اللاعب الحالية
            all_player_points=[60, 75, 80, 90]  # نقاط جميع اللاعبين للمقارنة
        )
        print(f"رد البوت: {response}")
    else:
        print(f"إجابة خاطئة! استغرقت {time_elapsed:.2f} ثانية")
        response = game.get_response_for_result(False, player_type='solo')
        print(f"رد البوت: {response}")

# ==== مثال لتجنب تكرار الأسئلة ====
print("\n= مثال لتجنب تكرار الأسئلة =")
# تجنب تكرار الأسئلة - سيتم تخزين الأسئلة المستخدمة مؤخرًا
for i in range(5):
    question = game.ask_random_question(question_type='Normal')
    print(f"السؤال {i+1}: {question['question']}")
    # لن يتم تكرار السؤال حتى استخدام جميع الأسئلة المتاحة

# يمكن إعادة تعيين قائمة الأسئلة المستخدمة مؤخرًا
game.question_manager.reset_recently_used_questions()
print("تم إعادة تعيين قائمة الأسئلة المستخدمة مؤخرًا")

# ==== مثال للتعامل مع أنواع الأسئلة المختلفة ====
print("\n= مثال للتعامل مع أنواع الأسئلة المختلفة =")
# أمثلة لأنواع الأسئلة المختلفة
normal_question = game.ask_random_question(question_type='Normal')
print(f"سؤال عادي: {normal_question['question'] if normal_question else 'لا يوجد'}")

golden_question = game.ask_random_question(question_type='Golden')
print(f"سؤال ذهبي: {golden_question['question'] if golden_question else 'لا يوجد'}")

steal_question = game.ask_random_question(question_type='Steal')
print(f"سؤال سرقة: {steal_question['question'] if steal_question else 'لا يوجد'}")

sabotage_question = game.ask_random_question(question_type='Sabotage')
print(f"سؤال تخريب: {sabotage_question['question'] if sabotage_question else 'لا يوجد'}")

doom_question = game.ask_random_question(question_type='Doom')
print(f"سؤال مصير: {doom_question['question'] if doom_question else 'لا يوجد'}")

fate_question = game.ask_random_question(question_type='The Test of Fate')
print(f"اختبار المصير: {fate_question['question'] if fate_question else 'لا يوجد'}")

# ==== مثال للتعامل مع الوقت والمكافآت ====
print("\n= مثال للتعامل مع الوقت والمكافآت =")
# طلب سؤال ذهبي وفحص المكافأة
golden_q = game.ask_random_question(question_type='Golden')
if golden_q:
    print(f"سؤال ذهبي: {golden_q['question']}")
    # إجابة سريعة (أقل من نصف الوقت)
    result = game.check_user_answer("إجابة صحيحة", time_elapsed=golden_q['time_limit'] / 3)
    if len(result) == 3:
        # حصلنا على مكافأة للإجابة السريعة
        is_correct, time_elapsed, bonus = result
        print(f"مكافأة! {bonus['bonus']} - الإجابة صحيحة في {time_elapsed:.2f} ثانية")

# طلب سؤال "اختبار المصير" للتعامل مع الوقت الإضافي
fate_q = game.ask_random_question(question_type='The Test of Fate')
if fate_q:
    print(f"اختبار المصير: {fate_q['question']}")
    # إجابة متأخرة (الوقت الأصلي + 20%)
    time_limit = fate_q['time_limit']
    result = game.check_user_answer("إجابة صحيحة", time_elapsed=time_limit * 1.2)
    is_correct, time_elapsed = result[:2]
    print(f"نتيجة الاختبار المصيري (متأخرة): {'ناجح' if is_correct else 'فاشل'} - الوقت: {time_elapsed:.2f} ثانية")

# ==== مثال للأسئلة حسب التصنيف ====
print("\n= مثال للأسئلة حسب التصنيف =")
# يمكن أيضًا اختيار أسئلة بناءً على التصنيف
history_question = game.ask_random_question(category='History')
print(f"سؤال تاريخي: {history_question['question'] if history_question else 'لا يوجد'}")

science_question = game.ask_random_question(category='Science')
print(f"سؤال علمي: {science_question['question'] if science_question else 'لا يوجد'}")

# يمكن الجمع بين النوع والتصنيف
golden_history_question = game.ask_random_question(question_type='Golden', category='History')
print(f"سؤال ذهبي تاريخي: {golden_history_question['question'] if golden_history_question else 'لا يوجد'}")
"""