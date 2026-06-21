from flask import Blueprint, request, jsonify
from models import University, Professor

professors_bp = Blueprint('professors', __name__)

@professors_bp.route('/add', methods=['POST'])
def create_professor():
    data = request.get_json()
    university = University.get_instance()
    
    try:
        professor = Professor(
            professor_id=data['professorId'],
            name=data['name'],
            email=data['email'],
            department=data['department']
        )
        university.users.append(professor)
        return jsonify({
            'message': 'Professor created successfully',
            'professor': professor.to_dict()
        }), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@professors_bp.route('/<professor_id>/assign_grade', methods=['POST'])
def assign_grade(professor_id):
    data = request.get_json()
    university = University.get_instance()
    
    try:
        # Validate required fields
        if not data or 'studentId' not in data or 'courseId' not in data or 'grade' not in data:
            return jsonify({'error': 'Missing required fields: studentId, courseId, and grade are required'}), 400

        # Validate grade format
        valid_grades = ['A', 'B', 'C', 'D', 'F']
        if data['grade'] not in valid_grades:
            return jsonify({'error': 'Invalid grade format. Must be one of: A, B, C, D, F'}), 400

        # Get and validate professor
        professor = university.get_professor(professor_id)
        if not professor:
            return jsonify({'error': 'Professor not found'}), 404
            
        # Get and validate student
        student = university.get_student(data['studentId'])
        if not student:
            return jsonify({'error': 'Student not found'}), 404
            
        # Get and validate course
        course = university.get_course(data['courseId'])
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        # Validate professor teaches the course
        if course.professor != professor:
            return jsonify({'error': 'Professor is not teaching this course'}), 403

        # Validate student is enrolled in the course
        if student not in course.enrolled_students:
            return jsonify({'error': 'Student is not enrolled in this course'}), 400

        # Assign the grade
        student.update_grade(course.course_id, data['grade'])
        return jsonify({'message': f'Successfully assigned grade {data["grade"]} to {student.name} for {course.name}'}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@professors_bp.route('/<prof_id>/dashboard', methods=['GET'])
def view_dashboard(prof_id):
    university = University.get_instance()
    professor = university.get_professor(prof_id)
    
    if not professor:
        return jsonify({'error': 'Professor not found'}), 404
    
    # Calculate statistics
    total_courses = len(professor.courses_taught)
    total_students = sum(len(course.enrolled_students) for course in university.courses 
                        if course.professor and course.professor.user_id == prof_id)
    
    # Get course details
    courses_teaching = []
    for course in university.courses:
        if course.professor and course.professor.user_id == prof_id:
            # Calculate average grade for this course
            grades = []
            for student in course.enrolled_students:
                if course.course_id in student.grades:
                    grade = student.grades[course.course_id]
                    if grade == 'A': grades.append(95)
                    elif grade == 'B': grades.append(85)
                    elif grade == 'C': grades.append(75)
                    elif grade == 'D': grades.append(65)
                    elif grade == 'F': grades.append(55)
            
            avg_grade = sum(grades)/len(grades) if grades else None
            
            courses_teaching.append({
                'code': course.course_id,
                'name': course.name,
                'students': len(course.enrolled_students),
                'avg_grade': letter_grade(avg_grade) if avg_grade else 'N/A'
            })
    
    dashboard_data = {
        'prof_id': professor.user_id,
        'name': professor.name,
        'email': professor.email,
        'department': professor.department,
        'total_courses': total_courses,
        'total_students': total_students,
        'courses_teaching': courses_teaching
    }
    return jsonify(dashboard_data), 200

def letter_grade(score):
    if score >= 90: return 'A'
    if score >= 80: return 'B'
    if score >= 70: return 'C'
    if score >= 60: return 'D'
    return 'F'

@professors_bp.route('/list', methods=['GET'])
def list_professors():
    university = University.get_instance()
    professors = [user for user in university.users if isinstance(user, Professor)]
    return jsonify([professor.to_dict() for professor in professors]), 200

@professors_bp.route('/assign-professor-to-course', methods=['POST'])
def assign_professor_to_course():
    try:
        data = request.get_json()
        if not data or 'professorId' not in data or 'courseId' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        university = University.get_instance()
        professor = university.get_professor(data['professorId'])
        course = university.get_course(data['courseId'])

        if not professor:
            return jsonify({'error': 'Professor not found'}), 404
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        if course.professor:
            if course.professor.user_id == professor.user_id:
                return jsonify({'error': 'Professor is already assigned to this course'}), 400
            return jsonify({'error': 'Course already has an assigned professor'}), 400
            
        # Update both professor and course
        if course not in professor.courses_taught:
            professor.courses_taught.append(course)
        course.professor = professor
        
        return jsonify({
            'message': 'Professor assigned to course successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to assign professor to course: {str(e)}'}), 500

@professors_bp.route('/<prof_id>/courses', methods=['GET'])
def get_professor_courses(prof_id):
    try:
        university = University.get_instance()
        professor = university.get_professor(prof_id)
        
        if not professor:
            return jsonify({'error': 'Professor not found'}), 404
        
        courses = []
        for course in professor.courses_taught:
            course_dict = course.to_dict()
            course_dict['enrolled_students'] = len(course.enrolled_students)
            courses.append(course_dict)
            
        return jsonify({
            'professor': professor.to_dict(),
            'courses': courses
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get professor courses: {str(e)}'}), 500