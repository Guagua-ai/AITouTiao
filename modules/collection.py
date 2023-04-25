from flask import request, jsonify
from app import app
from models.collection import Collection
from models.like import Like
from models.user import User
from models.tweet import Tweet
from modules.utils import require_valid_user
from flask_jwt_extended import get_jwt_identity


@app.route('/collections', methods=['POST'])
@require_valid_user
def create_collection():
    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user.id:
        return jsonify({'error': 'User ID is required'}), 400

    name = request.json.get('name')
    if not current_user.id or not name:
        return jsonify({'error': 'User ID and collection name are required'}), 400

    try:
        collection = Collection.create_collection(current_user.id, name)
        return jsonify({'id': collection.id, 'userId': collection.user_id, 'name': collection.name}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/collections/<int:collection_id>/tweets', methods=['POST'])
@require_valid_user
def add_tweet_to_collection(collection_id):
    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user.id:
        return jsonify({'error': 'User ID is required'}), 400

    tweet_id = request.json.get('tweet_id')
    if not tweet_id:
        return jsonify({'error': 'Tweet ID is required'}), 400
    
    collection = None
    if collection_id == 0:
        collection = Collection.get_collection_by_name(user_id=current_user.id, name='Favorites')
    else:
        collection = Collection.get_collection_by_id(collection_id)
    if not collection:
        return jsonify({'error': f'Collection with ID {collection_id} not found'}), 404

    tweet = Tweet.get_tweet_by_id(tweet_id)
    if not tweet:
        return jsonify({'error': f'Tweet with ID {tweet_id} not found'}), 404

    try:
        collection.add_tweet_to_collection(tweet.id)
        return jsonify({'collectionId': collection.id, 'tweetId': tweet.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/collections', methods=['GET'])
@require_valid_user
def get_collections():
    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user.id:
        return jsonify({'error': 'User ID is required'}), 400

    since_id = request.args.get('since_id', default=None, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    start_token = request.args.get('start_token', default=None)

    collections = Collection.get_collections_by_user_id(current_user.id)

    if start_token is None:
        start_token = 0
    if since_id is not None:
        start_token = since_id

    # Paginate the tweet_data using the start_token
    paginated_data = collections[start_token: start_token + per_page]

    response_packet = {
        "status": "ok",
        "totalResults": len(collections),
        "perPage": per_page,
        "collections": [{
            'id': collection.id,
            'name': collection.name,
            'createdAt': collection.created_at
        } for collection in paginated_data],
        "nextStartToken": None
    }

    # Add 'next_start_token' to the response_packet if there are more tweets available
    if start_token + per_page < len(collections):
        next_start_token = start_token + per_page
        response_packet['nextStartToken'] = next_start_token

    return jsonify(response_packet), 200


@app.route('/collections/<int:collection_id>/tweets', methods=['GET'])
@require_valid_user
def get_tweets_from_collection(collection_id):
    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user.id:
        return jsonify({'error': 'User ID is required'}), 400

    since_id = request.args.get('since_id', default=None, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    start_token = request.args.get('start_token', default=None)

    if collection_id == 0:
        collection = Collection.get_collection_by_name(user_id=current_user.id, name='Favorites')
    else:
        collection = Collection.get_collection_by_id_and_user_id(collection_id, current_user.id)
    if not collection:
        return jsonify({'error': f'Collection with ID {collection_id} not found'}), 404

    # Get the tweets from the collection
    tweets = collection.get_tweets()

    if start_token is None:
        start_token = 0
    if since_id is not None:
        start_token = since_id

    # Paginate the tweet_data using the start_token
    paginated_data = tweets[start_token: start_token + per_page]
    liked_tweets = Like.get_likes_by_user_id_and_tweet_ids(current_user.id, [tweet.id for tweet in paginated_data])
    liked_tweets_ids = {like.tweet_id: like for like in liked_tweets}

    paginated_tweets = [tweet.to_ext_dict() for tweet in paginated_data]
    for idx, tweet in enumerate(paginated_tweets):
        if tweet['id'] in liked_tweets_ids:
            paginated_tweets[idx]['isLiked'] = True
        paginated_tweets[idx]['isCollected'] = True

    response_packet = {
        "totalResults": len(tweets),
        "perPage": per_page,
        "tweets": paginated_tweets,
        "nextStartToken": None
    }

    # Add 'nextStartToken' to the response_packet if there are more tweets available
    if start_token + per_page < len(tweets):
        next_start_token = start_token + per_page
        response_packet['nextStartToken'] = next_start_token

    return response_packet, 200


@app.route('/collections/<int:collection_id>/tweets/<int:tweet_id>', methods=['DELETE'])
@require_valid_user
def remove_tweet_from_collection(collection_id, tweet_id):
    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user.id:
        return jsonify({'error': 'User ID is required'}), 400

    collection = Collection.get_collection_by_id_and_user_id(
        collection_id, current_user.id)
    if not collection:
        return jsonify({'error': f'Collection with ID {collection_id} not found'}), 404

    tweet = Tweet.get_tweet_by_id(tweet_id)
    if not tweet:
        return jsonify({'error': f'Tweet with ID {tweet_id} not found'}), 404

    try:
        collection.remove_tweet(tweet)
        return jsonify({'collectionId': collection.id, 'tweetId': tweet.id})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
