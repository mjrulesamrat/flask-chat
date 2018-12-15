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

# Import authentication handlers
from .auth import basic_auth, token_auth, token_optional_auth


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
@token_optional_auth.login_required
def get_users():
    """
    Return list of users.
    This endpoint is publicly available, but if the client has a token it
    should send it, as that indicates to the server that the user is online.
    """
    users = User.query.order_by(User.updated_at.asc(), User.nickname.asc())
    if request.args.get('online'):
        users = users.filter_by(online=(request.args.get('online') != '0'))
    if request.args.get('updated_since'):
        users = users.filter(
            User.updated_at > int(request.args.get('updated_since')))
    return jsonify({'users': [user.to_dict() for user in users.all()]})


@app.route('/api/users/<id>', methods=['GET'])
@token_optional_auth.login_required
def get_user(id):
    """
    Return a user.
    This endpoint is publicly available, but if the client has a token it
    should send it, as that indicates to the server that the user is online.
    """
    return jsonify(User.query.get_or_404(id).to_dict())


@app.route('/api/users/<id>', methods=['PUT'])
@token_auth.login_required
def edit_user(id):
    """
    Modify an existing user.
    This endpoint is requires a valid user token.
    Also: users can only modify themselves.
    """
    user = User.query.get_or_404(id)
    if user != g.current_user:
        abort(403)
    user.from_dict(request.get_json() or {})
    db.session.add(user)
    db.session.commit()
    return '', 204


@app.route('/api/tokens', methods=['POST'])
@basic_auth.login_required
def new_token():
    """
    Request a user token.
    This endpoint is requires basic auth with nickname and password.
    """
    if g.current_user.token is None:
        g.current_user.generate_token()
        db.session.add(g.current_user)
        db.session.commit()
    return jsonify({'token': g.current_user.token})


@app.route('/api/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    """
    Revoke a user token.
    This endpoint is requires a valid user token.
    """
    g.current_user.token = None
    db.session.add(g.current_user)
    db.session.commit()
    return '', 204
