import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from chat.chatbot import Chatbot
from pull.puller import Puller


load_dotenv('.env')
print(os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)
open_ai_api=os.getenv('OPENAI_API_KEY')
puller = Puller(api_key=open_ai_api, local=True)
chatbot = Chatbot(api_key=open_ai_api, local=True)

@app.route('/collect', methods=['GET'])
def collect():
    puller.run()
    return jsonify({'message': 'Tweets collected and saved to elonmusk_tweets_translated.csv'})

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input')
    if not user_input:
        return jsonify({'error': 'User input is required'}), 400

    data = chatbot.read_csv('elonmusk_tweets_translated.csv')
    relevant_results = chatbot.find_relevant_results(data, user_input)
    response = chatbot.format_results(relevant_results)

    return jsonify(response)
