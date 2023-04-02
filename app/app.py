from functools import wraps
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from chat.chatbot import Chatbot
from pull.puller import Puller


load_dotenv('.env')

app = Flask(__name__)
CORS(app)
open_ai_api=os.getenv('OPENAI_API_KEY')
puller = Puller(api_key=open_ai_api, local=True)
chatbot = Chatbot(api_key=open_ai_api, local=True)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        since_id = request.args.get('since_id', type=int)

        # Allow request to proceed without a token if since_id is not provided
        if since_id is None:
            return f(*args, **kwargs)

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        elif token != 'your-token':  # Replace with your own token
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)
    return decorated



@app.route('/collect', methods=['GET'])
def collect():
    puller.run()
    return jsonify({'message': 'Tweets collected and saved to ai_tweets_translated.csv'})


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input')
    if not user_input:
        return jsonify({'error': 'User input is required'}), 400

    data = chatbot.read_csv('ai_tweets_translated.csv')
    relevant_results = chatbot.find_relevant_results(data, user_input)
    response = chatbot.format_results(relevant_results)

    return jsonify(response)


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

    tweet_data = chatbot.get_tweet_data()

    if since_id is not None:
        # Filter tweet_data based on the since_id
        tweet_data = [tweet for tweet in tweet_data if int(
            tweet['source']['id']) > since_id]

    # Paginate the tweet_data
    paginated_data = tweet_data[:per_page]

    response_packet = {
        "status": "ok",
        "totalResults": len(tweet_data),
        "perPage": per_page,
        "articles": paginated_data
    }

    # Add 'next_since_id' to the response_packet if there are more tweets available
    if len(paginated_data) < len(tweet_data):
        next_since_id = paginated_data[-1]['source']['id']
        response_packet['next_since_id'] = next_since_id

    return jsonify(response_packet)


@app.route('/count', methods=['GET'])
def count_total_records():
    relevant_results = chatbot.count_total_records()
    return jsonify({'count': relevant_results})
