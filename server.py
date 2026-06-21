import socket
import pickle
from threading import Thread
from models import Student, Course , University

students = {}
courses = {}

class UniversityServer:
    def __init__(self, host='127.0.0.1', port=5500):
        self.host = host
        self.port = port
        self.setup_socket()
    
    def setup_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"Server listening on {self.host}:{self.port}")
    
    def handle_client(self, conn):
        try:
            while True:
                data = conn.recv(5500)
                if not data:
                    break

                try:
                    command_data = pickle.loads(data)
                    command, *args = command_data

                    if command == 'GET_STUDENT':
                        student_id = args[0]
                        response = students.get(student_id, "Student not found")

                    elif command == 'ADD_STUDENT':
                        student_id, name, email, major = args
                        if student_id in students:
                            response = "Student already exists"
                        else:
                            students[student_id] = Student(student_id, name, email, major)
                            response = f"Student {student_id} added successfully"

                    elif command == 'ENROLL':
                        student_id, course_id = args
                        student = students.get(student_id)
                        if not student:
                            response = "Student not found"
                        else:
                            if course_id not in courses:
                                courses[course_id] = Course(course_id, course_id, "General", 3)  # Added required parameters
                            if course_id not in student.courses_enrolled:
                                student.courses_enrolled.append(course_id)
                                response = f"Student {student_id} enrolled in {course_id}"
                            else:
                                response = f"Student {student_id} already enrolled in {course_id}"
                    else:
                        response = "Unknown command"

                except Exception as e:
                    response = f"Error processing command: {str(e)}"

                conn.sendall(pickle.dumps(response))
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
    
    def run(self):
        print("Server is running...")
        while True:
            conn, addr = self.sock.accept()
            print(f"Connected by {addr}")
            Thread(target=self.handle_client, args=(conn,)).start()


if __name__ == "__main__":
    server = UniversityServer()
    server.run()
