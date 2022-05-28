from flask import Flask
from logging.config import dictConfig
from main.routes import configure_routes
from main.models import db

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/healthy-habits-manager'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

configure_routes(app)

db.init_app(app)

if __name__ == '__main__':
    app.run()