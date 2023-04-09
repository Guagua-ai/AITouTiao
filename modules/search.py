from operator import or_
from app import app
from flask import jsonify, request
from models.tweet import Tweet
from models.user import User
from search.index import create_post_search_index, create_user_search_index


@app.route('/posts/search', methods=['GET'])
def search_tweets():
    # Get the search query from the request query parameters
    query = request.args.get('q')

    # Use the Algolia index to search for tweets that match the query
    results = create_post_search_index().search(query)

    # Get the tweet IDs from the search results
    tweet_ids = [result['objectID'] for result in results['hits']]

    # Get the tweets from the database using the tweet IDs
    tweets = Tweet.query.filter(Tweet.id.in_(tweet_ids)).all()

    # Return the tweets as a JSON response
    return jsonify([tweet.to_dict() for tweet in tweets])


@app.route('/search/users', methods=['GET'])
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