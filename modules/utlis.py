from app import redis_store, jwt
from functools import wraps
from flask import jsonify
from flask_jwt_extended import current_user, verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended import get_current_user
from models.user import User


# Decorator to check if the user is logged in
@jwt.token_in_blocklist_loader
def check_if_token_in_denylist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    entry = redis_store.get(jti)
    return entry is not None


# Decorator to check if the user is admin
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)


# Decorator to check if the user is valid
def require_valid_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()  # Check if a valid JWT token is provided
        user_id = get_jwt_identity()  # Get the user ID from the JWT token

        # Check if the user exists
        current_user = User.query.filter_by(id=user_id).first()
        if not current_user:
            return jsonify({"message": "User not found"}), 404

        return f(*args, **kwargs)
    return decorated_function


# Decorator to check if the user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user or not current_user.is_admin:
            return jsonify({'message': 'Admin required'}), 403
        return f(*args, **kwargs)
    return decorated_function