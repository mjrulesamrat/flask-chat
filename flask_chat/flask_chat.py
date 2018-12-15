import os

from flask import Flask, request, jsonify, abort, make_response

from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

basedir = os.path.abspath(os.path.dirname(__file__) + '/..')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'db.sqlite'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask extensions
db = SQLAlchemy(app)
Bootstrap(app)

# Import models so that they are registered with SQLAlchemy
from .models import User, Message

# Registed API routes with the application
from .api import api as api_blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')


@app.route('/')
def index():
    """Serve client-side application."""
    return "Hello World"
