from flask import Blueprint, request, jsonify
from models import University, Student

students_bp = Blueprint('students', __name__)

@students_bp.route('/add', methods=['POST'])
def create_student():
    data = request.get_json()
    university = University.get_instance()
    
    try:
        student = Student(
            student_id=data['studentId'],
            name=data['name'],
            email=data['email'],
            major=data['major']
        )
        university.users.append(student)
        response_data = {
            'student_id': student.user_id,
            'name': student.name,
            'email': student.email,
            'major': student.major
        }
        return jsonify({
            'message': 'Student created successfully',
            'student': response_data
        }), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @students_bp.route('/<student_id>/dashboard', methods=['GET'])
# def view_dashboard(student_id):
#     university = University.get_instance()
#     student = university.get_student(student_id)
    
#     if not student:
#         return jsonify({'error': 'Student not found'}), 404
    
#     dashboard_data = {
#         'student_id': student.user_id,
#         'name': student.name,
#         'email': student.email,
#         'major': getattr(student, 'major', 'N/A'),
#         'courses_enrolled': getattr(student, 'courses_enrolled', []),
#         'grades': getattr(student, 'grades', {})
#     }
#     return jsonify(dashboard_data), 200

@students_bp.route('/<student_id>/dashboard', methods=['GET'])
def view_dashboard(student_id):
    university = University.get_instance()
    student = university.get_student(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    enrolled_courses = []
    for course_id in student.courses_enrolled:
        course = university.get_course(course_id)
        if course:
            enrolled_courses.append({
                'id': course.course_id,
                'name': course.name,
                'grade': student.grades.get(course_id, 'N/A')
            })
    
    dashboard_data = {
        'student_id': student.user_id,
        'name': student.name,
        'email': student.email,
        'major': student.major,
        'courses_enrolled': enrolled_courses,
        'total_courses': len(enrolled_courses)
    }
    return jsonify(dashboard_data), 200
    

@students_bp.route('/<student_id>/enroll', methods=['POST'])
def enroll_student(student_id):
    data = request.get_json()
    course_id = data['courseId']
    university = University.get_instance()
    
    try:
        student = university.get_student(student_id)
        course = university.get_course(course_id)
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        if student.enroll_course(course):
            return jsonify({
                'message': f'Student enrolled successfully'
            }), 200
        else:
            return jsonify({'error': 'Student already enrolled in this course'}), 400
            
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@students_bp.route('/<student_id>/register-library', methods=['POST'])
def register_student_to_library(student_id):
    university = University.get_instance()
    
    try:
        student = university.get_student(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
            
        library = university.library
        if library.register_student(student):
            return jsonify({
                'message': f'Student {student.name} registered to library successfully'
            }), 200
        else:
            return jsonify({'error': 'Student already registered in library'}), 400
            
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500