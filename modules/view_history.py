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

    if since_id is not None:
        # Filter view_history based on the since_id
        view_history = [item for item in view_history if item.id > since_id]

    # Paginate the view_history using the start_token
    if start_token:
        start_index = None
        for i, item in enumerate(view_history):
            if item.id == int(start_token):
                start_index = i
                break
        if start_index is None:
            # Invalid start_token, return empty response
            return jsonify({
                'status': 'ok',
                'totalResults': 0,
                'perPage': per_page,
                'view_history': [],
                'next_start_token': None
            })
        paginated_data = view_history[start_index + 1:start_index + 1 + per_page]
    else:
        paginated_data = view_history[:per_page]

    tweets_from_view_history = Tweet.get_tweets_by_ids([item.post_id for item in paginated_data])

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
            'content': tweet.content
        } for tweet in tweets_from_view_history],
        "next_start_token": None
    }

    # Add 'next_start_token' to the response_packet if there are more items available
    if len(paginated_data) < len(view_history):
        next_start_token = str(view_history[len(paginated_data)].id)
        response_packet['next_start_token'] = next_start_token

    return jsonify(response_packet)
