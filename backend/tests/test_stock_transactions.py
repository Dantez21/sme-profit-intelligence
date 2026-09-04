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


def create_product(client):
    category_id = create_category(client)

    response = client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "BEEF-RIBEYE-STOCK-001",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_warehouse(client):
    response = client.post(
        "/api/v1/warehouses",
        json={
            "name": "Main Warehouse",
            "code": "MAIN",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_stock_transaction(
    client,
    product_id,
    warehouse_id,
    transaction_type,
    quantity,
):
    return client.post(
        "/api/v1/stock-transactions",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "transaction_type": transaction_type,
            "quantity": quantity,
        },
    )


def test_create_opening_stock(client):
    product_id = create_product(client)
    warehouse_id = create_warehouse(client)

    response = create_stock_transaction(
        client,
        product_id,
        warehouse_id,
        "opening",
        100,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["product_id"] == product_id
    assert data["warehouse_id"] == warehouse_id
    assert data["transaction_type"] == "opening"
    assert data["quantity"] == "100.000"


def test_purchase_increases_stock(client):
    product_id = create_product(client)
    warehouse_id = create_warehouse(client)

    response = create_stock_transaction(
        client,
        product_id,
        warehouse_id,
        "purchase",
        50,
    )

    assert response.status_code == 201

    stock_response = client.get(
        "/api/v1/stock-transactions/stock",
        params={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
        },
    )

    assert stock_response.status_code == 200

    data = stock_response.json()

    assert data["stock_quantity"] == "50.000"
    assert data["unit"] == "kg"


def test_sale_decreases_stock(client):
    product_id = create_product(client)
    warehouse_id = create_warehouse(client)

    opening_response = create_stock_transaction(
        client,
        product_id,
        warehouse_id,
        "opening",
        100,
    )

    assert opening_response.status_code == 201

    sale_response = create_stock_transaction(
        client,
        product_id,
        warehouse_id,
        "sale",
        30,
    )

    assert sale_response.status_code == 201
    assert sale_response.json()["quantity"] == "-30.000"

    stock_response = client.get(
        "/api/v1/stock-transactions/stock",
        params={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
        },
    )

    assert stock_response.status_code == 200
    assert stock_response.json()["stock_quantity"] == "70.000"


def test_sale_cannot_exceed_available_stock(client):
    product_id = create_product(client)
    warehouse_id = create_warehouse(client)

    opening_response = create_stock_transaction(
        client,
        product_id,
        warehouse_id,
        "opening",
        20,
    )

    assert opening_response.status_code == 201

    sale_response = create_stock_transaction(
        client,
        product_id,
        warehouse_id,
        "sale",
        25,
    )

    assert sale_response.status_code == 409

    assert "Insufficient stock" in (
        sale_response.json()["detail"]
    )


def test_transfer_out_cannot_exceed_available_stock(client):
    product_id = create_product(client)
    warehouse_id = create_warehouse(client)

    opening_response = create_stock_transaction(
        client,
        product_id,
        warehouse_id,
        "opening",
        10,
    )

    assert opening_response.status_code == 201

    response = create_stock_transaction(
        client,
        product_id,
        warehouse_id,
        "transfer_out",
        15,
    )

    assert response.status_code == 409


def test_invalid_product_is_rejected(client):
    warehouse_id = create_warehouse(client)

    response = create_stock_transaction(
        client,
        9999,
        warehouse_id,
        "purchase",
        10,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_invalid_warehouse_is_rejected(client):
    product_id = create_product(client)

    response = create_stock_transaction(
        client,
        product_id,
        9999,
        "purchase",
        10,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Warehouse not found."


def test_get_stock_for_missing_product_is_rejected(client):
    warehouse_id = create_warehouse(client)

    response = client.get(
        "/api/v1/stock-transactions/stock",
        params={
            "product_id": 9999,
            "warehouse_id": warehouse_id,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_get_stock_for_missing_warehouse_is_rejected(client):
    product_id = create_product(client)

    response = client.get(
        "/api/v1/stock-transactions/stock",
        params={
            "product_id": product_id,
            "warehouse_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Warehouse not found."


def test_list_stock_transactions(client):
    product_id = create_product(client)
    warehouse_id = create_warehouse(client)

    first = create_stock_transaction(
        client,
        product_id,
        warehouse_id,
        "opening",
        100,
    )

    second = create_stock_transaction(
        client,
        product_id,
        warehouse_id,
        "sale",
        20,
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get("/api/v1/stock-transactions")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["transaction_type"] == "sale"
    assert data[1]["transaction_type"] == "opening"