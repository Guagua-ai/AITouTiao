from urllib import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import app, chatbot
from flask import request, jsonify
from models.collection import Collection
from models.like import Like
from models.tweet import Tweet
from models.user import User
from models.view_history import ViewHistory
from modules.utils import require_valid_user


@app.route('/tweets', methods=['GET'])
@jwt_required(optional=True)
def tweets():
    tweet_data = chatbot.get_tweet_data()
    
    if get_jwt_identity():
        current_user = User.get_user_by_id(get_jwt_identity())
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        collected_tweets = [
            tweet.id for tweet in Collection.get_collection_by_name(user_id=current_user.id, name='Favorites').tweets]
        
        liked_tweets = [
            like.tweet_id for like in current_user.get_likes()]
        for tweet in tweet_data:
            if tweet['id'] in liked_tweets:
                tweet['liked'] = True
            if tweet['id'] in collected_tweets:
                tweet['collected'] = True

    response_packet = {
        "totalResults": len(tweet_data),
        "articles": tweet_data
    }

    return jsonify(response_packet), 200


@app.route('/tweets/pagination', methods=['GET'])
@jwt_required(optional=True)
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
        "nextStartToken": None
    }
    
    if get_jwt_identity():
        current_user = User.get_user_by_id(get_jwt_identity())
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        collected_tweets = [
            tweet.id for tweet in Collection.get_collection_by_name(user_id=current_user.id, name='Favorites').tweets]
        
        liked_tweets = [
            like.tweet_id for like in current_user.get_likes()]
        for tweet in paginated_data:
            if tweet['id'] in liked_tweets:
                tweet['liked'] = True
            if tweet['id'] in collected_tweets:
                tweet['collected'] = True

    # Add 'next_start_token' to the response_packet if there are more tweets available
    if start_token + per_page < len(tweet_data):
        next_start_token = start_token + per_page
        response_packet['nextStartToken'] = next_start_token

    return jsonify(response_packet), 200


@app.route('/tweets/<int:tweet_id>', methods=['GET'])
@jwt_required(optional=True)
def get_tweet_by_id(tweet_id):
    tweet = Tweet.get_tweet_by_id(tweet_id)
    if tweet is not None:
        tweet_data = tweet.to_ext_dict(needs_content=True)
        if get_jwt_identity():
            current_user = User.get_user_by_id(get_jwt_identity())
            ViewHistory.add_to_view_history(current_user.id, tweet_id)
        return jsonify(tweet_data), 200
    else:
        return jsonify({'error': 'Tweet not found'}), 404


@app.route('/tweets/<int:tweet_id>/like', methods=['POST'])
@require_valid_user
def like_tweet(tweet_id):
    """
    Record a user's like for a tweet.
    Expects a tweet ID parameter in the URL.
    """
    tweet = Tweet.get_tweet_by_id(tweet_id)
    if not tweet:
        return jsonify({'message': 'Tweet not found'}), 404

    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user:
        return jsonify({'message': 'User not found'}), 404

    like = Like.get_like_by_user_id_and_tweet_id(
        user_id=current_user.id, tweet_id=tweet.id)
    if like:
        return jsonify({'message': 'User already liked this tweet'}), 400

    like = Like.create_like(user_id=current_user.id, tweet_id=tweet.id)
    tweet.add_like(like)

    return jsonify({'message': 'Like recorded successfully'}), 200


@app.route('/tweets/<int:tweet_id>/likes', methods=['GET'])
def get_likes_for_tweet(tweet_id):
    """
    Get all the likes for a tweet.
    Expects a tweet ID parameter in the URL.
    """
    tweet = Tweet.get_tweet_by_id(tweet_id)
    if not tweet:
        return jsonify({'message': 'Tweet not found'}), 404

    likes = tweet.get_likes()
    if not likes:
        return jsonify({'message': 'No likes found'}), 404

    likes_data = []
    for like in likes:
        user = User.get_user_by_id(like.user_id)
        likes_data.append({
            'id': like.id,
            'user_id': user.id,
            'name': user.name,
            'profile_image_url': user.profile_image
        })

    like_count = tweet.like_count()
    print(like_count)
    return jsonify({'likes': likes_data, 'like_count': like_count}), 200


@app.route('/tweets/<int:tweet_id>/unlike', methods=['POST'])
@require_valid_user
def unlike_tweet(tweet_id):
    """
    Remove a user's like for a tweet.
    Expects a tweet ID parameter in the URL.
    """
    tweet = Tweet.get_tweet_by_id(tweet_id)
    if not tweet:
        return jsonify({'message': 'Tweet not found'}), 404

    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user:
        return jsonify({'message': 'User not found'}), 404

    like = Like.get_like_by_user_id_and_tweet_id(
        user_id=current_user.id, tweet_id=tweet.id)
    if like is None:
        return jsonify({'message': 'User did not like this tweet'}), 400

    deleted_like = Like.unlike_by_id(like.id)
    tweet.remove_like(deleted_like)
    if not deleted_like:
        return jsonify({'message': 'Error deleting like'}), 500
    return jsonify({'message': 'Like deleted successfully'}), 200
