from flask import Blueprint, jsonify, request
from .exceptions import RoutingException, RequestException, GeneralException, DatabaseQueryException
from werkzeug.exceptions import HTTPException
from flask_login import login_required, current_user
from main import db
from .models import Habit, Action

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
    print(habit_objects)
    habits = []
    for habit_object in habit_objects:
        habit = habit_object.json()
        print(habit)
        habits.append(habit)
    print(habits)
    response =  ({'user': user.id,
        'habits': habits})
    return response

# add habit
@views.route('/add-habit', methods=['POST'])
@login_required
def add_habit():
    if request.method == 'POST':
        user = current_user
        habit = request.json
        if not habit['classification']:
            {'message': 'Habit classification is missing'}
        if not habit['recurrence']:
            {'message': 'Habit recurrence is missing'}
        if not habit['frequency']:
            {'message': 'Habit frequency is missing'}
        if not habit['reminder']:
            {'message': 'Habit reminder boolean is missing'}
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