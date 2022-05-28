from flask import jsonify, request, redirect, abort, url_for
from sqlalchemy.sql import exists
from werkzeug.exceptions import HTTPException
from .models import db, User
from .exceptions import RoutingException, RequestException, GeneralException
from .functions import hash_md5, is_email_valid, is_pass_valid

max_login = 20
min_login = 4

def configure_routes(app):

    # Error handler for custom exceptions
    @app.errorhandler(GeneralException)
    def exception_raised(e):
        return jsonify(e.message), e.status_code

    # Generic HTTP error handler
    @app.errorhandler(HTTPException)
    def generic_http_error(e):
        return jsonify(error=str(e)), e.code

    # getting the info about API
    @app.route('/index', methods=['GET'])
    def index():
        response = {"message": "index page"}
        return response

    # getting the info about API
    @app.route('/api_spec', methods=['GET'])
    def api_spec():
        response = {"info": {"version": "01.00"}}
        return response

    # register
    @app.route('/register', methods=['POST'])
    def register():
        if request.method == 'POST':
            login_valid, email_valid, password_valid = False, False, False
            response = {}
            # exctract request body
            try:
                user = request.json
            except:
                message = 'Server could not JSONify the request.'
                raise RequestException(message)
            try:
                login = user['login']
                email = user['email']
                password = user['password']
            except:
                message = 'Some keys are missing. Please provide following keys: login, email and password'
                raise RequestException(message)
            if login:
                if max_login >= len(login) >= min_login:
                    if not db.session.query(exists().where(User.login == login)).scalar():
                        login_valid = True
                    else:
                        response.update({'login_invalid': 'Login is already taken.'})
                else:
                    response.update({'login_invalid': 'Login must be at least 4 characters long.'})
            else:
                response.update({'login_invalid': 'Login is missing'})
            if email:
                if not db.session.query(exists().where(User.email == email)).scalar():
                    if is_email_valid(email):
                        email_valid = True
                    else:
                        response.update({'email_invalid': 'E-mail is invalid.'})
                else:
                    response.update({'E-mail is already taken'})
            else:
                response.update({'email_invalid': 'E-mail is missing.'})
            if password:
                if is_pass_valid(password):
                    password_valid = True
                    hashed_password = hash_md5(password)
                else:
                    response.update({'password_invalid': 'Password is not safe enough.'})
            else:
                response.update({'password_invalid': 'Password is missing'})

            if login_valid and email_valid and password_valid:
                valid_user = User(login=login, email=email, hashed_password=hashed_password)
                db.session.add(valid_user)
                db.session.commit()
                return {'message': 'Account created'}
            else:
                if login_valid:
                    response.update({'login': login})
                if email_valid:
                    response.update({'email': email})
                return jsonify(response)

    # login
    @app.route('/login', methods=['POST'])
    def login():
        if request.method == 'POST':
            # exctract request body
            try:
                user = request.json
            except:
                message = 'Server could not JSONify the request.'
                raise RequestException(message)
            try:
                login = user['login']
                password = user['password']
            except:
                message = 'Some keys are missing. Please provide following keys: login, email and password'
                raise RequestException(message)
            response = {}
            if db.session.query(User).filter(User.login == login):
                existing_user = db.session.query(User).filter(User.login == login)[0]
                hashed_password = hash_md5(password)
                if hashed_password == existing_user.hashed_password:
                    app.logger.info('%s logged in successfully', existing_user.login)
                    return redirect(url_for('index'))
                else:
                    app.logger.info('%s failed to log in', existing_user.login)
                    abort(401)
            else:
                response.update({'login_invalid': 'This login does not exist in database.'})