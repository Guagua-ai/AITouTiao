import os
import requests
from app import app
from flask import jsonify
from db.storage import upload_image_to_s3
from models.user import User
from models.tweet import Tweet
from modules.utlis import admin_required, require_valid_user
from translator.core import TranslatorCore


@app.route('/admin/promote/<int:user_id>', methods=['POST'])
@require_valid_user
@admin_required
def promote_user(user_id):
    """
    Promote a user to admin.
    Expects a user ID parameter in the URL.
    """
    if user_id == current_user.id:
        return jsonify({'message': 'You cannot promote yourself'}), 400
    current_user = User.get_user_by_id(current_user.id)
    if not current_user.is_admin:
        return jsonify({'message': 'Admin required'}), 403

    user = User.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if user.is_admin:
        return jsonify({'message': 'User is already an admin'}), 400

    User.update_user(user_id, is_admin=True)
    return jsonify({'message': 'User promoted successfully'}), 200


@app.route('/admin/download_tweet_images', methods=['POST'])
@require_valid_user
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
@require_valid_user
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
