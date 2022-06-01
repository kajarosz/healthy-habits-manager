from flask import Blueprint, jsonify, request
from .exceptions import RoutingException, RequestException, GeneralException, DatabaseQueryException
from werkzeug.exceptions import HTTPException
from flask_login import login_required, current_user
from main import db
from .models import Habit, Action
from datetime import date, datetime, timedelta


views = Blueprint('views', __name__)

# Error handler for custom exceptions
@views.errorhandler(GeneralException)
def exception_raised(e):
    return jsonify(e.message), e.status_code

# Generic HTTP error handler
@views.errorhandler(HTTPException)
def generic_http_error(e):
    return jsonify(error=str(e)), e.code

# getting the info about API
@views.route('/index', methods=['GET'])
def index():
    response = {"message": "index page"}
    return response

# getting the info about API
@views.route('/api_spec', methods=['GET'])
def api_spec():
    response = {"info": {"version": "01.00"}}
    return response

#  dashboard
@views.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    user = current_user
    habit_objects = user.habits
    daily_habits = []
    weekly_habits = []
    monthly_habits = []
    current_time = datetime.utcnow()
    current_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = current_time.weekday()
    current_week_from = current_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=weekday)
    current_week_to = current_week_from + timedelta(days=6)
    current_month_from = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if current_time.month in [1, 3, 5, 7, 8, 10, 12]:
        current_month_to = current_time.replace(day=31, hour=0, minute=0, second=0, microsecond=0)
    elif current_time.month in [2, 4, 6, 9, 11]:
        current_month_to = current_time.replace(day=30, hour=0, minute=0, second=0, microsecond=0)
    else:
        if current_time.year % 4 == 0:
            current_month_to = current_time.replace(day=29, hour=0, minute=0, second=0, microsecond=0)
        else:
            current_month_to = current_time.replace(day=28, hour=0, minute=0, second=0, microsecond=0)
    for habit_object in habit_objects:
        habit = habit_object.json()
        if habit['recurrence'] == 'DAILY':
            actions = habit_object.actions
            daily_actions = list(filter(lambda Action: Action.timestamp > current_day, actions))
            actions_no = len(daily_actions)
            habit.update({'completed': actions_no})
            daily_habits.append(habit)
        elif habit['recurrence'] == 'WEEKLY':
            actions = habit_object.actions
            weekly_actions = list(filter(lambda Action: current_week_from < Action.timestamp < current_week_to, actions))
            actions_no = len(weekly_actions)
            habit.update({'completed': actions_no})
            weekly_habits.append(habit)
        elif habit['recurrence'] == 'MONTHLY':
            actions = habit_object.actions
            monthly_actions = list(filter(lambda Action: current_month_from < Action.timestamp < current_month_to, actions))
            actions_no = len(monthly_actions)
            habit.update({'completed': actions_no})
            monthly_habits.append(habit)
    response =  ({'user': user.id,
        'daily habits': daily_habits,
        'weekly habits': weekly_habits,
        'monthly habits': monthly_habits})
    return response


# add habit
@views.route('/add-habit', methods=['POST'])
@login_required
def add_habit():
    if request.method == 'POST':
        user = current_user
        if not request.form.get('classification'):
            return {'message': 'Habit classification is missing'}
        else:
            classification = request.form.get('classification')
        if not request.form.get('recurrence'):
            return {'message': 'Habit recurrence is missing'}
        else:
            recurrence = request.form.get('recurrence')
        if not request.form.get('frequency'):
            return {'message': 'Habit frequency is missing'}
        else:
            frequency = request.form.get('frequency')
        if not request.form.get('reminder'):
            return {'message': 'Habit reminder boolean is missing'}
        else:
            if request.form.get('reminder').lower() == 'false':
                reminder = False
            elif request.form.get('reminder').lower() == 'true':
                reminder = True
        try:
            new_habit = Habit(user=user.id, classification=classification, recurrence=recurrence, frequency=frequency, reminder=reminder)
            db.session.add(new_habit)
            db.session.commit()
        except:
            message = 'Error occured while adding new habit to database.'
            raise DatabaseQueryException(message)
        return {'message': 'New habbit added!'}

# add action
@views.route('/add-action', methods=['POST'])
@login_required
def add_action():
    if request.method == 'POST':
        user = current_user
        if not request.form.get('classification'):
            return {'message': 'Habit info is missing'}
        else:
            classification = request.form.get('classification')
        habit = Habit.query.filter_by(user=user.id, classification=classification).first()
        try:
            new_action = Action(user=user.id, habit=habit.id)
            db.session.add(new_action)
            db.session.commit()
        except:
            message = 'Error occured while adding new action to database.'
            raise DatabaseQueryException(message)
        return {'message': 'New action added!'}
        