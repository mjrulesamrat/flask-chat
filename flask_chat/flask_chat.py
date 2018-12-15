import os

from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Serve client-side application."""
    return "Hello World"
