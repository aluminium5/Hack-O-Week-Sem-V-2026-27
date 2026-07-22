from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_books_api_returns_json(client):
    response = client.get("/api/books")
    assert response.status_code == 200
    books = response.get_json()
    assert isinstance(books, list)
    assert len(books) >= 2


def test_create_book_via_api(client):
    response = client.post(
        "/api/books",
        json={"title": "The Hobbit", "author": "J.R.R. Tolkien"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "The Hobbit"
    assert data["author"] == "J.R.R. Tolkien"


def test_update_and_delete_book(client):
    create_response = client.post(
        "/api/books",
        json={"title": "Test Book", "author": "Test Author"},
    )
    book_id = create_response.get_json()["id"]

    update_response = client.put(
        f"/api/books/{book_id}",
        json={"title": "Updated Book", "author": "Updated Author"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["title"] == "Updated Book"

    delete_response = client.delete(f"/api/books/{book_id}")
    assert delete_response.status_code == 200

    missing_response = client.get(f"/api/books/{book_id}")
    assert missing_response.status_code == 404


def test_books_page_renders_table(client):
    response = client.get("/books")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Library Management System" in html
    assert "Books Table" in html
