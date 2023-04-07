from app import app
from flask import jsonify
from models.user import User
from modules.utlis import admin_required, require_valid_user, current_user


@app.route('/admin/promote/<int:user_id>', methods=['POST'])
@require_valid_user
@admin_required
def promote_user(user_id):
    """
    Promote a user to admin.
    Expects a user ID parameter in the URL.
    """
    if user_id == current_user.id:
        return jsonify({'message': 'You cannot promote yourself'}), 400
    current_user = User.get_user_by_id(current_user.id)
    if not current_user.is_admin:
        return jsonify({'message': 'Admin required'}), 403

    user = User.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if user.is_admin:
        return jsonify({'message': 'User is already an admin'}), 400

    User.update_user(user_id, is_admin=True)
    return jsonify({'message': 'User promoted successfully'}), 200
