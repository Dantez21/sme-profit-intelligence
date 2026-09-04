def create_customer(
    client,
    name="John Doe",
    code="CUST-001",
):
    response = client.post(
        "/api/v1/customers",
        json={
            "name": name,
            "code": code,
            "email": "john@example.com",
            "phone": "+254700000000",
            "address": "Nairobi, Kenya",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_customer(client):
    response = client.post(
        "/api/v1/customers",
        json={
            "name": "John Doe",
            "code": "CUST-001",
            "email": "john@example.com",
            "phone": "+254700000000",
            "address": "Nairobi, Kenya",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "John Doe"
    assert data["code"] == "CUST-001"
    assert data["email"] == "john@example.com"
    assert data["is_active"] is True


def test_list_customers(client):
    create_customer(client)

    response = client.get("/api/v1/customers")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["code"] == "CUST-001"


def test_get_customer(client):
    customer = create_customer(client)

    response = client.get(
        f"/api/v1/customers/{customer['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == customer["id"]
    assert data["name"] == "John Doe"


def test_update_customer(client):
    customer = create_customer(client)

    response = client.put(
        f"/api/v1/customers/{customer['id']}",
        json={
            "name": "Jane Doe",
            "code": "CUST-002",
            "phone": "+254711111111",
            "is_active": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Jane Doe"
    assert data["code"] == "CUST-002"
    assert data["phone"] == "+254711111111"
    assert data["is_active"] is False


def test_delete_customer(client):
    customer = create_customer(client)

    response = client.delete(
        f"/api/v1/customers/{customer['id']}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/customers/{customer['id']}"
    )

    assert get_response.status_code == 404


def test_duplicate_customer_code_is_rejected(client):
    create_customer(client)

    response = client.post(
        "/api/v1/customers",
        json={
            "name": "Jane Doe",
            "code": "CUST-001",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A customer with this code already exists."
    )


def test_customer_not_found(client):
    response = client.get("/api/v1/customers/9999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Customer not found."


def test_update_customer_not_found(client):
    response = client.put(
        "/api/v1/customers/9999",
        json={
            "name": "Updated Customer",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Customer not found."


def test_delete_customer_not_found(client):
    response = client.delete(
        "/api/v1/customers/9999"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Customer not found."


def test_invalid_customer_email_is_rejected(client):
    response = client.post(
        "/api/v1/customers",
        json={
            "name": "Invalid Email Customer",
            "code": "CUST-INVALID-001",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422


def test_update_duplicate_customer_code_is_rejected(client):
    create_customer(
        client,
        name="John Doe",
        code="CUST-001",
    )

    second_customer = create_customer(
        client,
        name="Jane Doe",
        code="CUST-002",
    )

    response = client.put(
        f"/api/v1/customers/{second_customer['id']}",
        json={
            "code": "CUST-001",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A customer with this code already exists."
    )