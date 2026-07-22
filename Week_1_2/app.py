import os
import sqlite3

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL
            )
            """
        )
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        if count == 0:
            conn.execute("INSERT INTO books (title, author) VALUES (?, ?)", ("Python Basics", "John"))
            conn.execute("INSERT INTO books (title, author) VALUES (?, ?)", ("Flask Guide", "Alice"))
            conn.commit()


init_db()


def get_all_books():
    with get_db() as conn:
        rows = conn.execute("SELECT id, title, author FROM books ORDER BY id").fetchall()
    return [{"id": row["id"], "title": row["title"], "author": row["author"]} for row in rows]


def get_book_by_id(book_id):
    with get_db() as conn:
        row = conn.execute("SELECT id, title, author FROM books WHERE id = ?", (book_id,)).fetchone()
    if row is None:
        return None
    return {"id": row["id"], "title": row["title"], "author": row["author"]}


def create_book(title, author):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO books (title, author) VALUES (?, ?)",
            (title, author),
        )
        conn.commit()
        row = conn.execute("SELECT id, title, author FROM books WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return {"id": row["id"], "title": row["title"], "author": row["author"]}


def update_book_record(book_id, title, author):
    with get_db() as conn:
        conn.execute("UPDATE books SET title = ?, author = ? WHERE id = ?", (title, author, book_id))
        conn.commit()
        row = conn.execute("SELECT id, title, author FROM books WHERE id = ?", (book_id,)).fetchone()
    if row is None:
        return None
    return {"id": row["id"], "title": row["title"], "author": row["author"]}


def delete_book_record(book_id):
    with get_db() as conn:
        result = conn.execute("DELETE FROM books WHERE id = ?", (book_id,)).rowcount
        conn.commit()
    return result > 0


LANDING_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Library Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #f4f7fb, #e8f0fe); color: #203245; }
    .hero { max-width: 1100px; margin: 40px auto; background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); overflow: hidden; }
    .topbar { background: linear-gradient(90deg, #2f80ed, #1abc9c); color: white; padding: 28px 36px; }
    .topbar h1 { margin: 0 0 8px; font-size: 32px; }
    .topbar p { margin: 0; font-size: 16px; opacity: 0.95; }
    .content { padding: 28px 36px 36px; }
    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card { background: #f8fbff; border: 1px solid #dfe9fa; border-radius: 14px; padding: 16px; }
    .card h3 { margin: 0 0 8px; font-size: 16px; color: #2f4f6f; }
    .card .value { font-size: 28px; font-weight: bold; color: #2f80ed; }
    .actions { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px; }
    .btn { display: inline-block; padding: 10px 16px; border-radius: 999px; text-decoration: none; font-weight: bold; color: white; background: #2f80ed; }
    .btn.secondary { background: #27ae60; }
    .panel { border: 1px solid #e5ebf3; border-radius: 14px; padding: 18px; background: #fff; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { padding: 12px; text-align: center; border-bottom: 1px solid #e6ebf2; }
    th { background: #f3f7ff; color: #27415d; }
    a { color: #2f80ed; text-decoration: none; }
  </style>
</head>
<body>
  <div class="hero">
    <div class="topbar">
      <h1>Library Dashboard</h1>
      <p>Manage your books with a clean, modern overview.</p>
    </div>
    <div class="content">
      <div class="stats">
        <div class="card">
          <h3>Total Books</h3>
          <div class="value">{{ total_books }}</div>
        </div>
        <div class="card">
          <h3>Library Status</h3>
          <div class="value">Active</div>
        </div>
      </div>
      <div class="actions">
        <a class="btn" href="/books">Open Books Manager</a>
        <a class="btn secondary" href="/api/books">View API</a>
      </div>
      <div class="panel">
        <h2 style="margin-top:0;">Recently Added Books</h2>
        <table>
          <thead>
            <tr><th>ID</th><th>Title</th><th>Author</th></tr>
          </thead>
          <tbody>
            {% for book in books %}
            <tr>
              <td>{{ book['id'] }}</td>
              <td>{{ book['title'] }}</td>
              <td>{{ book['author'] }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</body>
</html>
"""

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
    books = get_all_books()
    return render_template_string(
        LANDING_TEMPLATE,
        books=books[:5],
        total_books=len(books),
    )


@app.route("/books")
def books_page():
    return render_template_string(HTML_TEMPLATE, books=get_all_books())


@app.route("/books", methods=["POST"])
def add_book_from_form():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    if not title or not author:
        return "Title and author are required", 400

    create_book(title, author)
    return "Book added successfully", 201


@app.route("/api/books")
def get_books():
    return jsonify(get_all_books())


@app.route("/api/books", methods=["POST"])
def add_book():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    new_book = create_book(title, author)
    return jsonify(new_book), 201


@app.route("/api/books/<int:book_id>")
def get_book(book_id):
    book = get_book_by_id(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)


@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    updated_book = update_book_record(book_id, title, author)
    if updated_book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(updated_book)


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    if delete_book_record(book_id):
        return jsonify({"message": "Book deleted"})
    return jsonify({"error": "Book not found"}), 404


@app.route("/books/<int:book_id>")
def show_book(book_id):
    book = get_book_by_id(book_id)
    if book is None:
        return "Book not found", 404
    return render_template_string(DETAIL_TEMPLATE, book=book)


@app.route("/books/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    book = get_book_by_id(book_id)
    if book is None:
        return "Book not found", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        if not title or not author:
            return "Title and author are required", 400
        update_book_record(book_id, title, author)
        return "Book updated successfully", 200

    return render_template_string(EDIT_TEMPLATE, book=book)


@app.route("/books/delete/<int:book_id>")
def delete_book_view(book_id):
    if delete_book_record(book_id):
        return "Book deleted successfully", 200
    return "Book not found", 404


if __name__ == "__main__":
    app.run(debug=True)