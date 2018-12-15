import os

from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

# Flask extensions
db = SQLAlchemy()
bootstrap = Bootstrap()

# Import models so that they are registered with SQLAlchemy
from . import models  # noqa

def create_app(config_name=None):
    basedir = os.path.abspath(os.path.dirname(__file__) + '/..')

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'db.sqlite'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize flask extensions
    db.init_app(app)
    bootstrap.init_app(app)

    from .flask_chat import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Registed API routes with the application
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app
