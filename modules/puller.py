from app import app, puller, q
from flask import jsonify
from modules.utlis import admin_required, require_valid_user
from steps.pull_step import PullStep

@app.route('/collect', methods=['GET'])
@require_valid_user
@admin_required
def collect():
    puller.run()
    return jsonify({'message': 'Tweets collected'})


@app.route('/collect_async', methods=['GET'])
@require_valid_user
@admin_required
def collect_async():
    job = q.enqueue(PullStep(), job_timeout=36000)
    return jsonify({'Tweets collection started with job_id': job.get_id()}), 202
