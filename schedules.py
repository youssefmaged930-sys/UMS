import datetime
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import University, Schedule

schedules_bp = Blueprint('schedules', __name__)

@schedules_bp.route('/add', methods=['POST'])
def add_schedule():
    try:
        data = request.get_json()
        schedule_id = data.get("scheduleId")
        course_id = data.get("courseId")
        professor_id = data.get("professorId")
        time_slot = data.get("timeSlot")
        classroom_id = data.get("classroomId")
        date = data.get("date")

        # Check each field individually
        missing_fields = []
        if not schedule_id:
            missing_fields.append("Schedule ID")
        if not course_id:
            missing_fields.append("Course ID") 
        if not professor_id:
            missing_fields.append("Professor ID")
        if not time_slot:
            missing_fields.append("Time Slot")
        if not classroom_id:
            missing_fields.append("Classroom ID")
        if not date:
            missing_fields.append("Date")

        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        university = University.get_instance()
        
        # Get course and professor
        course = university.get_course(course_id)
        professor = university.get_professor(professor_id)
        classroom = university.get_classroom(classroom_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404
        if not professor:
            return jsonify({"error": "Professor not found"}), 404
        if not classroom:
            return jsonify({"error": "Classroom not found"}), 404


        # Create new schedule
        new_schedule = Schedule(
            schedule_id=schedule_id,
            course=course,
            professor=professor,
            time_slot=time_slot,
            classroom=classroom,
            date=date
        )

        # Assign schedule
        if new_schedule.assign_schedule():
            return jsonify({
                "message": f"Schedule {schedule_id} added successfully",
                "schedule": {
                    "id": schedule_id,
                    "course": course.name,
                    "professor": professor.name,
                    "timeSlot": time_slot,
                    "classroom": f"{classroom.location} (Room {classroom.classroom_id})",
                    "date": date
                }
            }), 200
        else:
            return jsonify({"error": "Schedule conflicts with existing schedule"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedules_bp.route('/list', methods=['GET'])
def list_schedules():
    try:
        university = University.get_instance()
        schedules = getattr(university, 'schedules', [])
        
        schedule_list = []
        for schedule in schedules:
            schedule_list.append({
                "schedule_id": schedule.schedule_id,
                "course": schedule.course.name,
                "professor": schedule.professor.name,
                "time_slot": schedule.time_slot,
                "classroom": f"{schedule.classroom.location} (Room {schedule.classroom.classroom_id})",
                "date": schedule.date
            })
        
        return jsonify({"schedules": schedule_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedules_bp.route('/<schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    try:
        university = University.get_instance()
        schedules = getattr(university, 'schedules', [])
        
        for schedule in schedules:
            if schedule.schedule_id == schedule_id:
                return jsonify({
                    "schedule_id": schedule.schedule_id,
                    "course": schedule.course.name,
                    "professor": schedule.professor.name,
                    "time_slot": schedule.time_slot,
                    "classroom": f"{schedule.classroom.location} (Room {schedule.classroom.classroom_id})",
                    "date": schedule.date
                }), 200
        
        return jsonify({"error": "Schedule not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedules_bp.route('/update/<schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    try:
        data = request.get_json()
        new_time_slot = data.get("time_slot")
        new_classroom = data.get("classroom") 
        new_date = data.get("date")

        if not any([new_time_slot, new_classroom, new_date]):
            return jsonify({"error": "No update fields provided"}), 400

        university = University.get_instance()
        schedules = getattr(university, 'schedules', [])
        
        for schedule in schedules:
            if schedule.schedule_id == schedule_id:
                if new_classroom:
                    classroom = university.get_classroom(new_classroom)
                    if not classroom:
                        return jsonify({"error": "Classroom not found"}), 404
                    
                if schedule.update_schedule(new_time_slot, classroom if new_classroom else None, new_date):
                    return jsonify({
                        "message": f"Schedule {schedule_id} updated successfully",
                        "schedule": {
                            "schedule_id": schedule.schedule_id,
                            "course": schedule.course.name,
                            "professor": schedule.professor.name,
                            "time_slot": schedule.time_slot,
                            "classroom": f"{schedule.classroom.location} (Room {schedule.classroom.classroom_id})",
                            "date": schedule.date
                        }
                    }), 200
                else:
                    return jsonify({"error": "Failed to update schedule"}), 400
        
        return jsonify({"error": "Schedule not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500