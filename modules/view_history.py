from flask import request, jsonify
from app import app
from models.user import User
from models.tweet import Tweet
from models.view_history import ViewHistory
from modules.utlis import require_valid_user
from flask_jwt_extended import get_jwt_identity


@app.route('/view_history', methods=['POST'])
@require_valid_user
def add_to_view_history():
    current_user = User.get_user_by_id(get_jwt_identity())
    tweet_id = request.json.get('tweet_id')
    if not current_user.id or not tweet_id:
        return jsonify({'error': 'User ID and tweet ID are required'}), 400
    view_history = ViewHistory.add_to_view_history(current_user.id, tweet_id)
    return jsonify({'user_id': view_history.user_id, 'tweet_id': view_history.post_id, 'timestamp': view_history.timestamp}), 201


@app.route('/view_history', methods=['GET'])
@require_valid_user
def get_view_history():
    current_user = User.get_user_by_id(get_jwt_identity())

    since_id = request.args.get('since_id', default=None, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    start_token = request.args.get('start_token', default=None)

    view_history = ViewHistory.get_view_history_by_user_id(current_user.id)

    if start_token is None:
        start_token = 0
    if since_id is not None:
        start_token = since_id

    # Paginate the tweet_data using the start_token
    paginated_data = view_history[start_token: start_token + per_page]

    tweets_from_view_history = Tweet.get_tweets_by_ids(
        [item.post_id for item in paginated_data])
    response_packet = {
        "status": "ok",
        "totalResults": len(view_history),
        "perPage": per_page,
        "view_history": [{
            'id': tweet.id,
            'author': tweet.author,
            'title': tweet.title,
            'description': tweet.description,
            'url': tweet.url,
            'url_to_image': tweet.url_to_image,
            'published_at': tweet.published_at,
            'content': '',
        } for tweet in tweets_from_view_history],
        "next_start_token": None
    }

    # Add 'next_start_token' to the response_packet if there are more tweets available
    if start_token + per_page < len(view_history):
        next_start_token = start_token + per_page
        response_packet['next_start_token'] = next_start_token

    return jsonify(response_packet)
