from flask import Blueprint, jsonify, request
from .exceptions import RoutingException, RequestException, GeneralException, DatabaseQueryException
from werkzeug.exceptions import HTTPException
from flask_login import login_required, current_user
from main import db
from .models import Habit, Action
from datetime import datetime


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
    current_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    for habit_object in habit_objects:
        habit = habit_object.json()
        if habit['recurrence'] == 'DAILY':
            actions = habit_object.actions
            daily_actions = list(filter(lambda Action: Action.timestamp > current_time, actions))
            actions_no = len(daily_actions)
            habit.update({'completed': actions_no})
            daily_habits.append(habit)
        elif habit['recurrence'] == 'WEEKLY':
            weekly_habits.append(habit)
        elif habit['recurrence'] == 'MONTHLY':
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
        habit = request.json
        if not habit['classification']:
            return {'message': 'Habit classification is missing'}
        if not habit['recurrence']:
            return {'message': 'Habit recurrence is missing'}
        if not habit['frequency']:
            return {'message': 'Habit frequency is missing'}
        if not habit['reminder']:
            return {'message': 'Habit reminder boolean is missing'}
        else:
            if habit['reminder'].lower() == 'false':
                habit['reminder'] = False
            elif habit['reminder'].lower() == 'true':
                habit['reminder'] = True
        try:
            new_habit = Habit(user=user.id, classification=habit['classification'], recurrence=habit['recurrence'], frequency=habit['frequency'], reminder=habit['reminder'])
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
        action = request.json
        if not action['classification']:
            return {'message': 'Habit info is missing'}
        habit = Habit.query.filter_by(user=user.id, classification=action['classification']).first()
        try:
            new_action = Action(user=user.id, habit=habit.id)
            db.session.add(new_action)
            db.session.commit()
        except:
            message = 'Error occured while adding new action to database.'
            raise DatabaseQueryException(message)
        return {'message': 'New action added!'}
        