from functools import wraps
from urllib import request
from flask import jsonify


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('access_token', type=int)

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        return f(*args, **kwargs)
    return decorated
