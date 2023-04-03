from functools import wraps
from urllib import request
from app import app
from chat import chatbot
from flask import request, jsonify
from utils import token_required


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
@token_required
def tweets_pagination():
    since_id = request.args.get('since_id', default=None, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    start_token = request.args.get('start_token', default=None)

    tweet_data = chatbot.get_tweet_data()

    if since_id is not None:
        # Filter tweet_data based on the since_id
        tweet_data = [tweet for tweet in tweet_data if int(
            tweet['id']) > since_id]

    # Paginate the tweet_data using the start_token
    if start_token:
        start_index = None
        for i, tweet in enumerate(tweet_data):
            if tweet['id'] == int(start_token):
                start_index = i
                break
        if start_index is None:
            # Invalid start_token, return empty response
            return jsonify({
                'status': 'ok',
                'totalResults': 0,
                'perPage': per_page,
                'articles': [],
                'next_start_token': None
            })
        paginated_data = tweet_data[start_index + 1:start_index + 1 + per_page]
    else:
        paginated_data = tweet_data[:per_page]

    response_packet = {
        "status": "ok",
        "totalResults": len(tweet_data),
        "perPage": per_page,
        "articles": paginated_data,
        "next_start_token": None
    }

    # Add 'next_start_token' to the response_packet if there are more tweets available
    if len(paginated_data) < len(tweet_data):
        next_start_token = str(tweet_data[len(paginated_data)]['id'])
        response_packet['next_start_token'] = next_start_token

    return jsonify(response_packet)
