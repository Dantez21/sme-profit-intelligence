def test_create_product(client):
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "BEEF-RIBEYE-TEST-001",
            "description": "Premium ribeye beef cut",
            "category": "Beef Cuts",
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Ribeye Steak"
    assert data["sku"] == "BEEF-RIBEYE-TEST-001"
    assert data["category"] == "Beef Cuts"


def test_list_products(client):
    client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "BEEF-RIBEYE-TEST-002",
            "category": "Beef Cuts",
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    response = client.get("/api/v1/products")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Ribeye Steak"


def test_get_product(client):
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "T-Bone Steak",
            "sku": "BEEF-TBONE-TEST-001",
            "category": "Beef Cuts",
            "unit": "kg",
            "cost_price": 900.00,
            "selling_price": 1400.00,
        },
    )

    product_id = create_response.json()["id"]

    response = client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "T-Bone Steak"


def test_update_product(client):
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "BEEF-RIBEYE-TEST-003",
            "category": "Beef Cuts",
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    product_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "selling_price": 1350.00,
        },
    )

    assert response.status_code == 200
    assert response.json()["selling_price"] == "1350.00"


def test_delete_product(client):
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Sirloin Steak",
            "sku": "BEEF-SIRLOIN-TEST-001",
            "category": "Beef Cuts",
            "unit": "kg",
            "cost_price": 800.00,
            "selling_price": 1200.00,
        },
    )

    product_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/products/{product_id}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/products/{product_id}"
    )

    assert get_response.status_code == 404


def test_duplicate_sku_is_rejected(client):
    product = {
        "name": "Ribeye Steak",
        "sku": "BEEF-RIBEYE-DUPLICATE",
        "category": "Beef Cuts",
        "unit": "kg",
        "cost_price": 850.00,
        "selling_price": 1250.00,
    }

    first_response = client.post(
        "/api/v1/products",
        json=product,
    )

    second_response = client.post(
        "/api/v1/products",
        json=product,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_product_not_found(client):
    response = client.get("/api/v1/products/99999")

    assert response.status_code == 404