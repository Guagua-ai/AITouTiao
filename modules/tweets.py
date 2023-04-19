from functools import wraps
from urllib import request

from flask_jwt_extended import get_jwt_identity, jwt_required
from app import app, chatbot
from flask import request, jsonify

from models.tweet import Tweet
from models.user import User
from models.view_history import ViewHistory
from utils.time import standard_format


@app.route('/tweets', methods=['GET'])
def tweets():
    tweet_data = chatbot.get_tweet_data()

    response_packet = {
        "status": "ok",
        "totalResults": len(tweet_data),
        "articles": tweet_data
    }

    return jsonify(response_packet)


@app.route('/tweets/pagination', methods=['GET'])
def tweets_pagination():
    since_id = request.args.get('since_id', default=None, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    start_token = request.args.get('start_token', default=None)

    tweet_data = chatbot.get_tweet_data()

    if start_token is None:
        start_token = 0
    if since_id is not None:
        start_token = since_id

    # Paginate the tweet_data using the start_token
    paginated_data = tweet_data[start_token: start_token + per_page]

    response_packet = {
        "status": "ok",
        "totalResults": len(tweet_data),
        "perPage": per_page,
        "articles": paginated_data,
        "next_start_token": None
    }

    # Add 'next_start_token' to the response_packet if there are more tweets available
    if start_token + per_page < len(tweet_data):
        next_start_token = start_token + per_page
        response_packet['next_start_token'] = next_start_token

    return jsonify(response_packet)


@app.route('/tweets/<int:tweet_id>', methods=['GET'])
@jwt_required(optional=True)
def get_tweet_by_id(tweet_id):
    tweet = Tweet.query.get(tweet_id)
    if tweet is not None:
        tweet_data = {
            "id": tweet.id,
            "source": {
                'id': tweet.source_id,
                'name': tweet.source_name
            },
            "author": tweet.author,
            "title": tweet.title,
            "description": tweet.description,
            "url": tweet.url,
            "urlToImage": tweet.url_to_image,
            "publishedAt": standard_format(tweet.published_at),
            "content": tweet.content
        }
        if get_jwt_identity():
            current_user = User.get_user_by_id(get_jwt_identity())
            ViewHistory.add_to_view_history(current_user.id, tweet_id)
        return jsonify(tweet_data), 200
    else:
        return jsonify({'error': 'Tweet not found'}), 404
