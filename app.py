from flask import Flask, jsonify, request

app = Flask(__name__)

books = [
    {
        "id": 1,
        "title": "Python Basics",
        "author": "John"
    },
    {
        "id": 2,
        "title": "Flask Guide",
        "author": "Alice"
    }
]

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the Library API"
    })

@app.route("/books")
def get_books():
    return jsonify(books)

@app.route("/books/<int:id>")
def get_book(id):

    for book in books:
        if book["id"] == id:
            return jsonify(book)

    return jsonify({"error": "Book not found"}), 404

@app.route("/books", methods=["POST"])
def add_book():

    data = request.get_json()

    new_book = {
        "id": len(books) + 1,
        "title": data["title"],
        "author": data["author"]
    }

    books.append(new_book)

    return jsonify(new_book), 201

if __name__ == "__main__":
    app.run(debug=True)