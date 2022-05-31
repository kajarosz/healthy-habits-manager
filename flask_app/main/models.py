import enum
from flask_login import UserMixin
from datetime import datetime
from main import db

class Classification(enum.Enum):
    WATER = 'drink water'
    WALKING = 'go for a walk'
    READING = 'read book'
    SLEEPING = 'hours of sleep'
    EATING = 'eat healthy meals'
    EXERCISE = 'exercise'

class Recurrence(enum.Enum):
    DAILY = 'day'
    WEEKLY = 'week'
    MONTHLY = 'month'

class Frequency(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True, unique=True, nullable=False)
    login = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), unique=False, nullable=False)
    habits = db.relationship('Habit', backref='users', lazy=False)
    actions = db.relationship('Action', backref='users', lazy=False)

    def __str__(self):
        return self.login

class Habit(db.Model):
    __tablename__ = 'habits'
    id = db.Column(db.Integer, primary_key = True, unique=True, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    classification = db.Column(db.Enum(Classification), default=Classification.WATER, nullable=False)
    recurrence = db.Column(db.Enum(Recurrence), default=Recurrence.DAILY, nullable=False)
    frequency = db.Column(db.Enum(Frequency), default=Frequency.ONE, nullable=False)
    reminder = db.Column(db.Boolean, default=False)
    actions = db.relationship('Action', backref='habits', lazy=False)

    def __str__(self):
        return self.classification.name

    def json(self):
        result = {'id': self.id,
        'user': self.user,
        'classification': self.classification.name,
        'recurrence': self.recurrence.name,
        'frequency': self.frequency.name,
        'reminder': self.reminder}
        return result

class Action(db.Model):
    __tablename__ = 'actions'
    id = db.Column(db.Integer, primary_key = True, unique=True, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    habit = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=False), default=datetime.utcnow())

    def __str__(self):
        return f'User {self.user} performed habit: {self.habit}.'
