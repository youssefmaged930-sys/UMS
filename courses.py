from flask import Blueprint, request, jsonify
from models import University, Course

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/add', methods=['POST'])
def create_course():
    data = request.get_json()
    university = University.get_instance()
    
    try:
        course = Course(
            course_id=data['courseId'],
            name=data['courseName'],
            department=data['department'],
            credits=data['credits']
        )
        university.courses.append(course)
        return jsonify({
            'message': 'Course created successfully',
            'course': course.to_dict()
        }), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    university = University.get_instance()
    course = university.get_course(course_id)
    
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    return jsonify(course.to_dict()), 200

@courses_bp.route('/list', methods=['GET'])
def list_courses():
    university = University.get_instance()
    courses = university.courses
    return jsonify([course.to_dict() for course in courses]), 200