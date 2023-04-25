from operator import or_
from app import app
from flask import jsonify, request
from models.tweet import Tweet
from models.user import User
from modules.utils import require_valid_user
from search.index import create_post_search_index, create_user_search_index

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
    tweets = Tweet.get_tweets_by_ids(tweet_ids)

    # Convert the tweets to a dictionary with the tweet ID string as the key
    tweets_dict = {str(tweet.id): tweet for tweet in tweets}

    tweets = [
        tweets_dict[tweet_id].to_ext_dict() for tweet_id in tweet_ids
    ]

    # Return the tweets as a JSON response
    return jsonify(tweets), 200


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
                user_objects.append(user.to_ext_dict())
            else:
                create_user_search_index().delete_object(user_hit['objectID'])
    
    return jsonify(user_objects), 200
