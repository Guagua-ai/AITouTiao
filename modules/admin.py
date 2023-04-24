import os
import requests
from app import app
from flask import jsonify, request
from db.storage import upload_image_to_s3
from models.user import User
from models.tweet import Tweet
from modules.utils import admin_required
from search.index import create_post_search_index, create_user_search_index
from translator.core import TranslatorCore
from utils.time import standard_format


@app.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    """
    Get all users.
    """
    users = User.get_all_users()
    return jsonify({'users': [user.to_dict() for user in users]}), 200


@app.route('/admin/user/promote/<int:user_id>', methods=['POST'])
@admin_required
def promote_user(user_id):
    """
    Promote a user to admin.
    Expects a user ID parameter in the URL.
    """
    user = User.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if user.is_admin():
        return jsonify({'message': 'User is already an admin'}), 400

    User.update_user(user_id, role='admin')
    return jsonify({'message': 'User promoted successfully'}), 200


@app.route('/admin/user/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    Update a user's information.
    Expects a user ID parameter in the URL.
    """
    user = User.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    user = User.update_user(user_id,
                            name=data.get('name'),
                            email=data.get('email'),
                            phone=data.get('phone'),
                            profile_image=data.get('profile_image'),
                            role=data.get('role'),
                            quota=data.get('quota'))

    if data.get('email') or data.get('phone') or data.get('name'):
        create_user_search_index().partial_update_object(user.to_index_dict())
    return jsonify({'message': 'User updated successfully'}), 200


@app.route('/admin/user/<int:user_id>', methods=['DELETE'])
@admin_required
def remove_user(user_id):
    """
    Remove a user by ID.
    """
    user = User.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    User.delete_user(user_id)
    create_user_search_index().delete_object(user.id)
    return jsonify({'message': 'User deleted successfully'}), 200


@app.route('/admin/download_tweet_images', methods=['POST'])
@admin_required
def download_tweet_images():
    """
    Downloads images from all tweets' url_to_image and uploads them to S3.
    """
    tweets = Tweet.get_all_tweets()
    url_set = set()
    for tweet in tweets:
        url_to_image = tweet.url_to_image
        if "s3.amazonaws.com" in url_to_image:
            continue

        if url_to_image and url_to_image not in url_set:
            # Download image from URL
            response = requests.get(url_to_image)
            if response.status_code != 200:
                continue
            image_data = response.content

            bucket_key = 'server-news-tweet-photo'

            # Upload the image to S3
            object_key = f'tweets/{tweet.author}.jpg'
            success = upload_image_to_s3(bucket_key, object_key, image_data)
            if not success:
                continue

            # Get the URL of the S3 object
            object_url = f'https://{bucket_key}.s3.amazonaws.com/{object_key}'

            # Update the tweet's url_to_image field
            Tweet.update_tweet(tweet.id, url_to_image=object_url)

            # Add the URL to the set
            url_set.add(url_to_image)
        else:
            # Get the URL of the S3 object
            object_key = f'tweets/{tweet.author}.jpg'

            # Update the tweet's url_to_image field
            object_url = f'https://{bucket_key}.s3.amazonaws.com/{object_key}'

            # Update the tweet's url_to_image field
            Tweet.update_tweet(tweet.id, url_to_image=object_url)

    return jsonify({'message': 'Images downloaded and uploaded successfully'}), 200


@app.route('/admin/purify_tweets', methods=['PUT'])
@admin_required
def purify_tweets():
    """
    Removes all tweets from the database.
    """
    tweets = Tweet.get_all_tweets()
    translator = TranslatorCore(os.getenv('OPENAI_API_KEY'))
    for tweet in tweets:
        # Purify the tweet's title, description, and content
        updated_title = translator.purify_text(tweet.title)
        updated_description = translator.purify_text(tweet.description)
        updated_content = translator.purify_text(tweet.content)
        # Update the tweet's content field
        Tweet.update_tweet(tweet.id,
                           title=updated_title,
                           description=updated_description,
                           content=updated_content)

    return jsonify({'message': 'Tweets purified successfully'}), 200


@app.route('/admin/tweets', methods=['GET'])
@admin_required
def get_all_tweets():
    """
    Get all tweets.
    """
    tweets = Tweet.get_all_tweets()

    response_packet = {
        "totalResults": len(tweets),
        "articles": [{
            "id": tweet.id,
            "source": {
                'id': tweet.source_id,
                'name': tweet.source_name
            },
            "author": tweet.author,
            "displayname": tweet.display_name,
            "title": tweet.title,
            "description": tweet.description,
            "url": tweet.url,
            "urlToImage": tweet.url_to_image,
            "publishedAt": standard_format(tweet.published_at),
            "content": tweet.content,
            "likes": tweet.num_likes,
        } for tweet in tweets]
    }

    return jsonify(response_packet), 200


@app.route('/admin/tweets/<int:tweet_id>', methods=['PUT'])
@admin_required
def update_tweet(tweet_id):
    """
    Update a tweet's information by ID.
    Expects a JSON payload with fields to update in the request body.
    """
    tweet = Tweet.get_tweet_by_id(tweet_id)
    if not tweet:
        return jsonify({'message': 'Tweet not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    source_id = data.get('source_id')
    source_name = data.get('source_name')
    author = data.get('author')
    display_name = data.get('display_name')
    title = data.get('title')
    description = data.get('description')
    url = data.get('url')
    url_to_image = data.get('urlToImage')
    published_at = data.get('publishedAt')
    content = data.get('content')

    tweet = Tweet.update_tweet(tweet_id,
                               source_id=source_id,
                               source_name=source_name,
                               author=author,
                               display_name=display_name,
                               title=title,
                               description=description,
                               url=url,
                               url_to_image=url_to_image,
                               published_at=published_at,
                               content=content)
    if author or title or description or content or url or url_to_image or published_at:
        create_post_search_index().save_object(tweet.to_index_dict())
    return jsonify({'message': 'Tweet updated successfully', 'tweet': tweet.to_dict()}), 200


@app.route('/admin/tweets/<int:tweet_id>', methods=['DELETE'])
@admin_required
def delete_tweet(tweet_id):
    """
    Delete a tweet by ID.
    """
    tweet = Tweet.get_tweet_by_id(tweet_id)
    if not tweet:
        return jsonify({'message': 'Tweet not found'}), 404

    Tweet.delete_tweet(tweet_id)
    create_post_search_index().delete_object(tweet.id)
    return jsonify({'message': 'Tweet deleted successfully'}), 200


@app.route('/admin/search/reindex', methods=['POST'])
@admin_required
def reindex_search():
    """
    Reindex all users and tweets.
    """
    # Reindex users
    users = User.get_all_users()
    user_index = create_user_search_index()
    user_index.clear_objects()
    user_index.save_objects([user.to_index_dict() for user in users])

    # Reindex tweets
    tweets = Tweet.get_all_tweets()
    tweet_index = create_post_search_index()
    tweet_index.clear_objects()
    tweet_index.save_objects([tweet.to_index_dict() for tweet in tweets])

    return jsonify({'message': 'Search reindexed successfully'}), 200
