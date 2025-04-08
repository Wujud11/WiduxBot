import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

csrf = CSRFProtect()
from forms import MentionSettingsForm, CustomReplyForm, QuestionForm, PraiseTeaseForm, ChannelForm, PointsSettingsForm

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "widuxbot-secret-key")
csrf.init_app(app)

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize JSON files if they don't exist
def initialize_json_files():
    json_files = {
        'data/settings.json': {
            'mention_enabled': True,
            'max_mentions': 5,
            'timeout_duration': 300,
            'warning_threshold': 3,
            'warning_message': 'تنبيه {username}، لقد قمت بعمل {count} منشن من أصل {max_mentions}',
            'timeout_message': '{username} تم إعطاؤك تايم أوت لمدة {timeout} ثانية بسبب استخدام {count} منشن',
            'cooldown_period': 86400
        },
        'data/questions.json': [],
        'data/custom_replies.json': [],
        'data/channels.json': [
            {
                "channel_name": "example",
                "platform": "twitch",
                "is_enabled": True
            }
        ],
        'data/praise_teasing.json': {
            'win_solo': ['أحسنت!', 'رائع!', 'مبدع!'],
            'win_group': ['فريق رائع!', 'تعاون مثالي!'],
            'win_team': ['الفريق الأفضل!', 'قوة جماعية!'],
            'leader_doom_loss': ['حظ أوفر للمرة القادمة!', 'خسارة صعبة!'],
            'leader_lowest_points': ['ستتحسن المرة القادمة!', 'حظ أوفر!'],
            'solo_loser': ['حاول مرة أخرى!', 'لا تيأس!'],
            'team_loser': ['تدربوا أكثر!', 'المرة القادمة لكم!'],
            'points_below_50': ['احتاج للتحسين!', 'جمع نقاط أكثر المرة القادمة!']
        },
        'data/points_settings.json': {
            'quick_answer_points': 10,
            'normal_answer_points': 5,
            'late_answer_points': 0,
            'quick_answer_time': 5,
            'normal_answer_time': 10,
            'streak_enabled': True,
            'streak_threshold': 3,
            'streak_bonus_points': 10,
            'streak_messages': [
                'استمر! أنت على سلسلة إجابات صحيحة!',
                'رائع! سلسلة الإجابات الصحيحة مستمرة!',
                'أنت على نار! سلسلة الإجابات الصحيحة تزداد!'
            ]
        }
    }
    
    for file_path, default_content in json_files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, ensure_ascii=False, indent=4)

initialize_json_files()

# Helper functions for JSON operations
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.logger.error(f"Error loading JSON from {file_path}")
        if 'settings' in file_path:
            return {}
        return []

def save_json(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        app.logger.error(f"Error saving JSON to {file_path}: {str(e)}")
        return False

# Routes
@app.route('/')
def index():
    settings = load_json('data/settings.json')
    custom_replies = load_json('data/custom_replies.json')
    
    mention_form = MentionSettingsForm()
    if settings:
        mention_form.mention_enabled.data = settings.get('mention_enabled', True)
        mention_form.max_mentions.data = settings.get('max_mentions', 5)
        mention_form.timeout_duration.data = settings.get('timeout_duration', 300)
        mention_form.warning_threshold.data = settings.get('warning_threshold', 3)
        mention_form.warning_message.data = settings.get('warning_message', '')
        mention_form.timeout_message.data = settings.get('timeout_message', '')
        mention_form.cooldown_period.data = settings.get('cooldown_period', 86400)
    
    custom_reply_form = CustomReplyForm()
    
    praise_teasing = load_json('data/praise_teasing.json')
    praise_form = PraiseTeaseForm()
    
    if praise_teasing:
        praise_form.win_solo.data = '\n'.join(praise_teasing.get('win_solo', []))
        praise_form.win_group.data = '\n'.join(praise_teasing.get('win_group', []))
        praise_form.win_team.data = '\n'.join(praise_teasing.get('win_team', []))
        praise_form.leader_doom_loss.data = '\n'.join(praise_teasing.get('leader_doom_loss', []))
        praise_form.leader_lowest_points.data = '\n'.join(praise_teasing.get('leader_lowest_points', []))
        praise_form.solo_loser.data = '\n'.join(praise_teasing.get('solo_loser', []))
        praise_form.team_loser.data = '\n'.join(praise_teasing.get('team_loser', []))
        praise_form.points_below_50.data = '\n'.join(praise_teasing.get('points_below_50', []))
    
    return render_template('index.html', 
                           mention_form=mention_form, 
                           custom_reply_form=custom_reply_form,
                           praise_tease_form=praise_form,
                           custom_replies=custom_replies)

@app.route('/questions')
def questions():
    questions_data = load_json('data/questions.json')
    question_form = QuestionForm()
    return render_template('questions.html', questions=questions_data, form=question_form)

@app.route('/save_mention_settings', methods=['POST'])
def save_mention_settings():
    form = MentionSettingsForm(request.form)
    if form.validate():
        # قراءة الإعدادات الحالية للحفاظ على أي إعدادات إضافية
        current_settings = load_json('data/settings.json') or {}
        
        # تحديث الإعدادات بالقيم الجديدة
        current_settings.update({
            'mention_enabled': form.mention_enabled.data,
            'max_mentions': form.max_mentions.data,
            'timeout_duration': form.timeout_duration.data,
            'warning_threshold': form.warning_threshold.data,
            'warning_message': form.warning_message.data,
            'timeout_message': form.timeout_message.data,
            'cooldown_period': form.cooldown_period.data
        })
        
        if save_json('data/settings.json', current_settings):
            flash('تم حفظ إعدادات البوت بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حفظ الإعدادات', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"خطأ في {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('index'))

@app.route('/add_custom_reply', methods=['POST'])
def add_custom_reply():
    form = CustomReplyForm(request.form)
    if form.validate():
        username = form.username.data
        reply = form.reply.data
        
        custom_replies = load_json('data/custom_replies.json')
        custom_replies.append({'username': username, 'reply': reply})
        
        if save_json('data/custom_replies.json', custom_replies):
            flash('تم إضافة الرد المخصص بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حفظ الرد المخصص', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"خطأ في {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('index'))

@app.route('/delete_custom_reply/<int:index>', methods=['POST'])
def delete_custom_reply(index):
    custom_replies = load_json('data/custom_replies.json')
    
    if 0 <= index < len(custom_replies):
        del custom_replies[index]
        
        if save_json('data/custom_replies.json', custom_replies):
            flash('تم حذف الرد المخصص بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حذف الرد المخصص', 'danger')
    else:
        flash('الرد المخصص غير موجود', 'danger')
    
    return redirect(url_for('index'))

@app.route('/add_question', methods=['POST'])
def add_question():
    form = QuestionForm(request.form)
    if form.validate():
        question = {
            'question': form.question.data,
            'correct_answer': form.correct_answer.data,
            'alternative_answers': [ans.strip() for ans in form.alternative_answers.data.split(',') if ans.strip()],
            'category': form.category.data,
            'question_type': form.question_type.data,
            'time_limit': form.time_limit.data
        }
        
        questions = load_json('data/questions.json')
        questions.append(question)
        
        if save_json('data/questions.json', questions):
            flash('تم إضافة السؤال بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حفظ السؤال', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"خطأ في {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('questions'))

@app.route('/edit_question/<int:index>', methods=['POST'])
def edit_question(index):
    form = QuestionForm(request.form)
    if form.validate():
        questions = load_json('data/questions.json')
        
        if 0 <= index < len(questions):
            questions[index] = {
                'question': form.question.data,
                'correct_answer': form.correct_answer.data,
                'alternative_answers': [ans.strip() for ans in form.alternative_answers.data.split(',') if ans.strip()],
                'category': form.category.data,
                'question_type': form.question_type.data,
                'time_limit': form.time_limit.data
            }
            
            if save_json('data/questions.json', questions):
                flash('تم تحديث السؤال بنجاح', 'success')
            else:
                flash('حدث خطأ أثناء تحديث السؤال', 'danger')
        else:
            flash('السؤال غير موجود', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"خطأ في {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('questions'))

@app.route('/delete_question/<int:index>', methods=['POST'])
def delete_question(index):
    questions = load_json('data/questions.json')
    
    if 0 <= index < len(questions):
        del questions[index]
        
        if save_json('data/questions.json', questions):
            flash('تم حذف السؤال بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حذف السؤال', 'danger')
    else:
        flash('السؤال غير موجود', 'danger')
    
    return redirect(url_for('questions'))

@app.route('/upload_questions', methods=['POST'])
def upload_questions():
    try:
        if 'questions_file' not in request.files:
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(url_for('questions'))
        
        file = request.files['questions_file']
        
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(url_for('questions'))
        
        if file and file.filename.endswith('.json'):
            content = file.read()
            if not content:
                flash('الملف فارغ', 'danger')
                return redirect(url_for('questions'))
                
            questions_data = json.loads(content.decode('utf-8'))
            if save_json('data/questions.json', questions_data):
                flash(f'تم استيراد {len(questions_data)} سؤال بنجاح', 'success')
            else:
                flash('حدث خطأ أثناء حفظ الأسئلة', 'danger')
        else:
            flash('يرجى اختيار ملف JSON صحيح', 'danger')
    except json.JSONDecodeError:
        flash('الملف المرفوع ليس بصيغة JSON صحيحة', 'danger')
    except Exception as e:
        flash(f'حدث خطأ أثناء معالجة الملف: {str(e)}', 'danger')
    
    return redirect(url_for('questions'))

@app.route('/save_praise_teasing', methods=['POST'])
def save_praise_teasing():
    form = PraiseTeaseForm(request.form)
    if form.validate():
        praise_teasing = {
            'win_solo': [line.strip() for line in form.win_solo.data.split('\n') if line.strip()],
            'win_group': [line.strip() for line in form.win_group.data.split('\n') if line.strip()],
            'win_team': [line.strip() for line in form.win_team.data.split('\n') if line.strip()],
            'leader_doom_loss': [line.strip() for line in form.leader_doom_loss.data.split('\n') if line.strip()],
            'leader_lowest_points': [line.strip() for line in form.leader_lowest_points.data.split('\n') if line.strip()],
            'solo_loser': [line.strip() for line in form.solo_loser.data.split('\n') if line.strip()],
            'team_loser': [line.strip() for line in form.team_loser.data.split('\n') if line.strip()],
            'points_below_50': [line.strip() for line in form.points_below_50.data.split('\n') if line.strip()]
        }
        
        if save_json('data/praise_teasing.json', praise_teasing):
            flash('تم حفظ ردود المدح والطقطقة بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حفظ ردود المدح والطقطقة', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"خطأ في {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('index'))

@app.route('/upload_praise_teasing', methods=['POST'])
def upload_praise_teasing():
    if 'praise_teasing_file' not in request.files:
        flash('لم يتم تحديد ملف', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['praise_teasing_file']
    
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('index'))
    
    if file:
        try:
            praise_teasing_data = json.loads(file.read().decode('utf-8'))
            if save_json('data/praise_teasing.json', praise_teasing_data):
                flash('تم استيراد ردود المدح والطقطقة بنجاح', 'success')
            else:
                flash('حدث خطأ أثناء حفظ ردود المدح والطقطقة', 'danger')
        except Exception as e:
            flash(f'حدث خطأ أثناء قراءة الملف: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/channels')
def channels():
    channels_data = load_json('data/channels.json')
    channel_form = ChannelForm()
    return render_template('channels.html', channels=channels_data, form=channel_form)

@app.route('/add_channel', methods=['POST'])
def add_channel():
    form = ChannelForm(request.form)
    if form.validate():
        channel = {
            'channel_name': form.channel_name.data,
            'platform': form.platform.data,
            'is_enabled': form.is_enabled.data
        }
        
        channels = load_json('data/channels.json')
        
        # التحقق مما إذا كانت القناة موجودة بالفعل
        exists = False
        for i, existing_channel in enumerate(channels):
            if existing_channel.get('channel_name') == channel['channel_name'] and existing_channel.get('platform') == channel['platform']:
                # تحديث القناة الموجودة
                channels[i] = channel
                exists = True
                break
        
        # إذا لم تكن القناة موجودة، أضفها
        if not exists:
            channels.append(channel)
        
        if save_json('data/channels.json', channels):
            flash('تم حفظ القناة بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حفظ القناة', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"خطأ في {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('channels'))

@app.route('/edit_channel/<int:index>', methods=['POST'])
def edit_channel(index):
    form = ChannelForm(request.form)
    if form.validate():
        channels = load_json('data/channels.json')
        
        if 0 <= index < len(channels):
            channels[index] = {
                'channel_name': form.channel_name.data,
                'platform': form.platform.data,
                'is_enabled': form.is_enabled.data
            }
            
            if save_json('data/channels.json', channels):
                flash('تم تحديث القناة بنجاح', 'success')
            else:
                flash('حدث خطأ أثناء تحديث القناة', 'danger')
        else:
            flash('القناة غير موجودة', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"خطأ في {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('channels'))

@app.route('/delete_channel/<int:index>', methods=['POST'])
def delete_channel(index):
    channels = load_json('data/channels.json')
    
    if 0 <= index < len(channels):
        del channels[index]
        
        if save_json('data/channels.json', channels):
            flash('تم حذف القناة بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حذف القناة', 'danger')
    else:
        flash('القناة غير موجودة', 'danger')
    
    return redirect(url_for('channels'))

@app.route('/toggle_channel/<int:index>', methods=['POST'])
def toggle_channel(index):
    channels = load_json('data/channels.json')
    
    if 0 <= index < len(channels):
        # تبديل حالة التفعيل
        channels[index]['is_enabled'] = not channels[index].get('is_enabled', True)
        
        if save_json('data/channels.json', channels):
            status = 'تفعيل' if channels[index]['is_enabled'] else 'تعطيل'
            flash(f'تم {status} القناة بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء تحديث حالة القناة', 'danger')
    else:
        flash('القناة غير موجودة', 'danger')
    
    return redirect(url_for('channels'))

@app.route('/points_settings')
def points_settings():
    """
    عرض صفحة إعدادات النقاط
    """
    points_data = load_json('data/points_settings.json')
    points_form = PointsSettingsForm()
    
    if points_data:
        points_form.quick_answer_points.data = points_data.get('quick_answer_points', 10)
        points_form.normal_answer_points.data = points_data.get('normal_answer_points', 5)
        points_form.late_answer_points.data = points_data.get('late_answer_points', 0)
        points_form.quick_answer_time.data = points_data.get('quick_answer_time', 5)
        points_form.normal_answer_time.data = points_data.get('normal_answer_time', 10)
        points_form.streak_enabled.data = points_data.get('streak_enabled', True)
        points_form.streak_threshold.data = points_data.get('streak_threshold', 3)
        points_form.streak_bonus_points.data = points_data.get('streak_bonus_points', 10)
        points_form.streak_increase_enabled.data = points_data.get('streak_increase_enabled', False)
        points_form.streak_messages.data = '\n'.join(points_data.get('streak_messages', []))
    
    return render_template('points_settings.html', form=points_form)

@app.route('/save_points_settings', methods=['POST'])
def save_points_settings():
    """
    حفظ إعدادات النقاط
    """
    form = PointsSettingsForm(request.form)
    if form.validate():
        points_settings = {
            'quick_answer_points': form.quick_answer_points.data,
            'normal_answer_points': form.normal_answer_points.data,
            'late_answer_points': form.late_answer_points.data,
            'quick_answer_time': form.quick_answer_time.data,
            'normal_answer_time': form.normal_answer_time.data,
            'streak_enabled': form.streak_enabled.data,
            'streak_threshold': form.streak_threshold.data,
            'streak_bonus_points': form.streak_bonus_points.data,
            'streak_increase_enabled': form.streak_increase_enabled.data,
            'streak_messages': [line.strip() for line in form.streak_messages.data.split('\n') if line.strip()]
        }
        
        if save_json('data/points_settings.json', points_settings):
            flash('تم حفظ إعدادات النقاط بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حفظ إعدادات النقاط', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"خطأ في {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('points_settings'))

@app.route('/start_bot', methods=['POST'])
def start_bot():
    """
    تشغيل البوت في القناة
    """
    try:
        # قراءة القنوات النشطة
        channels = load_json('data/channels.json')
        active_channels = [ch for ch in channels if ch.get('is_enabled', True)]
        
        if not active_channels:
            flash('لا توجد قنوات مفعلة. يرجى إضافة قناة وتفعيلها أولاً.', 'warning')
            return redirect(url_for('channels'))
        
        # تأكد أن توكن تويتش موجود بمتغير البيئة TWITCH_ACCESS_TOKEN
        token = os.environ.get('TWITCH_ACCESS_TOKEN')
        
        if not token:
            flash('لم يتم العثور على توكن تويتش في متغير البيئة TWITCH_ACCESS_TOKEN. يرجى إضافته قبل تشغيل البوت.', 'danger')
            return redirect(url_for('index'))
        
        # تشغيل البوت كعملية منفصلة
        import subprocess
        import sys
        
        # استخدام نفس بيئة Python التي يعمل بها التطبيق الحالي
        python_executable = sys.executable
        
        # تشغيل البوت في الخلفية
        subprocess.Popen([python_executable, "bot.py"])
        
        # إضافة رسالة تأكيد
        channels_names = [ch.get('channel_name', ch.get('channel_id')) for ch in active_channels]
        flash(f'تم تشغيل البوت بنجاح! سيتصل البوت بـ {len(active_channels)} قناة: {", ".join(channels_names)}', 'success')
    except Exception as e:
        app.logger.error(f"Error starting bot: {str(e)}")
        flash(f'حدث خطأ أثناء تشغيل البوت: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
