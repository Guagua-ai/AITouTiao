from app import app, chatbot
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from models.user import User
from modules.utils import require_valid_user


@app.route('/chat', methods=['POST'])
@require_valid_user
def chat():
    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user:
        return jsonify({'error': 'User not found'}), 404

    user_input = request.json.get('user_input')
    if not user_input:
        return jsonify({'error': 'User input is required'}), 400

    relevant_results = chatbot.run_with_response(user_input)
    return jsonify(relevant_results), 200


@app.route('/chat/count', methods=['GET'])
@require_valid_user
def count_total_records():
    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user:
        return jsonify({'error': 'User not found'}), 404

    count_total_records = chatbot.count_total_records()
    return jsonify({'count': count_total_records}), 200
