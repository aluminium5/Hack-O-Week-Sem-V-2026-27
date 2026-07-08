from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

books = [
    {"id": 1, "title": "Python Basics", "author": "John"},
    {"id": 2, "title": "Flask Guide", "author": "Alice"},
]

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Library Management System</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f4f7fb; margin: 0; padding: 0; }
    .container { max-width: 900px; margin: 40px auto; background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
    h1 { text-align: center; color: #2c3e50; }
    .form-box { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px; }
    input { padding: 10px; width: 220px; border: 1px solid #ccc; border-radius: 8px; }
    button { padding: 10px 14px; border: none; border-radius: 8px; background: #2f80ed; color: white; cursor: pointer; }
    button.secondary { background: #e74c3c; }
    table { width: 100%; border-collapse: collapse; margin-top: 14px; }
    th, td { padding: 12px; text-align: center; border-bottom: 1px solid #ddd; }
    th { background: #2c3e50; color: white; }
    a { color: #2f80ed; text-decoration: none; }
    .actions a { margin: 0 6px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Library Management System</h1>
    <h2 style="text-align:center;">Books Table</h2>
    <form class="form-box" action="/books" method="post">
      <input name="title" placeholder="Book Name" required>
      <input name="author" placeholder="Author" required>
      <button type="submit">Add Book</button>
    </form>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Book Name</th>
          <th>Author</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for book in books %}
        <tr>
          <td>{{ book['id'] }}</td>
          <td>{{ book['title'] }}</td>
          <td>{{ book['author'] }}</td>
          <td class="actions">
            <a href="/books/{{ book['id'] }}">View</a>
            <a href="/books/edit/{{ book['id'] }}">Edit</a>
            <a href="/books/delete/{{ book['id'] }}" onclick="return confirm('Delete this book?')">Delete</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</body>
</html>
"""

DETAIL_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Book Details</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f4f7fb; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 40px auto; background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
    h1 { text-align: center; color: #2c3e50; }
    p { font-size: 18px; text-align: center; }
    a { display: inline-block; margin-top: 16px; color: #2f80ed; text-decoration: none; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Book Details</h1>
    <p><strong>ID:</strong> {{ book['id'] }}</p>
    <p><strong>Title:</strong> {{ book['title'] }}</p>
    <p><strong>Author:</strong> {{ book['author'] }}</p>
    <p><a href="/books">Back to Books</a></p>
  </div>
</body>
</html>
"""

EDIT_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Edit Book</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f4f7fb; margin: 0; padding: 0; }
    .container { max-width: 500px; margin: 40px auto; background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
    h1 { text-align: center; color: #2c3e50; }
    form { display: flex; flex-direction: column; gap: 12px; }
    input { padding: 10px; border: 1px solid #ccc; border-radius: 8px; }
    button { padding: 10px; border: none; border-radius: 8px; background: #27ae60; color: white; cursor: pointer; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Edit Book</h1>
    <form action="/books/edit/{{ book['id'] }}" method="post">
      <input name="title" value="{{ book['title'] }}" required>
      <input name="author" value="{{ book['author'] }}" required>
      <button type="submit">Update Book</button>
    </form>
  </div>
</body>
</html>
"""


@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Library API"})


@app.route("/books")
def books_page():
    return render_template_string(HTML_TEMPLATE, books=books)


@app.route("/books", methods=["POST"])
def add_book_from_form():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    if not title or not author:
        return "Title and author are required", 400

    new_book = {"id": len(books) + 1, "title": title, "author": author}
    books.append(new_book)
    return "Book added successfully", 201


@app.route("/api/books")
def get_books():
    return jsonify(books)


@app.route("/api/books", methods=["POST"])
def add_book():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    new_book = {"id": len(books) + 1, "title": title, "author": author}
    books.append(new_book)
    return jsonify(new_book), 201


@app.route("/api/books/<int:book_id>")
def get_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return jsonify(book)
    return jsonify({"error": "Book not found"}), 404


@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    for book in books:
        if book["id"] == book_id:
            book["title"] = title
            book["author"] = author
            return jsonify(book)
    return jsonify({"error": "Book not found"}), 404


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            del books[index]
            return jsonify({"message": "Book deleted"})
    return jsonify({"error": "Book not found"}), 404


@app.route("/books/<int:book_id>")
def show_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return render_template_string(DETAIL_TEMPLATE, book=book)
    return "Book not found", 404


@app.route("/books/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    for book in books:
        if book["id"] == book_id:
            if request.method == "POST":
                book["title"] = request.form.get("title", "").strip()
                book["author"] = request.form.get("author", "").strip()
                if not book["title"] or not book["author"]:
                    return "Title and author are required", 400
                return "Book updated successfully", 200
            return render_template_string(EDIT_TEMPLATE, book=book)
    return "Book not found", 404


@app.route("/books/delete/<int:book_id>")
def delete_book_view(book_id):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            del books[index]
            return "Book deleted successfully", 200
    return "Book not found", 404


if __name__ == "__main__":
    app.run(debug=True)