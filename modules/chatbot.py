from app import app, chatbot
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.user import User


@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user:
        return jsonify({'error': 'User not found'}), 404

    user_input = request.json.get('user_input')
    if not user_input:
        return jsonify({'error': 'User input is required'}), 400

    relevant_results = chatbot.run_with_response(user_input)
    return jsonify(relevant_results)


@app.route('/chat/count', methods=['GET'])
@jwt_required()
def count_total_records():
    current_user = User.get_user_by_id(get_jwt_identity())
    if not current_user:
        return jsonify({'error': 'User not found'}), 404

    count_total_records = chatbot.count_total_records()
    return jsonify({'count': count_total_records})
