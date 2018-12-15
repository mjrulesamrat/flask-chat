import os

from flask import Flask, request, jsonify, abort

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

@app.route('/')
def index():
    """Serve client-side application."""
    return "Hello World"


@app.route('/api/users', methods=['POST'])
def new_user():
    """
    Register a new user.
    This endpoint is publicly available.
    """
    user = User.create(request.get_json() or {})
    if User.query.filter_by(nickname=user.nickname).first() is not None:
        abort(400)
    db.session.add(user)
    db.session.commit()
    r = jsonify(user.to_dict())
    return r


@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Return list of users.
    """
    users = User.query.order_by(User.updated_at.asc(), User.nickname.asc())
    if request.args.get('online'):
        users = users.filter_by(online=(request.args.get('online') != '0'))
    if request.args.get('updated_since'):
        users = users.filter(
            User.updated_at > int(request.args.get('updated_since')))
    return jsonify({'users': [user.to_dict() for user in users.all()]})


@app.route('/api/users/<id>', methods=['GET'])
def get_user(id):
    """
    Return a user.
    """
    return jsonify(User.query.get_or_404(id).to_dict())


@app.route('/api/users/<id>', methods=['PUT'])
def edit_user(id):
    """
    Modify an existing user.
    """
    user = User.query.get_or_404(id)
    # No authentication at the moment
    # if user != g.current_user:
    #     abort(403)
    user.from_dict(request.get_json() or {})
    db.session.add(user)
    db.session.commit()
    return '', 204
