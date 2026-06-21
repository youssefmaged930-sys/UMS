from abc import ABC, abstractmethod
from multipledispatch import dispatch
from models import GradeUpdateProxy, Student, Professor, Course, CourseProxy, Department, Administrator, Classroom, Schedule, Exam, Library, University
from data_manager import save_data, load_data

def run_terminal_program():
    students = {}
    professors = {}
    courses = {}
    departments = {}
    admins = {}
    exams = []
    library = Library("LIB-01")
    classrooms = {}
    schedules = []
    loaded_data = load_data()
    if loaded_data:  # If data was loaded successfully
        students = {s.user_id: s for s in loaded_data.get("users", []) if isinstance(s, Student)}
        professors = {p.user_id: p for p in loaded_data.get("users", []) if isinstance(p, Professor)}
        admins = {a.user_id: a for a in loaded_data.get("users", []) if isinstance(a, Administrator)}
        courses = {c.course_id: c for c in loaded_data.get("courses", [])}
        departments = {d.department_id: d for d in loaded_data.get("departments", [])}
        exams = loaded_data.get("exams", [])
        library = loaded_data.get("library", Library("LIB-01"))
        classrooms = loaded_data.get("classrooms", {})
        schedules = loaded_data.get("schedules", [])

    while True:
        print("\nUNIVERSITY MANAGEMENT SYSTEM")
        print("1. Add Student")
        print("2. Add Professor")
        print("3. Add Course")
        print("4. Enroll Student in Course")
        print("5. Assign Professor to Course")
        print("6. View Student Dashboard")
        print("7. View Professor Dashboard")
        print("8. Admin Login and Dashboard")
        print("9. Add Book to Library")
        print("10. Register Student to Library")
        print("11. Borrow Book")
        print("12. Return Book")
        print("13. Schedule Exam")
        print("14. Record Exam Result")
        print("15. View Exam Info")
        print("16. Add Classroom")
        print("17. Allocate Time Slot")
        print("18. View Classroom Info")
        print("19. Assign Schedule")
        print("20. View Schedule Details")
        print("21. Assign Grade to Student")

        print("0. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            sid = input("Student ID: ")
            name = input("Name: ")
            email = input("Email: ")
            major = input("Major: ")
            students[sid] = Student(sid, name, email, major)
            print(f"Student {name} added.")
        elif choice == "2":
            pid = input("Professor ID: ")
            name = input("Name: ")
            email = input("Email: ")
            dept = input("Department: ")
            professors[pid] = Professor(pid, name, email, dept)
            print(f"Professor {name} added.")
        elif choice == "3":
            cid = input("Course ID: ")
            name = input("Course Name: ")
            dept = input("Department: ")
            credits = int(input("Credits: "))
            courses[cid] = CourseProxy(cid, name, dept, credits)
            #course = Course(cid, name, dept, credits)
            #courses[cid] = course
            print(f"Course {name} added.")
        elif choice == "4":
            sid = input("Student ID: ")
            cid = input("Course ID: ")
            if sid in students and cid in courses:
                courses[cid].add_student(students[sid])
            else:
                print("Invalid student or course ID.")
        elif choice == "5":
            pid = input("Professor ID: ")
            cid = input("Course ID: ")
            if pid in professors and cid in courses:
                courses[cid].assign_professor(professors[pid])
            else:
                print("Invalid professor or course ID.")
        elif choice == "6":
            sid = input("Student ID: ")
            if sid in students:
                students[sid].login("password")
                students[sid].view_dashboard()
            else:
                print("Student not found.")
        elif choice == "7":
            pid = input("Professor ID: ")
            if pid in professors:
                professors[pid].login("password")
                professors[pid].view_dashboard()
            else:
                print("Professor not found.")
        elif choice == "8":
            aid = input("Admin ID: ")
            name = input("Name: ")
            email = input("Email: ")
            phone = input("Phone (optional): ")
            admin = Administrator(aid, name, email, phone)
            admins[aid] = admin
            admin.login("adminpass")
            admin.view_dashboard()
        elif choice == "9":
            bid = input("Book ID: ")
            title = input("Book Title: ")
            author = input("Author: ")
            library.add_book(bid, title, author)
        elif choice == "10":
            sid = input("Student ID: ")
            if sid in students:
                library.register_student(students[sid])
            else:
                print("Student not found.")
        elif choice == "11":
            sid = input("Student ID: ")
            bid = input("Book ID: ")
            library.borrow_book(sid, bid)
        elif choice == "12":
            sid = input("Student ID: ")
            bid = input("Book ID: ")
            library.return_book(sid, bid)
        elif choice == "13":
            eid = input("Exam ID: ")
            cid = input("Course ID: ")
            date = input("Date (YYYY-MM-DD): ")
            duration = int(input("Duration (in minutes): "))
            room_id = input("Classroom ID: ")
            if cid not in courses:
                print("Invalid course ID.")
                continue
            classroom = Classroom(room_id, f"Room {room_id}", 50)
            exam = Exam(eid, courses[cid], date, duration)
            if exam.schedule_exam(classroom):
                exams.append(exam)
        elif choice == "14":
            eid = input("Exam ID: ")
            sid = input("Student ID: ")
            grade = input("Grade: ")
            target_exam = None
            for ex in exams:
                if ex.exam_id == eid:
                    target_exam = ex
                    break
            if not target_exam:
                print("Exam not found.")
                continue
            if sid not in students:
                print("Student not found.")
                continue
            target_exam.record_results(students[sid], grade)
        elif choice == "15":
            eid = input("Exam ID: ")
            for ex in exams:
                if ex.exam_id == eid:
                    ex.view_exam_info()
                    break
            else:
                print("Exam not found.")

        elif choice == "16":
            cid = input("Classroom ID: ")
            loc = input("Location: ")
            cap = int(input("Capacity: "))
            if cid not in classrooms:
                classrooms[cid] = Classroom(cid, loc, cap)
                print(f"Classroom {cid} added.")
            else:
                print("Classroom already exists.")

        elif choice == "17":
            cid = input("Classroom ID: ")
            date = input("Date (YYYY-MM-DD): ")
            slot = input("Time Slot (e.g., 10:00-12:00): ")
            if cid in classrooms:
                classrooms[cid].allocate_class(date, slot)
            else:
                print("Classroom not found.")

        elif choice == "18":
            cid = input("Classroom ID: ")
            if cid in classrooms:
                classrooms[cid].get_classroom_info()
            else:
                print("Classroom not found.")

        elif choice == "19":
            sid = input("Schedule ID: ")
            cid = input("Course ID: ")
            pid = input("Professor ID: ")
            room_id = input("Classroom ID: ")
            date = input("Date (YYYY-MM-DD): ")
            time_slot = input("Time Slot (e.g. 14:00-16:00): ")

            if cid not in courses:
                print("Invalid course ID.")
                continue
            if pid not in professors:
                print("Invalid professor ID.")
                continue
            if room_id not in classrooms:
                print("Invalid classroom ID.")
                continue

            sched = Schedule(sid, courses[cid], professors[pid], time_slot, classrooms[room_id], date)
            if sched.assign_schedule():
                schedules.append(sched)

        elif choice == "20":
            sid = input("Schedule ID: ")
            found = False
            for sched in schedules:
                if sched.schedule_id == sid:
                    sched.view_schedule()
                    found = True
                    break
            if not found:
                print("Schedule not found.")
        
        elif choice == "21":  # Assign grade
            pid = input("Professor ID: ")
            sid = input("Student ID: ")
            cid = input("Course ID: ")
            grade = input("Grade: ")
            
            if pid in professors and sid in students and cid in courses:
                professor = professors[pid]
                student = students[sid]
                course = courses[cid]
                
                # Wrap student in proxy
                protected_student = GradeUpdateProxy(student, professor)
                success = professor.assign_grade(protected_student, course.name, grade)
            else:
                print("Invalid IDs")
                success = False
    
            print("✅ Success" if success else "❌ Failed")


        elif choice == "0":
            print("Exiting program.")
            save_data(students, professors, courses, departments, admins, exams, library, classrooms, schedules)
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    run_terminal_program()