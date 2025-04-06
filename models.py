import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)  # If the bot is currently active in this channel
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Channel {self.name}>"
    
    def to_dict(self):
        """Convert channel to dictionary format"""
        return {
            'id': self.id,
            'name': self.name,
            'active': self.active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        
class MentionSetting(db.Model):
    """Settings for bot mentions handling"""
    id = db.Column(db.Integer, primary_key=True)
    max_mentions = db.Column(db.Integer, default=3)  # Max mentions before timeout
    timeout_duration = db.Column(db.Integer, default=5)  # Timeout duration in seconds
    timeout_message = db.Column(db.Text, default="ترا انت اصلا مغرم ب البوت ! بس لازم تاكل تايم اوت {timeout} ثواني!")
    warning_message = db.Column(db.Text, default="لاحظت انك تمنشن كثير، هذا منشن {count} من {max_mentions}. شوي شوي علينا!")
    global_cooldown = db.Column(db.Integer, default=86400)  # Time in seconds between timeouts (default: 1 day)
    warning_threshold = db.Column(db.Integer, default=2)  # At which mention count to send warning (default: second mention)
    
    def __repr__(self):
        return f"<MentionSetting max={self.max_mentions}, timeout={self.timeout_duration}s, warning={self.warning_threshold}>"
        
class CustomMentionResponse(db.Model):
    """Custom responses for specific users when they mention the bot"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    response = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CustomMentionResponse for {self.username}>"
        
class UserMentionTracker(db.Model):
    """Track mentions by users for timeout system"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    mention_count = db.Column(db.Integer, default=0)
    last_timeout = db.Column(db.DateTime, nullable=True)
    last_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserMentionTracker {self.username}: {self.mention_count} mentions>"
        
    def increment(self):
        """Increment mention count, return True if threshold reached"""
        self.mention_count += 1
        return self.mention_count
        
    def reset(self):
        """Reset mention count"""
        self.mention_count = 0
        self.last_reset = datetime.utcnow()
        
    def set_timeout(self):
        """Set timeout for user"""
        self.last_timeout = datetime.utcnow()
        
    def can_timeout_again(self, cooldown_seconds):
        """Check if user can be timed out again based on cooldown"""
        if not self.last_timeout:
            return True
        
        cooldown_period = timedelta(seconds=cooldown_seconds)
        return datetime.utcnow() - self.last_timeout > cooldown_period

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    alternative_answers = db.Column(db.Text, nullable=True)  # Stored as comma-separated answers
    category = db.Column(db.String(50), nullable=True)
    difficulty = db.Column(db.String(20), default='normal')  # normal, golden, steal, doom, fate, sabotage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Question {self.id}: {self.question[:30]}...>'
    
    def get_all_valid_answers(self):
        """Return a list of all valid answers (correct and alternatives)"""
        answers = [self.correct_answer]
        
        if self.alternative_answers:
            alt_answers = [ans.strip() for ans in self.alternative_answers.split(',')]
            answers.extend(alt_answers)
            
        return answers
    
    def to_dict(self):
        """Convert question to dictionary format"""
        answers = [self.correct_answer]
        if self.alternative_answers:
            answers.extend([ans.strip() for ans in self.alternative_answers.split(',')])
            
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.correct_answer,
            'choices': answers,
            'category': self.category,
            'difficulty': self.difficulty,
            'active': self.active
        }

def init_app(app):
    db.init_app(app)
    
    # Create all tables
    with app.app_context():
        db.create_all()
        
        # Check if mention settings exist, create default if not
        if MentionSetting.query.count() == 0:
            print("Initializing mention settings with defaults...")
            default_settings = MentionSetting()
            db.session.add(default_settings)
            db.session.commit()
        
        # Check if questions table is empty and populate with initial questions if needed
        if Question.query.count() == 0:
            print("Initializing database with sample questions...")
            populate_initial_questions()

def populate_initial_questions():
    """Populate the database with initial questions from the config file"""
    from config import QUESTIONS
    
    for q_data in QUESTIONS:
        question = Question(
            question=q_data['question'],
            correct_answer=q_data['answer'],
            category='general',
            difficulty='normal'
        )
        db.session.add(question)
    
    db.session.commit()
    print(f"Added {len(QUESTIONS)} initial questions to the database.")