from flask import Blueprint, jsonify, request
from .exceptions import RoutingException, RequestException, GeneralException, DatabaseQueryException
from werkzeug.exceptions import HTTPException
from flask_login import login_required, current_user
from main import db
from .models import Habit, Action
from .functions import current_dashboard, actions_from_current_interval


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
    response = current_dashboard(user)
    return response


# add habit
@views.route('/habit', methods=['POST', 'DELETE'])
@login_required
def habit():
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
    elif request.method == 'DELETE':
        user = current_user
        if not request.form.get('classification'):
            return {'message': 'Habit info is missing'}
        else:
            classification = request.form.get('classification')
        habit = Habit.query.filter_by(user=user.id, classification=classification).first()
        actions = habit.actions
        for action in actions:
            db.session.delete(action)
        db.session.delete(habit)
        db.session.commit()
        return {'message': 'Habit was deleted.'}

# add action
@views.route('/action', methods=['POST', 'DELETE'])
@login_required
def action():
    user = current_user
    if not request.form.get('classification'):
        return {'message': 'Habit info is missing'}
    else:
        classification = request.form.get('classification')
    habit = Habit.query.filter_by(user=user.id, classification=classification).first()
    if request.method == 'POST':
        try:
            action = Action(user=user.id, habit=habit.id)
        except:
            message = 'Error occured whilecreating new action object.'
            raise DatabaseQueryException(message)
        try:
            db.session.add(action)
            db.session.commit()
            return {'message': 'New action added!'}
        except:
            message = 'Error occured while adding new action to database.'
            raise DatabaseQueryException(message)
    elif request.method == 'DELETE':
        action = actions_from_current_interval(user, habit)
        if action == None:
            return {'message': 'No action found for current time period.'}
        try:
            db.session.delete(action)
            db.session.commit()
            return {'message': 'Action deleted!'}
        except:
            message = 'Error occured while deleting action to database.'
            raise DatabaseQueryException(message)