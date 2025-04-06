import datetime
from app import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

class Channel(db.Model):
    """Model representing a Twitch channel where the bot is active"""
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    game_sessions = relationship("GameSession", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Channel {self.name}>"

class Question(db.Model):
    """Model representing a trivia question"""
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    answers = Column(Text, nullable=False)  # Comma-separated list of acceptable answers
    category = Column(String(50), default='general')
    difficulty = Column(Integer, default=2)  # 1=easy, 2=medium, 3=hard
    question_type = Column(String(20), default='normal')  # normal, golden, steal, doom, sabotage, fate
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Question {self.id}: {self.text[:30]}...>"

    def check_answer(self, answer):
        """Check if the provided answer matches any of the correct answers"""
        if not answer:
            return False

        # Convert both answer and stored answers to lowercase and strip whitespace
        user_answer = answer.strip().lower()
        correct_answers = [ans.strip().lower() for ans in self.answers.split(',')]

        return user_answer in correct_answers

class GameSession(db.Model):
    """Model representing a game session"""
    __tablename__ = 'game_sessions'

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=False)
    mode = Column(String(20), nullable=False)  # فردي، تحدي، تيم
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    channel = relationship("Channel", back_populates="game_sessions")
    players = relationship("Player", back_populates="game_session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<GameSession {self.id} - {self.mode} in {self.channel.name}>"

class Player(db.Model):
    """Model representing a player in a game session"""
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('game_sessions.id'), nullable=False)
    username = Column(String(50), nullable=False)
    team = Column(String(20), nullable=True)  # أحمر، أزرق
    is_leader = Column(Boolean, default=False)
    score = Column(Integer, default=0)
    consecutive_correct = Column(Integer, default=0)  # For tracking consecutive correct answers
    is_eliminated = Column(Boolean, default=False)  # For players eliminated from the game via sabotage

    # Relationships
    game_session = relationship("GameSession", back_populates="players")

    def __repr__(self):
        return f"<Player {self.username} - Score: {self.score}>"

class FunnyResponse(db.Model):
    """Model for storing funny responses for low-scoring players/teams"""
    __tablename__ = 'funny_responses'

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    min_score = Column(Integer, default=0)
    max_score = Column(Integer, default=50)
    is_team_response = Column(Boolean, default=False)  # Whether this is for teams or individual players
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<FunnyResponse {self.id}: {self.text[:30]}...>"

class PraiseResponse(db.Model):
    """Model for storing praise responses for winning players/teams"""
    __tablename__ = 'praise_responses'

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    min_score = Column(Integer, default=80)  # Minimum score to trigger this response
    game_mode = Column(String(20), default='all')  # all, solo, group, team
    is_team_response = Column(Boolean, default=False)  # Whether this is for teams or individual players
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<PraiseResponse {self.id}: {self.text[:30]}...>"

class EliminationMessage(db.Model):
    """Model for storing humorous messages sent when a player is eliminated"""
    __tablename__ = 'elimination_messages'

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<EliminationMessage {self.id}: {self.text[:30]}...>"