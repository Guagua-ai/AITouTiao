from app import app, puller, q
from flask import jsonify
from steps import PullStep
from modules.utils import admin_required

usernames = [
            #  'lexfridman',
              'ClementDelangue',
              'OfficialLoganK',
            #  'elonmusk',
            #  'sama',
            #  'ylecun',
            #  'karpathy',
              'goodfellow_ian',
            #  'demishassabis',
            #  'OpenAI',
            #  'DeepMind',
             ]


@app.route('/admin/collect', methods=['GET'])
@admin_required
def collect():
    for username in usernames:
        puller.run(usernames=[username])
    return jsonify({'message': 'Tweets collected'}), 200


@app.route('/admin/collect_async', methods=['GET'])
@admin_required
def collect_async():
    jobs = []
    # for username in usernames:
    #     jobs.append(q.enqueue(PullStep([username]), job_timeout=36000))
    jobs.append(q.enqueue(PullStep(usernames), job_timeout=36000))
    return jsonify({'Tweets collection started with job_ids': [job.id for job in jobs]}), 202
