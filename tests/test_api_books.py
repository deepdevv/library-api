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
