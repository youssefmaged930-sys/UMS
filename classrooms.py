import datetime
from flask import Blueprint, request, jsonify
from models import University, Classroom

classrooms_bp = Blueprint('classrooms', __name__)

@classrooms_bp.route('/add', methods=['POST']) 
def add_classroom():
    try:
        data = request.get_json()
        classroom_id = data.get("classroomId")
        location = data.get("location")
        capacity = data.get("capacity")

        if not all([classroom_id, location, capacity]):
            return jsonify({"error": "Missing required fields"}), 400

        university = University.get_instance()
        
        # Check if classroom ID already exists
        if classroom_id in university.classrooms:
            return jsonify({"error": "Classroom ID already exists"}), 400

        # Create new classroom
        new_classroom = Classroom(
            classroom_id=classroom_id,
            location=location, 
            capacity=capacity
        )

        # Add to university
        university.add_classroom(new_classroom)

        return jsonify({"message": f"Classroom {classroom_id} added successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@classrooms_bp.route('/list', methods=['GET'])
def list_classrooms():
    try:
        university = University.get_instance()
        classrooms = university.classrooms
        
        classroom_list = []
        for classroom in classrooms:
            classroom_list.append({
                "classroom_id": classroom.classroom_id,
                "location": classroom.location,
                "capacity": classroom.capacity
            })
        
        return jsonify({"classrooms": classroom_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@classrooms_bp.route('/<classroom_id>', methods=['GET'])
def get_classroom(classroom_id):
    try:
        university = University.get_instance()
        classroom = university.get_classroom(classroom_id)
        if classroom:
            return jsonify({
                "classroom_id": classroom.classroom_id,
                "location": classroom.location,
                "capacity": classroom.capacity
            }), 200
        else:
            return jsonify({"error": "Classroom not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@classrooms_bp.route('/allocate', methods=['POST'])
def allocate_classroom():
    try:
        data = request.get_json()
        classroom_id = data.get("classroomId")
        date = data.get("date") 
        time_slot = data.get("timeSlot")

        # Validate required fields
        if not all([classroom_id, date, time_slot]):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate date format and check if date is in the future
        try:
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
            today = datetime.datetime.now().date()
            if date_obj.date() < today:
                return jsonify({"error": "Cannot allocate classroom for past dates"}), 400
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        university = University.get_instance()
        classroom = university.get_classroom(classroom_id)
        if not classroom:
            return jsonify({"error": "Classroom not found"}), 404
        
        # Check if classroom is already allocated for the given date and time
        if classroom.is_allocated(date, time_slot):
            return jsonify({"error": "Classroom already allocated for the given date and time"}), 400
        
        # Initialize schedule for date if not exists
        if date not in classroom.schedule:
            classroom.schedule[date] = []
            
        # Allocate classroom
        classroom.allocate(date, time_slot)
        
        return jsonify({
            "message": f"Classroom {classroom_id} allocated for {date} at {time_slot}",
            "classroom": {
                "id": classroom_id,
                "location": classroom.location,
                "date": date,
                "timeSlot": time_slot
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
