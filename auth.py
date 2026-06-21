from flask import Blueprint, request, jsonify
from models import University

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')
    
    university = University.get_instance()
    user = None
    
    # Find user by ID
    for u in university.users:
        if u.user_id == user_id:
            user = u
            break
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.login(password):
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Login failed'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    user_id = data.get('user_id')
    
    university = University.get_instance()
    user = university.get_user(user_id)  # You'll need to implement this method
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.logout():
        return jsonify({'message': 'Logout successful'}), 200
    else:
        return jsonify({'error': 'Logout failed'}), 400