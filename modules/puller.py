from app import app, puller, q
from flask import jsonify
from steps import PullStep
from modules.utlis import admin_required, require_valid_user

usernames = ['elonmusk', 'sama', 'ylecun']

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
    # jobs = []
    # for username in usernames:
    #     jobs.append(q.enqueue(PullStep([username]), job_timeout=36000))
    # return jsonify({'Tweets collection started with job_ids': [job.id for job in jobs]}), 202
    job = q.enqueue(PullStep(usernames), job_timeout=36000)
    return jsonify({'Tweets collection started with job_ids': job.id}), 202
