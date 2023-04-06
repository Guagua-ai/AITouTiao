from app import app, chatbot
from flask import request, jsonify


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input')
    if not user_input:
        return jsonify({'error': 'User input is required'}), 400

    data = chatbot.read_csv('ai_tweets_translated.csv')
    relevant_results = chatbot.find_relevant_results(data, user_input)
    response = chatbot.format_results(relevant_results)

    return jsonify(response)


@app.route('/count', methods=['GET'])
def count_total_records():
    relevant_results = chatbot.count_total_records()
    return jsonify({'count': relevant_results})
