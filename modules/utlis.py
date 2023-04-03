from functools import wraps
from urllib import request


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        since_id = request.args.get('since_id', type=int)

        # Allow request to proceed without a token if since_id is not provided
        if since_id is None:
            return f(*args, **kwargs)

        # if not token:
        #     return jsonify({'message': 'Token is missing!'}), 401
        # elif token != 'your-token':  # Replace with your own token
        #     return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)
    return decorated
