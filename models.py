from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app import db

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default="عام")
    question_type = db.Column(db.String(20), default="normal")
    difficulty = db.Column(db.Integer, default=1)  # 1: سهل، 2: متوسط، 3: صعب
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    times_asked = db.Column(db.Integer, default=0)
    times_answered_correctly = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.text[:30]}...>'

class FunnyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    min_score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=50)
    is_team_response = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FunnyResponse {self.id}: {self.text[:30]}...>'

class GameStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(100), nullable=False)
    game_mode = db.Column(db.String(20), nullable=False)
    player_count = db.Column(db.Integer, default=0)
    questions_asked = db.Column(db.Integer, default=0)
    highest_score = db.Column(db.Integer, default=0)
    winner_name = db.Column(db.String(100))
    date_played = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GameStats {self.id}: {self.channel} - {self.game_mode}>'

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    games_played = db.Column(db.Integer, default=0)
    last_game = db.Column(db.DateTime)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Channel {self.name}>'

class PraiseResponse(db.Model):
    """ردود المدح والثناء للفائزين"""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    min_score = db.Column(db.Integer, default=80)  # النقاط الأدنى للفوز
    game_mode = db.Column(db.String(20), default="all")  # all, solo, group, team
    is_team_response = db.Column(db.Boolean, default=False)  # هل هو رد للفريق
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PraiseResponse {self.id}: {self.text[:30]}...>'