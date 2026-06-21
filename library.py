from flask import Blueprint, request, jsonify
from models import University, Library

library_bp = Blueprint('library', __name__)

@library_bp.route('/add-book', methods=['POST'])
def add_book():
    try:
        data = request.get_json()
        book_id = data.get('bookId')
        title = data.get('title')
        author = data.get('author')

        if not all([book_id, title, author]):
            return jsonify({"error": "Missing required fields"}), 400

        university = University.get_instance()
        if not hasattr(university, 'library'):
            university.library = Library("LIB-01")

        library = university.library

        # Add the book
        try:
            success = library.add_book(book_id, title, author)
            
            if success:
                return jsonify({
                    "message": f"Book '{title}' added successfully",
                    "book": {
                        "id": book_id,
                        "title": title,
                        "author": author,
                        "available": True,
                        "borrowed_by": None
                    }
                }), 201
            else:
                return jsonify({"error": f"Book with ID {book_id} already exists"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/borrow-book', methods=['POST'])
def borrow_book():
    try:
        data = request.get_json()
        student_id = data.get('studentId')
        book_id = data.get('bookId')

        if not all([student_id, book_id]):
            return jsonify({"error": "Missing required fields"}), 400

        university = University.get_instance()
        library = university.library

        # Borrow the book
        success = library.borrow_book(student_id, book_id)
        
        if success:
            book = library.books[book_id]
            return jsonify({
                "message": f"Book '{book['title']}' borrowed successfully",
                "book": {
                    "id": book_id,
                    "title": book['title'],
                    "author": book['author'],
                    "available": False,
                    "borrowed_by": student_id
                }
            }), 200
        else:
            return jsonify({"error": "Failed to borrow book"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/return-book', methods=['POST'])
def return_book():
    try:
        data = request.get_json()
        student_id = data.get('studentId')
        book_id = data.get('bookId')

        if not all([student_id, book_id]):
            return jsonify({"error": "Missing required fields"}), 400

        university = University.get_instance()
        library = university.library

        # Return the book
        try:
            success = library.return_book(student_id, book_id)
            
            if success:
                book = library.books[book_id]
                return jsonify({
                    "message": f"Book '{book['title']}' returned successfully",
                    "book": {
                        "id": book_id,
                        "title": book['title'],
                        "author": book['author'],
                        "available": True,
                        "borrowed_by": None
                    }
                }), 200
            else:
                return jsonify({"error": "Failed to return book"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    try:
        university = University.get_instance()
        library = university.library
        
        if book_id not in library.books:
            return jsonify({"error": "Book not found"}), 404
            
        book = library.books[book_id]
        return jsonify({
            "id": book_id,
            "title": book['title'],
            "author": book['author'],
            "available": book['available'],
            "borrowed_by": book['borrowed_by']
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    try:
        university = University.get_instance()
        student = university.get_student(student_id)
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        return jsonify({
            "id": student.user_id,
            "name": student.name,
            "email": student.email,
            "major": student.major,
            "libraryRegistered": student.libraryRegistered
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
