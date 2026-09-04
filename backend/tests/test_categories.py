def test_create_category(client):
    response = client.post(
        "/api/v1/categories",
        json={
            "name": "Beef Cuts",
            "description": "Beef product category",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Beef Cuts"
    assert data["description"] == "Beef product category"
    assert "id" in data
    assert "created_at" in data


def test_list_categories(client):
    client.post(
        "/api/v1/categories",
        json={
            "name": "Beef Cuts",
            "description": "Beef products",
        },
    )

    client.post(
        "/api/v1/categories",
        json={
            "name": "Dairy",
            "description": "Dairy products",
        },
    )

    response = client.get("/api/v1/categories")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Dairy"
    assert data[1]["name"] == "Beef Cuts"


def test_get_category(client):
    create_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Beef Cuts",
            "description": "Beef products",
        },
    )

    assert create_response.status_code == 201

    category_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/categories/{category_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == category_id
    assert data["name"] == "Beef Cuts"


def test_update_category(client):
    create_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Beef Cuts",
            "description": "Beef products",
        },
    )

    assert create_response.status_code == 201

    category_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/categories/{category_id}",
        json={
            "name": "Premium Beef Cuts",
            "description": "Premium beef products",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Premium Beef Cuts"
    assert data["description"] == "Premium beef products"


def test_delete_category(client):
    create_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Beef Cuts",
            "description": "Beef products",
        },
    )

    assert create_response.status_code == 201

    category_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/categories/{category_id}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/categories/{category_id}"
    )

    assert get_response.status_code == 404


def test_duplicate_category_is_rejected(client):
    category = {
        "name": "Beef Cuts",
        "description": "Beef products",
    }

    first_response = client.post(
        "/api/v1/categories",
        json=category,
    )

    second_response = client.post(
        "/api/v1/categories",
        json=category,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json()["detail"] == (
        "A category with this name already exists."
    )


def test_category_not_found(client):
    response = client.get("/api/v1/categories/9999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Category not found."


def test_update_category_not_found(client):
    response = client.put(
        "/api/v1/categories/9999",
        json={
            "name": "Updated Category",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Category not found."
    

def test_delete_category_with_products_is_rejected(client):
    category_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Beef Cuts",
            "description": "Beef products",
        },
    )

    assert category_response.status_code == 201

    category_id = category_response.json()["id"]

    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "BEEF-RIBEYE-CATEGORY-DELETE-001",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    assert product_response.status_code == 201

    response = client.delete(
        f"/api/v1/categories/{category_id}"
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Cannot delete a category that is assigned to products."
    )