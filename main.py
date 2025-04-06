import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import threading
from bot import TriviaBot
import models
from models import db, Question, Channel
import config

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
models.init_app(app)

# Create a global variable for the bot instance
bot_instance = None

# Function to run the Twitch bot
def run_bot():
    global bot_instance
    # Check if we have the required Twitch credentials
    if not os.environ.get('TWITCH_OAUTH_TOKEN') or not os.environ.get('TWITCH_CLIENT_ID'):
        print("Missing Twitch credentials. Bot will not start.")
        return None
        
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot_instance = TriviaBot()
        bot_instance.run()
        return bot_instance
    except Exception as e:
        print(f"Error starting bot: {e}")
        return None

# Start the bot in a separate thread
def start_bot():
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    return bot_thread

# Route for the home page
@app.route('/')
def home():
    global bot_instance
    
    # Check for required Twitch credentials
    has_credentials = bool(os.environ.get('TWITCH_OAUTH_TOKEN')) and bool(os.environ.get('TWITCH_CLIENT_ID'))
    bot_status = "configured" if has_credentials else "not_configured"
    
    # Start the bot if it's not running yet and we have credentials
    if bot_instance is None and has_credentials:
        start_bot()
    
    twitch_client_id = os.environ.get('TWITCH_CLIENT_ID', '')
    redirect_uri = request.url_root
    
    return render_template('index.html', 
                           client_id=twitch_client_id, 
                           redirect_uri=redirect_uri,
                           bot_status=bot_status)

@app.route('/add-bot-to-channel', methods=['POST'])
def add_bot_to_channel():
    channel_name = request.form.get('channel_name', '').strip().lower()
    
    if not channel_name:
        flash('يرجى إدخال اسم القناة', 'danger')
        return redirect(url_for('home'))
    
    try:
        global bot_instance
        # Check if bot is running
        if bot_instance is None:
            start_bot()
            # Small delay to allow bot to initialize
            import time
            time.sleep(1)
        
        # Check if the channel already exists in the database
        channel = Channel.query.filter_by(name=channel_name).first()
        
        if not channel:
            # Add to database
            channel = Channel(name=channel_name, active=True)
            db.session.add(channel)
            db.session.commit()
        elif not channel.active:
            # Reactivate the channel
            channel.active = True
            db.session.commit()
        
        # Add the bot to the channel
        if bot_instance and hasattr(bot_instance, 'join_channels'):
            # Use the join_channels method if it exists
            bot_instance.join_channels([channel_name])
            flash(f'تمت إضافة البوت إلى قناة {channel_name} بنجاح', 'success')
        else:
            flash('لم يتمكن البوت من الانضمام إلى القناة. يرجى المحاولة مرة أخرى لاحقًا.', 'warning')
    except Exception as e:
        flash(f'حدث خطأ أثناء إضافة البوت: {str(e)}', 'danger')
    
    return redirect(url_for('home'))

@app.route('/channels')
def manage_channels():
    channels = Channel.query.order_by(Channel.created_at.desc()).all()
    return render_template('channels.html', channels=channels)

@app.route('/channels/<int:id>/toggle', methods=['POST'])
def toggle_channel(id):
    channel = Channel.query.get_or_404(id)
    channel.active = not channel.active
    db.session.commit()
    
    # If reactivating, try to join the channel
    if channel.active:
        try:
            global bot_instance
            if bot_instance and hasattr(bot_instance, 'join_channels'):
                bot_instance.join_channels([channel.name])
        except Exception as e:
            flash(f'تم تفعيل القناة ولكن حدث خطأ أثناء الانضمام: {str(e)}', 'warning')
    
    flash(f'تم {"تفعيل" if channel.active else "إيقاف"} القناة {channel.name} بنجاح', 'success')
    return redirect(url_for('manage_channels'))

@app.route('/channels/<int:id>/delete', methods=['POST'])
def delete_channel(id):
    channel = Channel.query.get_or_404(id)
    channel_name = channel.name
    db.session.delete(channel)
    db.session.commit()
    
    flash(f'تم حذف القناة {channel_name} بنجاح', 'success')
    return redirect(url_for('manage_channels'))

# Routes for question management
@app.route('/questions')
def manage_questions():
    categories = db.session.query(Question.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    questions = Question.query.order_by(Question.id).all()
    return render_template('questions.html', questions=questions, categories=categories)

@app.route('/questions/new', methods=['GET', 'POST'])
def new_question():
    if request.method == 'POST':
        question_text = request.form.get('question')
        correct_answer = request.form.get('correct_answer')
        alternative_answers = request.form.get('alternative_answers')
        category = request.form.get('category')
        difficulty = request.form.get('difficulty', 'normal')
        
        if not question_text or not correct_answer:
            flash('السؤال والإجابة الصحيحة مطلوبة', 'danger')
            return redirect(url_for('new_question'))
        
        question = Question(
            question=question_text,
            correct_answer=correct_answer,
            alternative_answers=alternative_answers,
            category=category,
            difficulty=difficulty
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('تمت إضافة السؤال بنجاح', 'success')
        return redirect(url_for('manage_questions'))
    
    categories = db.session.query(Question.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('question_form.html', question=None, categories=categories)

@app.route('/questions/<int:id>/edit', methods=['GET', 'POST'])
def edit_question(id):
    question = Question.query.get_or_404(id)
    
    if request.method == 'POST':
        question.question = request.form.get('question')
        question.correct_answer = request.form.get('correct_answer')
        question.alternative_answers = request.form.get('alternative_answers')
        question.category = request.form.get('category')
        question.difficulty = request.form.get('difficulty', 'normal')
        
        db.session.commit()
        
        flash('تم تحديث السؤال بنجاح', 'success')
        return redirect(url_for('manage_questions'))
    
    categories = db.session.query(Question.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('question_form.html', question=question, categories=categories)

@app.route('/questions/<int:id>/delete', methods=['POST'])
def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    
    flash('تم حذف السؤال بنجاح', 'success')
    return redirect(url_for('manage_questions'))

@app.route('/load-sample-questions', methods=['POST'])
def load_sample_questions():
    try:
        from load_questions import load_user_questions
        load_user_questions()
        flash('تم تحميل الأسئلة بنجاح', 'success')
    except Exception as e:
        flash(f'حدث خطأ أثناء تحميل الأسئلة: {str(e)}', 'danger')
    
    return redirect(url_for('manage_questions'))

@app.route('/import-questions', methods=['GET', 'POST'])
def import_questions():
    if request.method == 'POST':
        questions_text = request.form.get('questions_text', '')
        category = request.form.get('category', '')
        new_category = request.form.get('new_category', '')
        difficulty = request.form.get('difficulty', 'normal')
        
        # Use the new category if provided
        if new_category:
            category = new_category
        
        # Parse the questions from the text
        questions_added = 0
        questions_failed = 0
        
        for line in questions_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            try:
                # Split question and answers
                parts = line.split('|')
                if len(parts) != 2:
                    questions_failed += 1
                    continue
                    
                question_text = parts[0].strip()
                answers = parts[1].strip()
                
                # Split answers by comma
                answer_list = [a.strip() for a in answers.split(',')]
                
                if not answer_list:
                    questions_failed += 1
                    continue
                    
                # First answer is the correct one
                correct_answer = answer_list[0]
                alternative_answers = None
                
                # If there are alternative answers
                if len(answer_list) > 1:
                    alternative_answers = ','.join(answer_list[1:])
                
                # Create the question
                question = Question(
                    question=question_text,
                    correct_answer=correct_answer,
                    alternative_answers=alternative_answers,
                    category=category,
                    difficulty=difficulty
                )
                
                db.session.add(question)
                questions_added += 1
                
            except Exception as e:
                print(f"Error importing question: {e}")
                questions_failed += 1
        
        # Commit all the questions
        db.session.commit()
        
        if questions_added > 0:
            flash(f'تم استيراد {questions_added} سؤال بنجاح. {questions_failed} سؤال فشل.', 'success')
        else:
            flash(f'لم يتم استيراد أي سؤال. تحقق من تنسيق النص.', 'danger')
            
        return redirect(url_for('manage_questions'))
    
    categories = db.session.query(Question.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('import_questions.html', categories=categories)

# Route for bot setup
@app.route('/bot-setup', methods=['GET', 'POST'])
def bot_setup():
    from models import MentionSetting, CustomMentionResponse
    
    # Get current bot settings
    current_settings = {
        'token': os.environ.get('TWITCH_OAUTH_TOKEN', ''),
        'client_id': os.environ.get('TWITCH_CLIENT_ID', ''),
        'channel': os.environ.get('TWITCH_CHANNEL', '')
    }
    
    # Get mention settings
    mention_settings = MentionSetting.query.first()
    if not mention_settings:
        mention_settings = MentionSetting()
        db.session.add(mention_settings)
        db.session.commit()
    
    # Get custom responses
    custom_responses = CustomMentionResponse.query.all()
    
    return render_template(
        'bot_setup.html', 
        current_settings=current_settings,
        mention_settings=mention_settings,
        custom_responses=custom_responses
    )

@app.route('/save-bot-settings', methods=['POST'])
def save_bot_settings():
    from models import MentionSetting, CustomMentionResponse
    
    # Get base twitch settings
    token = request.form.get('twitch_token', '').strip()
    client_id = request.form.get('twitch_client_id', '').strip()
    channel = request.form.get('twitch_channel', '').strip()
    
    # Get mention settings
    max_mentions = request.form.get('max_mentions', '3').strip()
    timeout_duration = request.form.get('timeout_duration', '5').strip()
    timeout_message = request.form.get('timeout_message', 'تم إعطاؤك تايم أوت {timeout} ثواني لكثرة المنشنات!').strip()
    global_cooldown = request.form.get('global_cooldown', '86400').strip()
    
    # Update mention settings
    settings = MentionSetting.query.first()
    if not settings:
        settings = MentionSetting()
        db.session.add(settings)
    
    settings.max_mentions = int(max_mentions)
    settings.timeout_duration = int(timeout_duration)
    settings.timeout_message = timeout_message
    settings.global_cooldown = int(global_cooldown)
    
    # Save settings
    db.session.commit()
    
    # Handle custom response operations
    if 'add_custom_response' in request.form:
        username = request.form.get('new_username', '').strip().lower()
        response = request.form.get('new_response', '').strip()
        
        if username and response:
            # Check if already exists
            existing = CustomMentionResponse.query.filter_by(username=username).first()
            if existing:
                existing.response = response
                existing.active = True
            else:
                custom = CustomMentionResponse(username=username, response=response)
                db.session.add(custom)
            
            db.session.commit()
            flash(f'تم إضافة/تحديث رد مخصص للمستخدم: {username}', 'success')
        else:
            flash('يرجى تعبئة اسم المستخدم والرد المخصص', 'danger')
    
    # Process delete/toggle operations if any
    for key in request.form:
        if key.startswith('delete_response_'):
            response_id = key.split('_')[2]
            resp = CustomMentionResponse.query.get(response_id)
            if resp:
                db.session.delete(resp)
                db.session.commit()
                flash(f'تم حذف الرد المخصص للمستخدم: {resp.username}', 'success')
        
        elif key.startswith('toggle_response_'):
            response_id = key.split('_')[2]
            resp = CustomMentionResponse.query.get(response_id)
            if resp:
                resp.active = not resp.active
                db.session.commit()
                status = 'تفعيل' if resp.active else 'تعطيل'
                flash(f'تم {status} الرد المخصص للمستخدم: {resp.username}', 'success')
    
    # This is just a message since in Replit we can't directly modify environment variables
    # from within the application. User needs to set these manually.
    if token and client_id:
        flash('تم تسجيل الإعدادات. لتفعيل هذه الإعدادات، يجب عليك تعيين المتغيرات البيئية التالية في لوحة تحكم Replit أو Render:', 'info')
        flash(f'TWITCH_OAUTH_TOKEN: {token[:5]}...', 'info')
        flash(f'TWITCH_CLIENT_ID: {client_id[:5]}...', 'info')
        if channel:
            flash(f'TWITCH_CHANNEL: {channel}', 'info')
    else:
        flash('يرجى تعبئة TWITCH_OAUTH_TOKEN و TWITCH_CLIENT_ID على الأقل', 'danger')
    
    return redirect(url_for('bot_setup'))

# Manage mention settings
@app.route('/mention-settings', methods=['GET', 'POST'])
def mention_settings():
    from models import MentionSetting, CustomMentionResponse
    
    # Get mention settings
    current_settings = MentionSetting.query.first()
    if not current_settings:
        print("Initializing mention settings with defaults...")
        current_settings = MentionSetting()
        db.session.add(current_settings)
        db.session.commit()
    
    # Get custom responses
    custom_responses = CustomMentionResponse.query.all()
    
    return render_template(
        'mention_settings.html', 
        current_settings=current_settings,
        custom_responses=custom_responses
    )

@app.route('/save-mention-settings', methods=['POST'])
def save_mention_settings():
    from models import MentionSetting, CustomMentionResponse
    
    # Get mention settings
    max_mentions = request.form.get('max_mentions', '3').strip()
    timeout_duration = request.form.get('timeout_duration', '5').strip()
    timeout_message = request.form.get('timeout_message', 'ترا انت اصلا مغرم ب البوت ! بس لازم تاكل تايم اوت {timeout} ثواني!').strip()
    warning_message = request.form.get('warning_message', 'لاحظت انك تمنشن كثير، هذا منشن {count} من {max_mentions}. شوي شوي علينا!').strip()
    warning_threshold = request.form.get('warning_threshold', '2').strip()
    global_cooldown = request.form.get('global_cooldown', '86400').strip()
    
    # Update mention settings
    settings = MentionSetting.query.first()
    if not settings:
        settings = MentionSetting()
        db.session.add(settings)
    
    settings.max_mentions = int(max_mentions)
    settings.timeout_duration = int(timeout_duration)
    settings.timeout_message = timeout_message
    settings.warning_message = warning_message
    settings.warning_threshold = int(warning_threshold)
    settings.global_cooldown = int(global_cooldown)
    
    # Save settings
    db.session.commit()
    
    # Handle custom response operations
    if 'add_custom_response' in request.form:
        username = request.form.get('new_username', '').strip().lower()
        response = request.form.get('new_response', '').strip()
        
        if username and response:
            # Check if already exists
            existing = CustomMentionResponse.query.filter_by(username=username).first()
            if existing:
                existing.response = response
                existing.active = True
            else:
                custom = CustomMentionResponse(username=username, response=response)
                db.session.add(custom)
            
            db.session.commit()
            flash(f'تم إضافة/تحديث رد مخصص للمستخدم: {username}', 'success')
        else:
            flash('يرجى تعبئة اسم المستخدم والرد المخصص', 'danger')
    
    # Process delete/toggle operations if any
    for key in request.form:
        if key.startswith('delete_response_'):
            response_id = key.split('_')[2]
            resp = CustomMentionResponse.query.get(response_id)
            if resp:
                db.session.delete(resp)
                db.session.commit()
                flash(f'تم حذف الرد المخصص للمستخدم: {resp.username}', 'success')
        
        elif key.startswith('toggle_response_'):
            response_id = key.split('_')[2]
            resp = CustomMentionResponse.query.get(response_id)
            if resp:
                resp.active = not resp.active
                db.session.commit()
                status = 'تفعيل' if resp.active else 'تعطيل'
                flash(f'تم {status} الرد المخصص للمستخدم: {resp.username}', 'success')
    
    flash('تم حفظ إعدادات المنشن بنجاح!', 'success')
    return redirect(url_for('mention_settings'))

# Add custom mention response
@app.route('/add-custom-response', methods=['POST'])
def add_custom_response():
    from models import CustomMentionResponse
    
    username = request.form.get('username', '').strip().lower()
    response = request.form.get('response', '').strip()
    
    if username and response:
        # Check if already exists
        existing = CustomMentionResponse.query.filter_by(username=username).first()
        if existing:
            existing.response = response
            existing.active = True
        else:
            custom = CustomMentionResponse(username=username, response=response)
            db.session.add(custom)
        
        db.session.commit()
        flash(f'تم إضافة/تحديث رد مخصص للمستخدم: {username}', 'success')
    else:
        flash('يرجى تعبئة اسم المستخدم والرد المخصص', 'danger')
    
    return redirect(url_for('mention_settings'))

# Toggle custom mention response status
@app.route('/toggle-custom-response/<int:id>')
def toggle_custom_response(id):
    from models import CustomMentionResponse
    
    response = CustomMentionResponse.query.get_or_404(id)
    response.active = not response.active
    db.session.commit()
    
    status = 'تفعيل' if response.active else 'تعطيل'
    flash(f'تم {status} الرد المخصص للمستخدم: {response.username}', 'success')
    return redirect(url_for('mention_settings'))

# Delete custom mention response
@app.route('/delete-custom-response/<int:id>')
def delete_custom_response(id):
    from models import CustomMentionResponse
    
    response = CustomMentionResponse.query.get_or_404(id)
    username = response.username
    db.session.delete(response)
    db.session.commit()
    
    flash(f'تم حذف الرد المخصص للمستخدم: {username}', 'success')
    return redirect(url_for('mention_settings'))

# Create an error handler for 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('error.html'), 500

if __name__ == '__main__':
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
