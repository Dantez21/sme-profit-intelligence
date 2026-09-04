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
            "sku": "BEEF-RIBEYE-SALE-001",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_customer(client):
    response = client.post(
        "/api/v1/customers",
        json={
            "name": "Walk-in Customer",
            "code": "CUST-SALE-001",
            "email": "customer@example.com",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_warehouse(client):
    response = client.post(
        "/api/v1/warehouses",
        json={
            "name": "Main Warehouse",
            "code": "WH-SALE-001",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_opening_stock(
    client,
    product_id,
    warehouse_id,
    quantity,
):
    return client.post(
        "/api/v1/stock-transactions",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "transaction_type": "opening",
            "quantity": quantity,
        },
    )


def create_sale(
    client,
    customer_id,
    warehouse_id,
    product_id,
    quantity=10,
    unit_price=1250.00,
):
    return client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer_id,
            "warehouse_id": warehouse_id,
            "reference": "SALE-TEST-001",
            "notes": "Test sale",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                }
            ],
        },
    )


def get_stock(client, product_id, warehouse_id):
    return client.get(
        "/api/v1/stock-transactions/stock",
        params={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
        },
    )


def test_create_sale_as_draft(client):
    product_id = create_product(client)
    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    response = create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["customer_id"] == customer_id
    assert data["warehouse_id"] == warehouse_id
    assert data["status"] == "draft"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product_id
    assert data["items"][0]["quantity"] == "10.000"
    assert data["items"][0]["unit_price"] == "1250.00"


def test_draft_sale_does_not_change_stock(client):
    product_id = create_product(client)
    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    opening_response = create_opening_stock(
        client,
        product_id,
        warehouse_id,
        100,
    )

    assert opening_response.status_code == 201

    sale_response = create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
        quantity=20,
    )

    assert sale_response.status_code == 201

    stock_response = get_stock(
        client,
        product_id,
        warehouse_id,
    )

    assert stock_response.status_code == 200
    assert stock_response.json()["stock_quantity"] == "100.000"


def test_submitting_sale_decreases_stock(client):
    product_id = create_product(client)
    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    opening_response = create_opening_stock(
        client,
        product_id,
        warehouse_id,
        100,
    )

    assert opening_response.status_code == 201

    sale_response = create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
        quantity=30,
    )

    assert sale_response.status_code == 201

    sale_id = sale_response.json()["id"]

    submit_response = client.post(
        f"/api/v1/sales/{sale_id}/submit"
    )

    assert submit_response.status_code == 200

    data = submit_response.json()

    assert data["status"] == "submitted"

    stock_response = get_stock(
        client,
        product_id,
        warehouse_id,
    )

    assert stock_response.status_code == 200
    assert stock_response.json()["stock_quantity"] == "70.000"


def test_submitting_sale_creates_stock_transaction(client):
    product_id = create_product(client)
    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    create_opening_stock(
        client,
        product_id,
        warehouse_id,
        100,
    )

    sale_response = create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
        quantity=25,
    )

    sale_id = sale_response.json()["id"]

    submit_response = client.post(
        f"/api/v1/sales/{sale_id}/submit"
    )

    assert submit_response.status_code == 200

    response = client.get(
        "/api/v1/stock-transactions"
    )

    assert response.status_code == 200

    transactions = response.json()

    assert len(transactions) == 2

    sale_transaction = next(
        transaction
        for transaction in transactions
        if transaction["transaction_type"] == "sale"
    )

    assert sale_transaction["quantity"] == "-25.000"
    assert sale_transaction["product_id"] == product_id
    assert sale_transaction["warehouse_id"] == warehouse_id


def test_sale_cannot_exceed_available_stock(client):
    product_id = create_product(client)
    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    create_opening_stock(
        client,
        product_id,
        warehouse_id,
        20,
    )

    sale_response = create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
        quantity=25,
    )

    sale_id = sale_response.json()["id"]

    submit_response = client.post(
        f"/api/v1/sales/{sale_id}/submit"
    )

    assert submit_response.status_code == 409

    assert "Insufficient stock" in (
        submit_response.json()["detail"]
    )

    stock_response = get_stock(
        client,
        product_id,
        warehouse_id,
    )

    assert stock_response.json()["stock_quantity"] == "20.000"


def test_multi_item_sale_is_atomic(client):
    category_id = create_category(client)

    first_product = client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "SALE-ATOMIC-001",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    second_product = client.post(
        "/api/v1/products",
        json={
            "name": "Sirloin Steak",
            "sku": "SALE-ATOMIC-002",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 800.00,
            "selling_price": 1200.00,
        },
    )

    assert first_product.status_code == 201
    assert second_product.status_code == 201

    first_product_id = first_product.json()["id"]
    second_product_id = second_product.json()["id"]

    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    first_stock = create_opening_stock(
        client,
        first_product_id,
        warehouse_id,
        100,
    )

    second_stock = create_opening_stock(
        client,
        second_product_id,
        warehouse_id,
        5,
    )

    assert first_stock.status_code == 201
    assert second_stock.status_code == 201

    sale_response = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer_id,
            "warehouse_id": warehouse_id,
            "reference": "SALE-ATOMIC-001",
            "items": [
                {
                    "product_id": first_product_id,
                    "quantity": 20,
                    "unit_price": 1250.00,
                },
                {
                    "product_id": second_product_id,
                    "quantity": 10,
                    "unit_price": 1200.00,
                },
            ],
        },
    )

    assert sale_response.status_code == 201

    sale_id = sale_response.json()["id"]

    submit_response = client.post(
        f"/api/v1/sales/{sale_id}/submit"
    )

    assert submit_response.status_code == 409

    first_stock_response = get_stock(
        client,
        first_product_id,
        warehouse_id,
    )

    second_stock_response = get_stock(
        client,
        second_product_id,
        warehouse_id,
    )

    assert first_stock_response.json()["stock_quantity"] == "100.000"
    assert second_stock_response.json()["stock_quantity"] == "5.000"


def test_sale_cannot_be_submitted_twice(client):
    product_id = create_product(client)
    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    create_opening_stock(
        client,
        product_id,
        warehouse_id,
        50,
    )

    sale_response = create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
        quantity=10,
    )

    sale_id = sale_response.json()["id"]

    first_submit = client.post(
        f"/api/v1/sales/{sale_id}/submit"
    )

    second_submit = client.post(
        f"/api/v1/sales/{sale_id}/submit"
    )

    assert first_submit.status_code == 200
    assert second_submit.status_code == 409

    assert second_submit.json()["detail"] == (
        "Sale has already been submitted."
    )


def test_sale_with_missing_customer_is_rejected(client):
    product_id = create_product(client)
    warehouse_id = create_warehouse(client)

    response = create_sale(
        client,
        customer_id=9999,
        warehouse_id=warehouse_id,
        product_id=product_id,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found."


def test_sale_with_missing_warehouse_is_rejected(client):
    product_id = create_product(client)
    customer_id = create_customer(client)

    response = create_sale(
        client,
        customer_id=customer_id,
        warehouse_id=9999,
        product_id=product_id,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Warehouse not found."


def test_sale_with_missing_product_is_rejected(client):
    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    response = create_sale(
        client,
        customer_id=customer_id,
        warehouse_id=warehouse_id,
        product_id=9999,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Product 9999 not found."
    )


def test_sale_requires_at_least_one_item(client):
    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    response = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer_id,
            "warehouse_id": warehouse_id,
            "items": [],
        },
    )

    assert response.status_code == 422