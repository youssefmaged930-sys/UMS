import unittest
from models import Student  # Import your Student class

class TestStudent(unittest.TestCase):
    def setUp(self):
        """Runs before each test method"""
        self.student = Student("S123", "John Doe", "john@uni.edu", "Computer Science")

    def test_enroll_course(self):
        self.student.enroll_course("CSC101")
        self.assertIn("CSC101", self.student.courses_enrolled)  # Check enrollment
        self.assertEqual(self.student.grades["CSC101"], None)   # Check grade initialized

    def test_drop_course(self):
        self.student.enroll_course("CSC101")
        self.student.drop_course("CSC101")
        self.assertNotIn("CSC101", self.student.courses_enrolled)  # Check removal

    def test_update_grade(self):
        self.student.enroll_course("CSC101")
        self.student.update_grade("CSC101", "A")
        self.assertEqual(self.student.grades["CSC101"], "A")  # Check grade update

if __name__ == '__main__':
    unittest.main()