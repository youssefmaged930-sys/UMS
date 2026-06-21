from abc import ABC, abstractmethod
from multipledispatch import dispatch

class GradeUpdateProxy:
    """Protected Proxy: Controls grade update access"""
    def init(self, real_student, professor):
        self.real_student = real_student  # Original Student object
        self.professor = professor        # Professor attempting grade update
    
    def update_grade(self, course_name, grade):
        """Proxy method with authorization check"""
        if course_name not in self.professor.courses_taught:
            print(f"❌ Professor {self.professor.name} cannot grade {course_name}")
            return False
        return self.real_student.update_grade(course_name, grade)

class User(ABC):
    def __init__(self, user_id, name, role, email):
        try:
            if not isinstance(user_id, (int, str)) or not user_id:
                raise ValueError("Invalid user ID")
            if not name or not isinstance(name, str):
                raise ValueError("Invalid name")
            if not role or not isinstance(role, str):
                raise ValueError("Invalid role")
            if not email or "@" not in email:
                raise ValueError("Invalid email format")
                
            self.user_id = user_id
            self.name = name
            self.role = role
            self.email = email
            self.logged_in = False
        except ValueError as e:
            print(f"User initialization failed: {e}")
            raise

    def login(self, password):
        try:
            if not password or not isinstance(password, str):
                raise ValueError("Password cannot be empty")
                
            self.logged_in = True
            print(f"{self.role} {self.name} logged in")
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            self.logged_in = False
            return False

    def logout(self):
        try:
            if not self.logged_in:
                raise RuntimeError("User is not logged in")
                
            self.logged_in = False
            print(f"{self.name} logged out")
            return True
        except Exception as e:
            print(f"Logout failed: {e}")
            return False

    @abstractmethod
    def view_dashboard(self):
        pass

class Student(User):
    def __init__(self, student_id, name, email, major):
        super().__init__(student_id, name, "student", email)
        self.major = major
        self.courses_enrolled = []
        self.grades = {}
        self.libraryRegistered = False
        self.borrowed_books = []

    def is_enrolled_in_course(self, course_id):
        return course_id in self.courses_enrolled

    def update_grade(self, course_id, grade):
        if not self.is_enrolled_in_course(course_id):
            return False
        self.grades[course_id] = grade
        return True

    def get_grade(self, course_id):
        return self.grades.get(course_id)

    def view_dashboard(self):
        if not self.logged_in:
            print("Please login first")
            return False
        
        print(f"""
        STUDENT DASHBOARD
        ID: {self.user_id}
        Name: {self.name}
        Major: {self.major}
        Courses Enrolled: {len(self.courses_enrolled)}
        """)
        self.view_grades()
        return True

    def enroll_course(self, course):
        if not isinstance(course, Course):
            raise ValueError("Must provide a Course object")
        
        if course.course_id not in self.courses_enrolled:
            self.courses_enrolled.append(course.course_id)
            self.grades[course.course_id] = None  # Initialize grade
            course.enrolled_students.append(self)
            return f"Enrolled in {course.course_id}"
        return f"Already enrolled in {course.course_id}"
    
    def drop_course(self, course_name):
        if course_name in self.courses_enrolled:
            self.courses_enrolled.remove(course_name)
            del self.grades[course_name]
            print(f"Successfully dropped {course_name}")
            return f"Successfully dropped {course_name}"
        return f"Not enrolled in {course_name}"

    def view_grades(self):
        if not self.grades:
            return "No courses enrolled or grades recorded yet."
        else:
            result = "Grades:\n"
            for course, grade in self.grades.items():
                result += f"{course}: {grade if grade is not None else 'No grade yet'}\n"
            return result

    def update_grade(self, course_name, grade):
        if course_name in self.courses_enrolled:
            self.grades[course_name] = grade
            return f"Grade updated to {grade} for {course_name}"
        return f"Cannot update grade - not enrolled in {course_name}"

    def get_info(self):
        self.view_dashboard()

    def __str__(self):
        return f"Student({self.user_id}, {self.name}, {self.major})"

    def to_dict(self):
        return {
            'student_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'major': self.major,
            'courses_enrolled': self.courses_enrolled,
            'grades': self.grades
        }

class Professor(User):
    def __init__(self, professor_id, name, email, department):
        super().__init__(professor_id, name, "professor", email)
        self.department = department
        self.courses_taught = []
        self.students = {}

    def view_dashboard(self):
        if not self.logged_in:
            print("Please login first")
            return False
        
        total_students = sum(len(students) for students in self.students.values())
        
        print(f"""
        PROFESSOR DASHBOARD
        ID: {self.user_id}
        Name: {self.name}
        Department: {self.department}
        Courses Teaching: {len(self.courses_taught)}
        Total Students: {total_students}
        """)

    def assign_grade(self, student, course_id, grade):
        return student.update_grade(course_id, grade)

    def add_course(self, course):
        if course.course_id not in self.courses_taught:
            self.courses_taught.append(course.course_id)
            self.students[course.course_id] = []
            return True
        return False

    def view_students(self, course_name=None):
        if not self.logged_in:
            print("Please login first")
            return False

        if course_name:
            if course_name in self.students:
                print(f"Students in {course_name}:")
                for student in self.students[course_name]:
                    print(f"- {student.name} (ID: {student.user_id})")
            else:
                print(f"No students in {course_name}")
        else:
            print("All your students:")
            for course, student_list in self.students.items():
                print(f"\n{course}:")
                for student in student_list:
                    print(f"- {student.name} (ID: {student.user_id})")

    def to_dict(self):
        return {
            'professor_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'courses_taught': self.courses_taught
        }

class Course:
    def __init__(self, course_id, name, department, credits):
        self.course_id = course_id
        self.name = name
        self.department = department
        self.credits = credits
        self.enrolled_students = []
        self.professor = None

    def add_student(self, student):
        if student in self.enrolled_students:
            print(f"{student.name} is already enrolled in {self.name}")
            return
        self.enrolled_students.append(student)
        if self.name not in student.courses_enrolled:
            student.courses_enrolled.append(self.name)
        print(f"Added {student.name} to {self.name}")

    def remove_student(self, student):
        if student not in self.enrolled_students:
            print(f"{student.name} is not enrolled in {self.name}")
            return
        self.enrolled_students.remove(student)
        if self.name in student.courses_enrolled:
            student.courses_enrolled.remove(self.name)
        print(f"Removed {student.name} from {self.name}")

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'name': self.name,
            'department': self.department,
            'credits': self.credits,
        }

    def get_course_info(self):
        professor_name = self.professor.name if self.professor else "Not assigned"
        student_names = [s.name for s in self.enrolled_students]
        
        info = f"""
        COURSE INFORMATION:
        ID: {self.course_id}
        Name: {self.name}
        Department: {self.department}
        Credits: {self.credits}
        Professor: {professor_name}
        Enrolled Students ({len(student_names)}): {', '.join(student_names) if student_names else 'None'}
        """
        print(info)

    def assign_professor(self, professor):
        if self.professor:
            print(f"{self.name} is already taught by {self.professor.name}")
            return
        self.professor = professor
        if self not in professor.courses_taught:
            professor.courses_taught.append(self)
        print(f"Assigned {professor.name} to teach {self.name}")

class CourseProxy:
    def _init_(self, course_id, name, department, credits):
        self._course_id = course_id
        self._name = name
        self._department = department
        self._credits = credits
        self._real_course = None  # The actual course (not created yet)

    def _getattr_(self, name):
        if self._real_course is None:
            self._real_course = Course(self._course_id, self._name, self._department, self._credits)
        return getattr(self._real_course, name)

class Department:
    def __init__(self, department_id, name, head_of_department):
        self.department_id = department_id
        self.name = name
        self.head_of_department = head_of_department
        self.courses_offered = []  # List of Course objects
        self.faculty_members = []  # List of Professor objects

    def get_department_info(self):
        info = f"""
        DEPARTMENT INFORMATION:
        ID: {self.department_id}
        Name: {self.name}
        Head: {self.head_of_department}
        Courses Offered: {len(self.courses_offered)}
        Faculty Members: {len(self.faculty_members)}
        """
        print(info)

    def list_courses(self):
        if not self.courses_offered:
            print("No courses offered in this department")
            return
        
        print(f"\nCourses Offered in {self.name}:")
        for course in self.courses_offered:
            print(f"- {course.name} (ID: {course.course_id}, Credits: {course.credits})")

    def list_professors(self):
        if not self.faculty_members:
            print("No faculty members in this department")
            return
        
        print(f"\nFaculty Members in {self.name}:")
        for professor in self.faculty_members:
            print(f"- {professor.name} (ID: {professor.professor_id})")

    def add_course(self, course):
        if course not in self.courses_offered:
            self.courses_offered.append(course)
            print(f"Added course: {course.name}")
        else:
            print(f"Course {course.name} already exists in department")

    def add_professor(self, professor):
        if professor not in self.faculty_members:
            self.faculty_members.append(professor)
            print(f"Added faculty member: {professor.name}")
        else:
            print(f"Professor {professor.name} already in department")

class Administrator(User):
    def __init__(self, admin_id, name, email, contact_phone=None):
        super().__init__(admin_id, name, "admin", email)
        self.admin_id = admin_id
        self.contact_info = {
            'email': email,
            'phone': contact_phone if contact_phone else 'N/A'
        }
        self.privileges = [
            "manage_users",
            "edit_courses",
            "override_grades",
            "modify_schedules"
        ]

    def view_dashboard(self):
        if not self.logged_in:
            print("Please login first")
            return False
        
        print(f"""
        ADMIN DASHBOARD
        ID: {self.admin_id}
        Name: {self.name}
        Role: {self.role}
        Contact: {self.contact_info['email']} | {self.contact_info['phone']}
        Privileges: {', '.join(self.privileges)}
        """)
        return True

    @dispatch(object, object)
    def add_student(self, student, course):
        if not self.logged_in:
            print("Please login first")
            return False
            
        if student in course.enrolled_students:
            print(f"{student.name} already enrolled in {course.name}")
            return False
            
        course.enrolled_students.append(student)
        student.courses_enrolled.append(course.name)
        print(f"Added {student.name} to {course.name}")
        return True

    @dispatch(object)
    def add_student(self, student):
        print("Error: No course specified")
        return False

    @dispatch(object, object)
    def remove_student(self, student, course):
        if not self.logged_in:
            print("Please login first")
            return False
            
        if student not in course.enrolled_students:
            print(f"{student.name} not enrolled in {course.name}")
            return False
            
        course.enrolled_students.remove(student)
        if course.name in student.courses_enrolled:
            student.courses_enrolled.remove(course.name)
        print(f"Removed {student.name} from {course.name}")
        return True

    @dispatch(object)
    def remove_student(self, student):
        print("Error: No course specified")
        return False

    @dispatch(object, object)
    def assign_professor(self, professor, course):
        if not self.logged_in:
            print("Please login first")
            return False
            
        if course.professor:
            print(f"{course.name} already taught by {course.professor.name}")
            return False
            
        course.professor = professor
        if course.name not in professor.courses_taught:
            professor.courses_taught.append(course.name)
        print(f"Assigned {professor.name} to {course.name}")
        return True

    @dispatch(str, object)
    def assign_professor(self, professor_id, course):
        professor = None
        if not professor:
            print(f"Professor {professor_id} not found")
            return False
        return self.assign_professor(professor, course)

    @dispatch(object)
    def manage_course(self, course):
        course.get_course_info()
        return True

    @dispatch(object, str)
    def manage_course(self, course, new_name):
        if not self.logged_in:
            print("Please login first")
            return False
            
        if new_name and new_name != course.name:
            old_name = course.name
            for student in course.enrolled_students:
                if course.name in student.courses_enrolled:
                    student.courses_enrolled[student.courses_enrolled.index(course.name)] = new_name
            
            if course.professor and course.name in course.professor.courses_taught:
                course.professor.courses_taught[course.professor.courses_taught.index(course.name)] = new_name
            
            course.name = new_name

            if hasattr(course, 'department') and course.department:
                for dept_course in course.department.courses_offered:
                    if dept_course.name == old_name:
                        dept_course.name = new_name

            print(f"Updated course {course.course_id}: name: {old_name} → {new_name}")
            return True
            
        print("No changes made")
        return False

    @dispatch(object, int)
    def manage_course(self, course, new_credits):
        if not self.logged_in:
            print("Please login first")
            return False
            
        if new_credits is not None and new_credits != course.credits:
            old_credits = course.credits
            course.credits = new_credits
            print(f"Updated course {course.course_id}: credits: {old_credits} → {new_credits}")
            return True
            
        print("No changes made")
        return False

    @dispatch(object, object)
    def manage_course(self, course, new_dept):
        if not self.logged_in:
            print("Please login first")
            return False
            
        if new_dept and new_dept != getattr(course, 'department', None):
            old_dept = getattr(course, 'department', None)
            if old_dept and old_dept.courses_offered:
                old_dept.courses_offered.remove(course)
            if new_dept:
                new_dept.courses_offered.append(course)
            course.department = new_dept
            print(f"Updated course {course.course_id}: department: {old_dept.name if old_dept else None} → {new_dept.name}")
            return True
            
        print("No changes made")
        return False

    @dispatch(object, str, int)
    def manage_course(self, course, new_name, new_credits):
        name_changed = self.manage_course(course, new_name)
        credits_changed = self.manage_course(course, new_credits)
        return name_changed or credits_changed

    @dispatch(object, str, object)
    def manage_course(self, course, new_name, new_dept):
        name_changed = self.manage_course(course, new_name)
        dept_changed = self.manage_course(course, new_dept)
        return name_changed or dept_changed

    @dispatch(object, int, object)
    def manage_course(self, course, new_credits, new_dept):
        credits_changed = self.manage_course(course, new_credits)
        dept_changed = self.manage_course(course, new_dept)
        return credits_changed or dept_changed

    @dispatch(object, str, int, object)
    def manage_course(self, course, new_name, new_credits, new_dept):
        name_changed = self.manage_course(course, new_name)
        credits_changed = self.manage_course(course, new_credits)
        dept_changed = self.manage_course(course, new_dept)
        return name_changed or credits_changed or dept_changed

class Classroom:
    def __init__(self, classroom_id, location, capacity):
        self.classroom_id = classroom_id
        self.location = location
        self.capacity = capacity
        self.schedule = {}

    def allocate_class(self, date, time_slot):
        if date not in self.schedule:
            self.schedule[date] = []
        
        if time_slot in self.schedule[date]:
            print(f"Time slot {time_slot} on {date} is already booked")
            return False
        
        self.schedule[date].append(time_slot)
        print(f"Allocated {time_slot} on {date} in {self.location} (Room {self.classroom_id})")
        return True

    def check_availability(self, date, time_slot=None):
        if date not in self.schedule:
            return True
        
        if not time_slot:
            return False
        
        return time_slot not in self.schedule[date]

    def get_classroom_info(self):
        booked_days = len(self.schedule)
        next_booking = min(self.schedule.keys()) if self.schedule else "None"
        
        info = f"""
        CLASSROOM INFORMATION
        ID: {self.classroom_id}
        Location: {self.location}
        Capacity: {self.capacity}
        Booked Days: {booked_days}
        Next Booking: {next_booking}
        """
        print(info)

    def is_allocated(self, date, time_slot):
        if date not in self.schedule:
            return False
        return time_slot in self.schedule[date]

    def allocate(self, date, time_slot):
        if date not in self.schedule:
            self.schedule[date] = []
            
        if not self.is_allocated(date, time_slot):
            self.schedule[date].append(time_slot)
            return True
        return False

class Schedule:
    def __init__(self, schedule_id, course, professor, time_slot, classroom, date):
        self.schedule_id = schedule_id
        self.course = course
        self.professor = professor
        self.time_slot = time_slot
        self.classroom = classroom
        self.date = date

    def assign_schedule(self):
        university = University.get_instance()
        if not hasattr(university, 'schedules'):
            university.schedules = []

        # Check for conflicts
        for schedule in university.schedules:
            if schedule.date == self.date and schedule.time_slot == self.time_slot:
                if (schedule.classroom == self.classroom or 
                    schedule.professor == self.professor):
                    return False

        if self.classroom.allocate(self.date, self.time_slot):
            university.schedules.append(self)
            return True
        return False

    def update_schedule(self, new_time_slot=None, new_location=None, new_date=None):
        university = University.get_instance()
        
        # Store original values
        old_time_slot = self.time_slot
        old_classroom = self.classroom
        old_date = self.date

        # Check conflicts for new values
        for schedule in university.schedules:
            if schedule == self:
                continue
                
            check_date = new_date if new_date else self.date
            check_time = new_time_slot if new_time_slot else self.time_slot
            check_room = new_location if new_location else self.classroom
            
            if schedule.date == check_date and schedule.time_slot == check_time:
                if (schedule.classroom == check_room or 
                    schedule.professor == self.professor):
                    return False

        # Remove old allocation
        if old_date in old_classroom.schedule:
            if old_time_slot in old_classroom.schedule[old_date]:
                old_classroom.schedule[old_date].remove(old_time_slot)

        # Update values and allocate
        if new_time_slot:
            self.time_slot = new_time_slot
        if new_location:
            self.classroom = new_location
        if new_date:
            self.date = new_date

        return self.classroom.allocate(self.date, self.time_slot)

    def view_schedule(self):
        info = f"""
        SCHEDULE DETAILS:
        ID: {self.schedule_id}
        Course: {self.course.name} ({self.course.course_id})
        Professor: {self.professor.name}
        Date: {self.date}
        Time: {self.time_slot}
        Location: {self.classroom.location} (Room {self.classroom.classroom_id})
        """
        print(info)

class Exam:
    def __init__(self, exam_id, course, date, duration):
        self.exam_id = exam_id
        self.course = course        # Course object
        self.date = date            # Format: "YYYY-MM-DD"
        self.duration = duration
        self.student_results = {}   # {student_id: grade}

    def schedule_exam(self, classroom):
        if not hasattr(self.course, 'exams'):
            self.course.exams = []
        self.course.exams.append(self)
        
        hours = self.duration // 60
        mins = self.duration % 60
        time_slot = f"09:00-{9+hours:02d}:{mins:02d}"
        
        if classroom.allocate_class(self.date, time_slot):
            print(f"Scheduled {self.course.name} exam on {self.date} for {self.duration} mins")
            return True
        return False

    def record_results(self, student, grade):
        if student.user_id not in self.student_results:
            self.student_results[student.user_id] = grade
            if hasattr(student, 'exam_grades'):
                student.exam_grades[self.exam_id] = grade
            print(f"Recorded grade {grade} for {student.name}")
            return True
        print(f"Result already exists for {student.name}")
        return False

    def view_exam_info(self):
        num_students = len(self.student_results)
        
        avg_grade = None
        if self.student_results:
            numeric_grades = []
            for grade in self.student_results.values():
                if isinstance(grade, (int, float)):
                    numeric_grades.append(grade)
                elif isinstance(grade, str) and grade.replace('.','',1).isdigit():
                    numeric_grades.append(float(grade))
            if numeric_grades:
                avg_grade = sum(numeric_grades)/len(numeric_grades)
        
        info = f"""
        EXAM INFORMATION:
        ID: {self.exam_id}
        Course: {self.course.name} ({self.course.course_id})
        Date: {self.date}
        Duration: {self.duration} minutes
        Students Completed: {num_students}
        Average Grade: {avg_grade if avg_grade is not None else 'N/A'}
        """
        print(info)

class Library:
    def __init__(self, library_id):
        self.library_id = library_id
        self.books = {}  # Format: {book_id: {"title": str, "author": str, "available": bool, "borrowed_by": str}}
        self.students_registered = {}  # Format: {student_id: Student object}

    def borrow_book(self, student_id, book_id):
        if student_id not in self.students_registered:
            raise Exception("Student is not registered in the library")
        
        if book_id not in self.books:
            raise Exception("Book does not exist in the library")
            
        if not self.books[book_id]["available"]:
            raise Exception("Book is already borrowed by another student")
            
        student = self.students_registered[student_id]
        
        if not student.libraryRegistered:
            raise Exception("Student is not registered in the library")
            
        # Update book status first
        self.books[book_id]["available"] = False
        self.books[book_id]["borrowed_by"] = student_id
        student.borrowed_books.append(book_id)
        
        return True

    def return_book(self, student_id, book_id):
        if student_id not in self.students_registered:
            raise Exception("Student is not registered")
            
        if book_id not in self.books:
            raise Exception("Book does not exist")
            
        if self.books[book_id]["available"]:
            raise Exception("Book was not borrowed")
            
        if self.books[book_id]["borrowed_by"] != student_id:
            raise Exception("Book was not borrowed by this student")
            
        self.books[book_id]["available"] = True
        self.books[book_id]["borrowed_by"] = None
        student = self.students_registered[student_id]
        
        if book_id in student.borrowed_books:
            student.borrowed_books.remove(book_id)
        
        return True

    def check_availability(self, book_id=None):
        if book_id:
            if book_id not in self.books:
                raise Exception("Book does not exist")
            return self.books[book_id]
        else:
            available_books = [
                {"id": book_id, **book_info} 
                for book_id, book_info in self.books.items() 
                if book_info["available"]
            ]
            return available_books

    def add_book(self, book_id, title, author):
        if book_id in self.books:
            raise Exception("Book already exists")
            
        self.books[book_id] = {
            "title": title,
            "author": author,
            "available": True,
            "borrowed_by": None
        }
        return True

    def register_student(self, student):
        if student.user_id in self.students_registered:
            raise Exception("Student already registered")
            
        self.students_registered[student.user_id] = student
        student.libraryRegistered = True
        return True

class University:
    _instance = None
    
    @staticmethod
    def get_instance():
        if University._instance is None:
            University._instance = University()
        return University._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):  
            print("Initializing University instance")  # Debug log
            self.departments = []
            self.users = []
            self.courses = []
            self.classrooms = {}  # Initialize as empty dictionary
            self.initialized = True
            print("Initial classrooms:", self.classrooms)  # Debug log
            
            # Add some test classrooms
            test_classrooms = [
                Classroom("101", "Main Building", 30),
                Classroom("102", "Main Building", 25),
                Classroom("201", "Science Wing", 40),
                Classroom("202", "Science Wing", 35)
            ]
            print("Created test classrooms:", test_classrooms)  # Debug log
            
            for classroom in test_classrooms:
                self.classrooms[classroom.classroom_id] = classroom
                print(f"Added classroom {classroom.classroom_id} to university")  # Debug log
                
            print("Final classrooms after initialization:", self.classrooms)  # Debug log
            self.initialized = True
    
    def add_department(self, department):
        self.departments.append(department)
    
    def add_user(self, user):
        self.users.append(user)
    
    def add_course(self, course):
        self.courses.append(course)

    def add_classroom(self, classroom):
        self.classrooms.append(classroom)

    def get_student(self, student_id):
        for user in self.users:
            if hasattr(user, 'user_id') and user.user_id == student_id:
                if isinstance(user, Student):  # Ensure it's a Student
                   return user
        return None

    def get_course(self, course_id):
        for course in self.courses:
            if hasattr(course, 'course_id') and course.course_id == course_id:
                return course
        return None

    def get_professor(self, professor_id):
        for user in self.users:
            if isinstance(user, Professor) and user.user_id == professor_id:
                return user
        return None
    
    def get_classroom(self, classroom_id):
        for classroom in self.classrooms:
            if hasattr(classroom, 'classroom_id') and classroom.classroom_id == classroom_id:
                return classroom
        return None