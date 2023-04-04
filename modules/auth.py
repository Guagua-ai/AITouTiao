from app import app
from urllib import request
from auth.auth import User
from flask import request, jsonify
from modules.utlis import token_required


@app.route('/signup', methods=['POST'])
def signup():
    """
    Registers a new user.
    Expects a JSON request with 'email' and 'password' fields.
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 409
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    """
    Logs in a user.
    Expects a JSON request with 'email' and 'password' fields.
    Returns a JWT token upon successful login.
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401
    token = user.generate_token()
    return jsonify({'token': token.decode('utf-8')}), 200


@app.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Logs out a user.
    """
    current_user = User.query.filter_by(id=g.user_id).first()
    current_user.revoked_token = True
    db.session.commit()
    return jsonify({'message': 'User logged out successfully'}), 200


@app.route('/profile', methods=['GET'])
@token_required
def profile():
    """
    Returns the current user's profile.
    """
    current_user = User.query.filter_by(id=g.user_id).first()
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'created_at': current_user.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200
