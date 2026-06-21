import socket
import pickle

class UniversityClient:
    def __init__(self, host='127.0.0.1', port=5500):  # Fixed __init__ and port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def get_student(self, student_id):
        self.sock.sendall(pickle.dumps(('GET_STUDENT', student_id)))
        return pickle.loads(self.sock.recv(5500))
     
    def add_student(self, student_id, name, email, major):
        self.sock.sendall(pickle.dumps(
            ('ADD_STUDENT', student_id, name, email, major)
        ))
        return pickle.loads(self.sock.recv(5500))

    def enroll_course(self, student_id, course_id):
        try:
            self.sock.sendall(pickle.dumps(('ENROLL', student_id, course_id)))
            data = self.sock.recv(5500)
            if not data:
                return "No response from server"
            return pickle.loads(data)
        except Exception as e:
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":
    client = UniversityClient()
    print(client.add_student("S789", "POP", "pop@gmail.com", "Math"))
    print(client.enroll_course("S789", "Math 101"))
