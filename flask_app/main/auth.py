from flask import jsonify, request, redirect, url_for, Blueprint
from sqlalchemy.sql import exists
from werkzeug.exceptions import HTTPException
from .models import User
from main import db
from .exceptions import RoutingException, RequestException, GeneralException
from .functions import hash_md5, is_email_valid, is_pass_valid
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

max_login = 20
min_login = 4


# Error handler for custom exceptions
@auth.errorhandler(GeneralException)
def exception_raised(e):
    return jsonify(e.message), e.status_code

# Generic HTTP error handler
@auth.errorhandler(HTTPException)
def generic_http_error(e):
    return jsonify(error=str(e)), e.code

# register
@auth.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        login_valid, email_valid, password_valid = False, False, False
        try:
            login = request.form.get('login')
            email = request.form.get('email')
            password = request.form.get('password')
        except:
            message = 'Some keys are missing. Please provide following keys: login, email and password'
            raise RequestException(message)
        if login:
            if max_login >= len(login) >= min_login:
                if not db.session.query(exists().where(User.login == login)).scalar():
                    login_valid = True
                else:
                    return {'login_invalid': 'Login is already taken.'}
            else:
                return {'login_invalid': 'Login must be at least 4 characters long.'}
        else:
            return {'login_invalid': 'Login is missing'}
        if email:
            if not db.session.query(exists().where(User.email == email)).scalar():
                if is_email_valid(email):
                    email_valid = True
                else:
                    return {'login': login,
                    'email_invalid': 'E-mail is invalid.'}
            else:
                return {'login': login,
                'email_invalid': 'E-mail is already taken'}
        else:
            return {'login': login,
            'email_invalid': 'E-mail is missing.'}
        if password:
            if is_pass_valid(password):
                password_valid = True
                hashed_password = hash_md5(password)
            else:
                return {'login': login,
                'email': email,
                'password_invalid': 'Password is not safe enough.'}
        else:
            return {'login': login,
                'email': email,
                'password_invalid': 'Password is missing'}
        if login_valid and email_valid and password_valid:
            valid_user = User(login=login, email=email, hashed_password=hashed_password)
            db.session.add(valid_user)
            db.session.commit()
            login_user(valid_user, remember=True)
            return {'message': 'Account created'}

# login
@auth.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        try:
            login = request.form.get('login')
            password = request.form.get('password')
        except:
            message = 'Some keys are missing. Please provide following keys: login, email and password'
            raise RequestException(message)
        existing_user = User.query.filter_by(login = login).first()
        if existing_user:
            hashed_password = hash_md5(password)
            if hashed_password == existing_user.hashed_password:
                login_user(existing_user, remember=True)
                return {'message': 'Logged in!'}
            else:
                return {'login': login,
                'message': 'Incorrect password'}
        else:
            return {'login_invalid': 'This login does not exist in database.'}

# logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return {'message': 'Logged out!'}
