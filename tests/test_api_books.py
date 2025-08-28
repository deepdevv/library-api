import pytest
from datetime import datetime

from app.schemas.books import BookCreate

@pytest.mark.asyncio
async def test_create_and_get_book(client):
    # Create
    payload = {"serial_number": "100001", "title": "API Book", "author": "Tester"}
    r = await client.post("/api/v1/books", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["serial_number"] == "100001"
    assert data["is_borrowed"] is False

    # Duplicate create → 409
    r2 = await client.post("/api/v1/books", json=payload)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "conflict"

    # List
    r3 = await client.get("/api/v1/books")
    assert r3.status_code == 200
    list_data = r3.json()
    assert list_data["total"] >= 1
    assert any(b["serial_number"] == "100001" for b in list_data["items"])


@pytest.mark.asyncio
async def test_borrow_and_return_book(client):
    # Create
    await client.post("/api/v1/books", json={"serial_number": "200001", "title": "Borrow me", "author": "X"})

    # Borrow
    r = await client.patch("/api/v1/books/200001/status", json={"action": "borrow", "borrower_card": "654321"})
    assert r.status_code == 200
    data = r.json()
    assert data["is_borrowed"] is True
    assert data["borrower_card"] == "654321"
    assert isinstance(datetime.fromisoformat(data["borrowed_at"].replace("Z","+00:00")), datetime)

    # Return
    r2 = await client.patch("/api/v1/books/200001/status", json={"action": "return"})
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["is_borrowed"] is False
    assert d2["borrower_card"] is None

    # Returning again conflicts
    r3 = await client.patch("/api/v1/books/200001/status", json={"action": "return"})
    assert r3.status_code == 409


@pytest.mark.asyncio
async def test_delete_book(client):
    # Create
    await client.post("/api/v1/books", json={"serial_number": "300001", "title": "Delete me", "author": "Y"})

    # Delete
    r = await client.delete("/api/v1/books/300001")
    assert r.status_code == 204

    # Delete again → 404
    r2 = await client.delete("/api/v1/books/300001")
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_list_books_with_filters(client):
    # Create two books
    await client.post("/api/v1/books", json={"serial_number": "400001", "title": "Alpha", "author": "Tester"})
    await client.post("/api/v1/books", json={"serial_number": "400002", "title": "Beta", "author": "Tester"})

    # Borrow one
    await client.patch("/api/v1/books/400001/status", json={"action": "borrow", "borrower_card": "123456"})

    # Filter by is_borrowed=true
    r = await client.get("/api/v1/books", params={"is_borrowed": True})
    assert r.status_code == 200
    data = r.json()
    assert all(item["is_borrowed"] for item in data["items"])

    # Filter by title substring
    r2 = await client.get("/api/v1/books", params={"title": "Beta"})
    assert r2.status_code == 200
    data2 = r2.json()
    assert all("Beta" in item["title"] for item in data2["items"])


@pytest.mark.asyncio
async def test_error_envelope_shape_on_conflict(client):
    # Create a book
    payload = {"serial_number": "500001", "title": "Conflict", "author": "Z"}
    await client.post("/api/v1/books", json=payload)

    # Create again → conflict
    r = await client.post("/api/v1/books", json=payload)
    assert r.status_code == 409
    body = r.json()
    assert "error" in body
    assert set(body["error"].keys()) == {"code", "message", "details"}
    assert body["error"]["code"] == "conflict"
