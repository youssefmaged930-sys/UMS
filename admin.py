from flask import Blueprint, request, jsonify
from models import University, Administrator

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/', methods=['POST'])
def create_admin():
    data = request.get_json()
    university = University.get_instance()
    
    try:
        admin = Administrator(
            data['admin_id'],
            data['name'],
            data['email'],
            data.get('contact_phone')
        )
        university.users.append(admin)
        return jsonify(admin.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/<admin_id>/dashboard', methods=['GET'])
def view_dashboard(admin_id):
    university = University.get_instance()
    admin = university.get_admin(admin_id)
    
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    if not admin.logged_in:
        return jsonify({'error': 'Please login first'}), 401
    
    return jsonify(admin.to_dict()), 200