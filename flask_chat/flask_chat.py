import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

# Flask extensions
Bootstrap(app)


@app.route('/')
def index():
    """Serve client-side application."""
    return "Hello World"
