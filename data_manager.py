import os
import pickle

from flask import Blueprint, jsonify
from models import University, Library

data_bp = Blueprint('data_manager', __name__)

@data_bp.route('/save', methods=['POST'])
def save_data():
    try:
        university = University.get_instance()
        print("Saving data - Current classrooms:", university.classrooms)  # Debug log
        
        data = {
            "users": university.users,
            "courses": university.courses,
            "departments": university.departments,
            "exams": getattr(university, 'exams', []),
            "library": getattr(university, 'library', Library("LIB-01")),
            "classrooms": getattr(university, 'classrooms', {}),  # Ensure classrooms is a dictionary
            "schedules": getattr(university, 'schedules', [])
        }
        print("Data to be saved:", data)  # Debug log
        
        with open("university_data.pkl", "wb") as f:
            pickle.dump(data, f)
        return jsonify({
                'message': 'Data saved successfully',
            }), 201
    except Exception as e:
        print("Error saving data:", str(e))  # Debug log
        return jsonify({'error': str(e)}), 500

def load_data():
    try:
        if os.path.exists("university_data.pkl"):
            print("Loading data from university_data.pkl")  # Debug log
            with open("university_data.pkl", "rb") as f:
                data = pickle.load(f)
            print("Loaded data:", data)  # Debug log
            
            university = University.get_instance()
            university.users = data.get("users", [])
            university.courses = data.get("courses", [])
            university.departments = data.get("departments", [])
            university.exams = data.get("exams", [])
            university.library = data.get("library", Library("LIB-01"))
            university.classrooms = data.get("classrooms", {})  # Ensure classrooms is a dictionary
            university.schedules = data.get("schedules", [])
            
            print("University instance after loading:", university.classrooms)  # Debug log
            return data
        print("No saved data found")  # Debug log
        return {}
    except Exception as e:
        print("Error loading data:", str(e))  # Debug log
        return {}