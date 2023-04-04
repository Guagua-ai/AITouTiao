from app import app, puller
from flask import jsonify


@app.route('/collect', methods=['GET'])
def collect():
    puller.run()
    return jsonify({'message': 'Tweets collected and saved to ai_tweets_translated.csv'})