def create_supplier(
    client,
    name="Beef Suppliers Ltd",
    code="SUP-001",
):
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": name,
            "code": code,
            "email": "supplier@example.com",
            "phone": "+254700000000",
            "address": "Nairobi, Kenya",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_supplier(client):
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Beef Suppliers Ltd",
            "code": "SUP-001",
            "email": "supplier@example.com",
            "phone": "+254700000000",
            "address": "Nairobi, Kenya",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Beef Suppliers Ltd"
    assert data["code"] == "SUP-001"
    assert data["email"] == "supplier@example.com"
    assert data["is_active"] is True


def test_list_suppliers(client):
    create_supplier(client)

    response = client.get("/api/v1/suppliers")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["code"] == "SUP-001"


def test_get_supplier(client):
    supplier = create_supplier(client)

    response = client.get(
        f"/api/v1/suppliers/{supplier['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == supplier["id"]
    assert data["name"] == "Beef Suppliers Ltd"


def test_update_supplier(client):
    supplier = create_supplier(client)

    response = client.put(
        f"/api/v1/suppliers/{supplier['id']}",
        json={
            "name": "Premium Beef Suppliers Ltd",
            "code": "SUP-002",
            "phone": "+254711111111",
            "is_active": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Premium Beef Suppliers Ltd"
    assert data["code"] == "SUP-002"
    assert data["phone"] == "+254711111111"
    assert data["is_active"] is False


def test_delete_supplier(client):
    supplier = create_supplier(client)

    response = client.delete(
        f"/api/v1/suppliers/{supplier['id']}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/suppliers/{supplier['id']}"
    )

    assert get_response.status_code == 404


def test_duplicate_supplier_code_is_rejected(client):
    create_supplier(client)

    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Another Supplier",
            "code": "SUP-001",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A supplier with this code already exists."
    )


def test_supplier_not_found(client):
    response = client.get("/api/v1/suppliers/9999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Supplier not found."


def test_update_supplier_not_found(client):
    response = client.put(
        "/api/v1/suppliers/9999",
        json={
            "name": "Updated Supplier",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Supplier not found."


def test_delete_supplier_not_found(client):
    response = client.delete(
        "/api/v1/suppliers/9999"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Supplier not found."


def test_invalid_supplier_email_is_rejected(client):
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Invalid Email Supplier",
            "code": "SUP-INVALID-001",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422


def test_update_duplicate_supplier_code_is_rejected(client):
    create_supplier(
        client,
        name="Supplier One",
        code="SUP-001",
    )

    second_supplier = create_supplier(
        client,
        name="Supplier Two",
        code="SUP-002",
    )

    response = client.put(
        f"/api/v1/suppliers/{second_supplier['id']}",
        json={
            "code": "SUP-001",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A supplier with this code already exists."
    )