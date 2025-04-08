from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, TextAreaField, SelectField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange, Optional

class MentionSettingsForm(FlaskForm):
    mention_enabled = BooleanField('حالة البوت')
    max_mentions = IntegerField('عدد المنشنات قبل التايم أوت', 
                               validators=[DataRequired(), NumberRange(min=1, message='يجب أن يكون الرقم أكبر من 0')])
    timeout_duration = IntegerField('مدة التايم أوت (بالثواني)', 
                                   validators=[DataRequired(), NumberRange(min=1, message='يجب أن يكون الرقم أكبر من 0')])
    warning_threshold = IntegerField('عتبة التحذير', 
                                    validators=[DataRequired(), NumberRange(min=1, message='يجب أن يكون الرقم أكبر من 0')])
    warning_message = TextAreaField('رسالة التحذير', validators=[DataRequired()])
    timeout_message = TextAreaField('رسالة التايم أوت', validators=[DataRequired()])
    cooldown_period = IntegerField('فترة التهدئة العامة (بالثواني)', 
                                  validators=[DataRequired(), NumberRange(min=1, message='يجب أن يكون الرقم أكبر من 0')])

    submit = SubmitField('حفظ الإعدادات')

class CustomReplyForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired()])
    reply = TextAreaField('الرد المخصص', validators=[DataRequired()])
    submit = SubmitField('إضافة رد مخصص')

class QuestionForm(FlaskForm):
    question = TextAreaField('السؤال', validators=[DataRequired()])
    correct_answer = StringField('الإجابة الصحيحة', validators=[DataRequired()])
    alternative_answers = TextAreaField('إجابات بديلة (مفصولة بفواصل)', validators=[Optional()])
    category = StringField('التصنيف', validators=[DataRequired()])
    question_type = SelectField('نوع السؤال', choices=[
        ('Normal', 'Normal'),
        ('Golden', 'Golden'),
        ('Steal', 'Steal'),
        ('Sabotage', 'Sabotage'),
        ('Doom', 'Doom'),
        ('The Test of Fate', 'The Test of Fate')
    ], validators=[DataRequired()])
    time_limit = IntegerField('الوقت المخصص للإجابة (بالثواني)', 
                             validators=[DataRequired(), NumberRange(min=1, message='يجب أن يكون الرقم أكبر من 0')])
    submit = SubmitField('إضافة سؤال')

class PraiseTeaseForm(FlaskForm):
    win_solo = TextAreaField('ردود مدح عند الفوز (فردي)', validators=[DataRequired()])
    win_group = TextAreaField('ردود مدح عند الفوز (مجموعة)', validators=[DataRequired()])
    win_team = TextAreaField('ردود مدح عند الفوز (فريق)', validators=[DataRequired()])
    leader_doom_loss = TextAreaField('ردود خاصة لليدر عند خسارة doom', validators=[DataRequired()])
    leader_lowest_points = TextAreaField('ردود خاصة لليدر عند كونه الأقل نقاط', validators=[DataRequired()])
    solo_loser = TextAreaField('ردود طقطقة للفردي الخاسر', validators=[DataRequired()])
    team_loser = TextAreaField('ردود طقطقة للتيم الخاسر', validators=[DataRequired()])
    points_below_50 = TextAreaField('ردود طقطقة لمن جاب نقاط أقل من 50', validators=[DataRequired()])
    submit = SubmitField('حفظ الردود')

class ChannelForm(FlaskForm):
    channel_name = StringField('اسم القناة', validators=[DataRequired()])
    platform = SelectField('المنصة', choices=[
        ('twitch', 'Twitch')
    ], validators=[DataRequired()])
    is_enabled = BooleanField('تفعيل القناة', default=True)
    submit = SubmitField('حفظ القناة')

class PointsSettingsForm(FlaskForm):
    quick_answer_points = IntegerField('نقاط الإجابة السريعة (أقل من ٥ ثوانٍ)', 
                                     validators=[DataRequired(), NumberRange(min=0, message='يجب أن يكون الرقم 0 أو أكبر')])
    normal_answer_points = IntegerField('نقاط الإجابة العادية (٥-١٠ ثوانٍ)', 
                                      validators=[DataRequired(), NumberRange(min=0, message='يجب أن يكون الرقم 0 أو أكبر')])
    late_answer_points = IntegerField('نقاط الإجابة المتأخرة (أكثر من ١٠ ثوانٍ)', 
                                    validators=[NumberRange(min=0, message='يجب أن يكون الرقم 0 أو أكبر')])
    quick_answer_time = IntegerField('الوقت المحدد للإجابة السريعة (بالثواني)', 
                                   validators=[DataRequired(), NumberRange(min=1, message='يجب أن يكون الرقم أكبر من 0')])
    normal_answer_time = IntegerField('الوقت المحدد للإجابة العادية (بالثواني)', 
                                    validators=[DataRequired(), NumberRange(min=1, message='يجب أن يكون الرقم أكبر من 0')])
    streak_enabled = BooleanField('تفعيل نظام السلسلة (الستريك)')
    streak_threshold = IntegerField('عدد الإجابات المتتالية لتفعيل المكافأة', 
                                  validators=[DataRequired(), NumberRange(min=2, message='يجب أن يكون الرقم 2 أو أكبر')])
    streak_bonus_points = IntegerField('نقاط مكافأة السلسلة', 
                                     validators=[DataRequired(), NumberRange(min=1, message='يجب أن يكون الرقم أكبر من 0')])
    streak_increase_enabled = BooleanField('تفعيل نظام مضاعفة المكافأة مع الاستمرار')
    streak_messages = TextAreaField('رسائل مكافأة السلسلة (كل سطر رسالة مختلفة)', validators=[DataRequired()])
    submit = SubmitField('حفظ إعدادات النقاط')
