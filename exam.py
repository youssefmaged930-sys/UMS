from flask import Blueprint, request, jsonify
from models import University, Exam, Course, Classroom

exam_bp = Blueprint('exam', __name__)

@exam_bp.route('/schedule-exam', methods=['POST'])
def schedule_exam():
    try:
        data = request.get_json()
        exam_id = data.get('examId')
        course_id = data.get('courseId')
        date = data.get('examDate')
        duration = data.get('duration')
        classroom_id = data.get('classroomId')

        if not all([exam_id, course_id, date, duration, classroom_id]):
            return jsonify({"error": "Missing required fields"}), 400

        university = University.get_instance()
        
        # Get course and classroom
        course = university.get_course(course_id)
        classroom = university.get_classroom(classroom_id)
        
        if not course:
            return jsonify({"error": "Course not found"}), 404
        if not classroom:
            return jsonify({"error": "Classroom not found"}), 404

        # Create and schedule exam
        exam = Exam(exam_id, course, date, int(duration))
        success = exam.schedule_exam(classroom)
        
        if success:
            return jsonify({
                "message": f"Exam scheduled successfully",
                "exam": {
                    "id": exam_id,
                    "course": course.name,
                    "date": date,
                    "duration": duration,
                    "classroom": f"{classroom.location} (Room {classroom.classroom_id})"
                }
            }), 201
        else:
            return jsonify({"error": "Failed to schedule exam - classroom may be unavailable"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exam_bp.route('/record-result', methods=['POST'])
def record_result():
    try:
        data = request.get_json()
        exam_id = data.get('examId')
        student_id = data.get('studentId')
        grade = data.get('grade')

        if not all([exam_id, student_id, grade]):
            return jsonify({"error": "Missing required fields"}), 400

        university = University.get_instance()
        
        # Get student
        student = university.get_student(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        # Find exam
        exam = None
        for course in university.courses:
            if hasattr(course, 'exams'):
                for e in course.exams:
                    if e.exam_id == exam_id:
                        exam = e
                        break
            if exam:
                break

        if not exam:
            return jsonify({"error": "Exam not found"}), 404

        # Record result
        success = exam.record_results(student, grade)
        
        if success:
            return jsonify({
                "message": f"Grade recorded successfully",
                "result": {
                    "exam_id": exam_id,
                    "student_id": student_id,
                    "grade": grade
                }
            }), 200
        else:
            return jsonify({"error": "Failed to record grade - result may already exist"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exam_bp.route('/exam/<exam_id>', methods=['GET'])
def get_exam_info(exam_id):
    try:
        university = University.get_instance()
        
        # Find exam
        exam = None
        for course in university.courses:
            if hasattr(course, 'exams'):
                for e in course.exams:
                    if e.exam_id == exam_id:
                        exam = e
                        break
            if exam:
                break

        if not exam:
            return jsonify({"error": "Exam not found"}), 404

        # Calculate statistics
        num_students = len(exam.student_results)
        avg_grade = None
        if exam.student_results:
            numeric_grades = []
            for grade in exam.student_results.values():
                if isinstance(grade, (int, float)):
                    numeric_grades.append(grade)
                elif isinstance(grade, str) and grade.replace('.','',1).isdigit():
                    numeric_grades.append(float(grade))
            if numeric_grades:
                avg_grade = sum(numeric_grades)/len(numeric_grades)

        return jsonify({
            "id": exam_id,
            "course": exam.course.name,
            "date": exam.date,
            "duration": exam.duration,
            "students_completed": num_students,
            "average_grade": avg_grade if avg_grade is not None else "N/A"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500 