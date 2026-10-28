
from flask import Flask, request, redirect, render_template_string
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "books.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Online Bookstore</title>
    <style>
        body { font-family: Arial; margin: 35px; background: #f4f6f8; }
        h1 { color: #243b55; }
        form, table { background: white; padding: 15px; margin-bottom: 20px; }
        input { padding: 8px; margin: 5px; }
        button { padding: 8px 12px; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
        th { background: #dce6f1; }
        a { margin-right: 8px; }
    </style>
</head>
<body>
    <h1>Online Bookstore</h1>
    <h3>{{ 'Update Book' if edit else 'Add a New Book' }}</h3>

    <form method="POST" action="{{ '/update/' ~ edit.id if edit else '/add' }}">
        <input name="title" placeholder="Book Title"
               value="{{ edit.title if edit else '' }}" required>
        <input name="author" placeholder="Author"
               value="{{ edit.author if edit else '' }}" required>
        <input name="price" type="number" min="0" step="0.01"
               placeholder="Price" value="{{ edit.price if edit else '' }}" required>
        <button type="submit">{{ 'Update Book' if edit else 'Add Book' }}</button>
        {% if edit %}<a href="/">Cancel</a>{% endif %}
    </form>

    <h3>Available Books</h3>
    <table>
        <tr><th>ID</th><th>Title</th><th>Author</th><th>Price</th><th>Actions</th></tr>
        {% for book in books %}
        <tr>
            <td>{{ book.id }}</td>
            <td>{{ book.title }}</td>
            <td>{{ book.author }}</td>
            <td>{{ "%.2f"|format(book.price) }}</td>
            <td>
                <a href="/edit/{{ book.id }}">Edit</a>
                <form method="POST" action="/delete/{{ book.id }}" style="display:inline;padding:0">
                    <button type="submit">Delete</button>
                </form>
            </td>
        </tr>
        {% else %}
        <tr><td colspan="5">No books added yet.</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""


@app.route("/")
def home():
    conn = get_db()
    books = conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(HTML, books=books, edit=None)


@app.route("/add", methods=["POST"])
def add_book():
    title = request.form["title"].strip()
    author = request.form["author"].strip()
    price = float(request.form["price"])

    conn = get_db()
    conn.execute(
        "INSERT INTO books (title, author, price) VALUES (?, ?, ?)",
        (title, author, price)
    )
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/edit/<int:book_id>")
def edit_book(book_id):
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    books = conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
    conn.close()

    if book is None:
        return "Book not found", 404

    return render_template_string(HTML, books=books, edit=book)


@app.route("/update/<int:book_id>", methods=["POST"])
def update_book(book_id):
    title = request.form["title"].strip()
    author = request.form["author"].strip()
    price = float(request.form["price"])

    conn = get_db()
    conn.execute(
        "UPDATE books SET title = ?, author = ?, price = ? WHERE id = ?",
        (title, author, price, book_id)
    )
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    conn = get_db()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return redirect("/")


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
