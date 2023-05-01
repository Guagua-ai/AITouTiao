import time
from app import app, puller, fm, fs
from flask import jsonify
from steps import PullStep
from modules.utils import admin_required

usernames = [
    'johnschulman2',
    'ilyasut',
    'reidhoffman',
    'peterthiel',
    'miramurati',
    'gdb',
    'chamath',
    'justinkan',
    'BigCodeProject',
    'harm_devries',
    'paulg',
    'Nicochan33',
    'sallyeaves',
    'erikbryn',
    'antgrasso',
    'kaggle',
    'Ronald_vanLoon',
    'TerenceLeungSF',
    'lexfridman',
    'ClementDelangue',
    'OfficialLoganK',
    'elonmusk',
    'Thom_Wolf',
    'AndrewYNg',
    'ID_AA_Carmack',
    'nigewillson',
    'sama',
    'ylecun',
    'karpathy',
    'goodfellow_ian',
    'demishassabis',
    'OpenAI',
    'DeepMind',
]


@app.route('/admin/collect', methods=['GET'])
@admin_required
def collect():
    for username in usernames:
        puller.run(usernames=[username])
        time.sleep(60)
    return jsonify({'message': 'Tweets collected'}), 200


@app.route('/admin/collect_async', methods=['GET'])
@admin_required
def collect_async():
    jobs = []
    for _, username in enumerate(usernames):
        job = fm.enqueue(PullStep([username]), job_timeout=36000)
        jobs.append(job)
    return jsonify({'Tweets collection started with job_ids': [job.id for job in jobs]}), 202


@app.route('/admin/collect_single_user/<string:username>', methods=['GET'])
@admin_required
def collect_single_user(username):
    if not username:
        return jsonify({'error': "Bad request. Missing or invalid 'username' in the URL path."}), 400
    puller.run(usernames=[username])
    return jsonify({'message': f'Tweets collected for {username}'}), 200


@app.route('/admin/collect_single_user_async/<string:username>', methods=['GET'])
@admin_required
def collect_single_user_async(username):
    if not username:
        return jsonify({'error': "Bad request. Missing or invalid 'username' in the URL path."}), 400
    job = fm.enqueue(PullStep([username]), job_timeout=36000)
    return jsonify({'message': f'Tweets collection started for {username} with job_id: {job.id}'}), 202