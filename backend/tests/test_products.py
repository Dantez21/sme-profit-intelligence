def create_category(client, name="Beef Cuts"):
    response = client.post(
        "/api/v1/categories",
        json={
            "name": name,
            "description": "Beef product category",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_create_product(client):
    category_id = create_category(client)

    response = client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "BEEF-RIBEYE-TEST-001",
            "description": "Premium ribeye beef cut",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Ribeye Steak"
    assert data["sku"] == "BEEF-RIBEYE-TEST-001"
    assert data["category_id"] == category_id
    assert data["reorder_level"] == "0.000"


def test_list_products(client):
    category_id = create_category(client)

    client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "BEEF-RIBEYE-TEST-002",
            "category_id": category_id,
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
    assert data[0]["category_id"] == category_id


def test_get_product(client):
    category_id = create_category(client)

    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "T-Bone Steak",
            "sku": "BEEF-TBONE-TEST-001",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 900.00,
            "selling_price": 1400.00,
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/products/{product_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "T-Bone Steak"
    assert data["category_id"] == category_id


def test_update_product(client):
    category_id = create_category(client)

    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "BEEF-RIBEYE-TEST-003",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Premium Ribeye Steak",
            "selling_price": 1350.00,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Premium Ribeye Steak"
    assert data["selling_price"] == "1350.00"
    assert data["category_id"] == category_id


def test_delete_product(client):
    category_id = create_category(client)

    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Sirloin Steak",
            "sku": "BEEF-SIRLOIN-TEST-001",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 800.00,
            "selling_price": 1200.00,
        },
    )

    assert create_response.status_code == 201

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
    category_id = create_category(client)

    product = {
        "name": "Ribeye Steak",
        "sku": "BEEF-RIBEYE-DUPLICATE",
        "category_id": category_id,
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

    assert second_response.json()["detail"] == (
        "A product with this SKU already exists."
    )


def test_product_not_found(client):
    response = client.get("/api/v1/products/9999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Product not found."


def test_product_category_not_found(client):
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Invalid Category Product",
            "sku": "INVALID-CATEGORY-001",
            "category_id": 9999,
            "unit": "kg",
            "cost_price": 500.00,
            "selling_price": 800.00,
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Category not found."


def test_update_product_category_not_found(client):
    category_id = create_category(client)

    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "BEEF-RIBEYE-CATEGORY-TEST",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "category_id": 9999,
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Category not found."

