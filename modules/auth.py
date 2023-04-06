import os
import time
import models

from app import app, redis_store
from urllib import request
from models.user import User
from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from modules.utlis import require_valid_user


@app.route('/auth/signup', methods=['POST'])
def signup():
    """
    Registers a new user.
    Expects a JSON request with 'email' and 'password' fields.
    """
    data = request.json
    if not data:
        return jsonify({'message': 'Request body is empty'}), 400
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    profile_image = None
    if data.get('profile_image') is not None:
        profile_image = data.get('profile_image')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    if User.get_user_by_email(email):
        return jsonify({'message': 'Email already exists'}), 400
    if User.get_user_by_name(name):
        return jsonify({'message': 'Name already exists'}), 400
    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    if len(name) < 3:
        return jsonify({'message': 'Name must be at least 3 characters'}), 400
    if len(name) > 20:
        return jsonify({'message': 'Name must be less than 20 characters'}), 400

    user = User.create_user(name, email, password, profile_image=profile_image)
    access_token = create_access_token(identity=user.id, additional_claims={
                                       "is_admin": user.is_admin()})
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'User created successfully',
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    }), 201


@app.route('/auth/login', methods=['POST'])
def login():
    """
    Logs in a user.
    Expects a JSON request with 'email' and 'password' fields.
    Returns a JWT token upon successful login.
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.get_user_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401
    access_token = create_access_token(identity=user.id, additional_claims={
                                       "is_admin": user.is_admin()})
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify({
        'message': 'User logged in successfully',
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    }), 200


@app.route('/auth/logout', methods=['POST'])
@require_valid_user
def logout():
    jti = get_jwt()['jti']  # Get the token identifier
    user_identity = get_jwt_identity()

    # Add token to the denylist
    redis_store.set(jti, user_identity, ex=get_jwt()['exp'] - int(time.time()))

    return jsonify({'message': 'Successfully logged out'}), 200


@app.route('/auth/profile', methods=['GET'])
@require_valid_user
def profile():
    """
    Returns the current user's profile.
    """
    current_user = User.get_user_by_id(get_jwt_identity())

    if not current_user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'created_at': current_user.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200


@app.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refreshes the access token.
    """
    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    access_token = create_access_token(identity=current_user.id, additional_claims={
                                       "is_admin": current_user.is_admin()})
    return jsonify({'access_token': access_token}), 200


@app.route('/auth', methods=['DELETE'])
@require_valid_user
def delete_account():
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
    user = User.query.get(user_id)  # Get the User instance from the database

    if user:
        User.delete_user(user_id)  # Delete the user from the database
        return jsonify({"message": "User account deleted successfully"}), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route('/auth/reset-password', methods=['POST'])
def reset_password_request():
    email = request.json['email']
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY").encode())
    token = serializer.dumps(email, salt='password-reset')

    send_email(email, token)

    return jsonify({"message": "Password reset email sent"}), 200


@app.route('/auth/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY").encode())
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except SignatureExpired:
        return jsonify({"error": "Token expired"}), 401

    new_password = request.json['new_password']
    if len(new_password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    if len(new_password) > 20:
        return jsonify({'message': 'Password must be less than 20 characters'}), 400

    user = User.query.filter_by(email=email).first()
    User.set_password(user, new_password)
    return jsonify({"message": "Password updated successfully"}), 200


# This route is used to reset the password
def send_email(to, token):
    sg = SendGridAPIClient(app.config['SENDGRID_API_KEY'])
    from_email = 'noreply@virtualdynamiclab.com'
    subject = 'GPT News Feed: Password Reset Request'
    reset_url = f'{request.host_url}reset-password/{token}'

    mail = SendGridMail(
        from_email=from_email,
        to_emails=to,
        subject=subject,
        html_content=f'<p>Please click the link below to reset your password:</p><br><a href="{reset_url}">{reset_url}</a>'
    )
    sg.send(mail)
