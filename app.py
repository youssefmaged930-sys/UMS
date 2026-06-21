from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from auth import auth_bp
from students import students_bp
from professors import professors_bp
from courses import courses_bp
from admin import admin_bp
from models import University
from data_manager import load_data, save_data
from data_manager import data_bp
from classrooms import classrooms_bp
from schedules import schedules_bp
from library import library_bp
from exam import exam_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Load initial data
    if not load_data():
        # Initialize with empty data if no saved data exists
        University.get_instance()
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp, url_prefix='/students')
    app.register_blueprint(professors_bp, url_prefix='/professors')
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(data_bp, url_prefix='/data_manager')
    app.register_blueprint(classrooms_bp, url_prefix='/classrooms')
    app.register_blueprint(schedules_bp, url_prefix='/schedules')
    app.register_blueprint(library_bp, url_prefix='/library')
    app.register_blueprint(exam_bp, url_prefix='/exam')

    @app.route('/')
    def dashboard():
        return render_template('index.html')
    
    @app.route('/login.html')
    def login_page():
        return render_template('index.html')
    
    @app.route('/admin')
    def admin_workspace():
        return render_template('login.html')
    
    @app.route('/librarian-dashboard.html')
    def librarian_dashboard():
        return render_template('librarian-dashboard.html')

    @app.route('/student-dashboard.html')
    def student_dashboard():
        return render_template('student-dashboard.html')

    @app.route('/prof-dashboard.html')
    def prof_dashboard():
        return render_template('prof-dashboard.html')

    @app.route('/add-student.html')
    def add_student_page():
        return render_template('add-student.html')
    
    @app.route('/add-professor.html')
    def add_professor_page():
        return render_template('add-professor.html')
    
    @app.route('/add-course.html')
    def add_course_page():
        return render_template('add-course.html')
    
    @app.route('/enroll-student-in-course.html')
    def enroll_student_in_course_page():
        return render_template('enroll-student-in-course.html')
    
    @app.route('/add-book.html')
    def add_book_page():
        return render_template('add-book.html')
    
    @app.route('/add-classroom.html')
    def add_classroom_page():
        return render_template('add-classroom.html')
    
    @app.route('/allocate-time-to-classroom.html')
    def allocate_time_to_classroom_page():
        return render_template('allocate-time-to-classroom.html')
    
    @app.route('/admin-login.html')
    def admin_login_page():
        return render_template('admin-login.html')
    
    @app.route('/admin-dashboard.html')
    def admin_dashboard_page():
        return render_template('admin-dashboard.html')
    
    @app.route('/assign-grade.html')
    def assign_grade_page():
        return render_template('assign-grade.html')
    
    @app.route('/assign-professor-to-course.html')
    def assign_professor_to_course_page():
        return render_template('assign-professor-to-course.html')
    
    @app.route('/assign-schedule.html')
    def assign_schedule_page():
        return render_template('assign-schedule.html')
    
    @app.route('/borrow-book.html')
    def borrow_book_page():
        return render_template('borrow-book.html')
    
    @app.route('/professor-dashboard.html')
    def professor_dashboard_page():
        return render_template('professor-dashboard.html')
    
    @app.route('/record-exam-result.html')
    def record_exam_result_page():
        return render_template('record-exam-result.html')
    
    @app.route('/register-student.html')
    def register_student_page():
        return render_template('register-student.html')
    
    @app.route('/return-book.html')
    def return_book_page():
        return render_template('return-book.html')
    
    @app.route('/schedule-exam.html')
    def schedule_exam_page():
        return render_template('schedule-exam.html')
    
    @app.route('/view-classroom-info.html')
    def view_classroom_info_page():
        return render_template('view-classroom-info.html')
    
    @app.route('/view-exam-info.html')
    def view_exam_info_page():
        return render_template('view-exam-info.html')
    
    @app.route('/view-schedule-details.html')
    def view_schedule_details_page():
        return render_template('view-schedule-details.html')
    
    @app.route('/view-student-dashboard.html')
    def view_student_dashboard_page():
        return render_template('view-student-dashboard.html')
    
    @app.route('/student-login.html')
    def student_login():
        return render_template('student-login.html')
    
    @app.route('/professor-login.html')
    def professor_login():
        return render_template('professor-login.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)