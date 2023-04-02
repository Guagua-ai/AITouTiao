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


@app.route('/count', methods=['GET'])
def count_total_records():
    relevant_results = chatbot.count_total_records()
    return jsonify({'count': relevant_results})
