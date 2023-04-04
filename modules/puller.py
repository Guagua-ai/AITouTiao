from app import app, puller
from flask import jsonify
from jobqueue import q

@app.route('/collect', methods=['GET'])
def collect():
    puller.run()
    return jsonify({'message': 'Tweets collected and saved to ai_tweets_translated.csv'})


@app.route('/collect_async', methods=['GET'])
def collect_async():
    job = q.enqueue(puller.run)
    return jsonify({'Tweets collection started with job_id': job.get_id()}), 202
