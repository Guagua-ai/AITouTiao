from operator import or_
from app import app
from flask import jsonify, request
from models.tweet import Tweet
from models.user import User
from modules.utils import require_valid_user
from search.index import create_post_search_index, create_user_search_index
from utils.time import standard_format


@app.route('/search/posts', methods=['GET'])
def search_tweets():
    # Get the search query from the request query parameters
    query = request.args.get('q')

    # Define the search parameters, including the fuzzy search query and settings
    request_options = {
        "query": query,
        "typoTolerance": "true",
        "minWordSizefor1Typo": 4,
        "minWordSizefor2Typos": 8,
        "ignorePlurals": "true",
        "advancedSyntax": "true",
        "page": 0,
        "hitsPerPage": 20,
    }

    # Use the Algolia index to search for tweets that match the query
    results = create_post_search_index().search(query, request_options)

    # Get the tweet IDs from the search results
    tweet_ids = [result['objectID'] for result in results['hits']]

    # Get the tweets from the database using the tweet IDs
    tweets = Tweet.query.filter(Tweet.id.in_(tweet_ids)).all()

    tweets = [
        {
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
            "content": '',
            "likes": tweet.num_likes,
        } for tweet in Tweet.query.filter(Tweet.id.in_(tweet_ids)).all()
    ]

    # Return the tweets as a JSON response
    return jsonify({
        "numResults": len(tweets),
        "tweets": tweets,
    }), 200


@app.route('/search/users', methods=['GET'])
@require_valid_user
def search_users():
    query = request.args.get('q', '')

    # Search for users
    user_results = create_user_search_index().search(query, {'hitsPerPage': 10})

    # Retrieve the associated user objects from the database
    user_objects = []
    with app.app_context():
        for user_hit in user_results['hits']:
            user = User.query.filter_by(id=user_hit['objectID']).first()
            if user:
                user_objects.append(user.to_dict())
    
    return jsonify(user_objects)