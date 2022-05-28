from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()


class Category(enum.Enum):
    WATER = 'drink water'
    WALKING = 'go for a walk'
    READING = 'read book'
    SLEEPING = 'hours of sleep'
    EATING = 'eat healthy meals'
    EXERCISE = 'exercise'

class Interval(enum.Enum):
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'

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

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True, unique=True, nullable=False)
    login = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), unique=False, nullable=False)
    #habits = db.relationship('Habit', secondary=habits, lazy='subquery', backref=db.backref('users', lazy=True))
    habits = db.relationship('Habit', backref='users', lazy=False)
    actions = db.relationship('Action', backref='users', lazy=False)

    def __str__(self):
        return self.login

class Habit(db.Model):
    __tablename__ = 'habits'
    id = db.Column(db.Integer, primary_key = True, unique=True, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.Enum(Category), default=Category.WATER, nullable=False)
    interval = db.Column(db.Enum(Interval), default=Interval.DAY, nullable=False)
    frequency = db.Column(db.Enum(Frequency), default=1, nullable=False)
    reminder = db.Column(db.Boolean, default=False)
    actions = db.relationship('Action', backref='habits', lazy=False)

    def __str__(self):
        return self.category

#habits = db.Table('habits',
#    db.Column('habit_id', db.Integer, db.ForeignKey('habit.id'), primary_key=True),
#    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
#)

class Action(db.Model):
    __tablename__ = 'actions'
    id = db.Column(db.Integer, primary_key = True, unique=True, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    habit = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __str__(self):
        return f'User {self.user} performed habit: {self.habit}.'
