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
            "sku": "BEEF-RIBEYE-PURCHASE-001",
            "category_id": category_id,
            "unit": "kg",
            "cost_price": 850.00,
            "selling_price": 1250.00,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_supplier(client):
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Beef Suppliers Ltd",
            "code": "SUP-PURCHASE-001",
            "email": "supplier@example.com",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_warehouse(client):
    response = client.post(
        "/api/v1/warehouses",
        json={
            "name": "Main Warehouse",
            "code": "WH-PURCHASE-001",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_purchase(
    client,
    supplier_id,
    warehouse_id,
    product_id,
    quantity=100,
    unit_cost=850.00,
):
    return client.post(
        "/api/v1/purchases",
        json={
            "supplier_id": supplier_id,
            "warehouse_id": warehouse_id,
            "reference": "PO-TEST-001",
            "notes": "Test purchase",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_cost": unit_cost,
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


def test_create_purchase_as_draft(client):
    product_id = create_product(client)
    supplier_id = create_supplier(client)
    warehouse_id = create_warehouse(client)

    response = create_purchase(
        client,
        supplier_id,
        warehouse_id,
        product_id,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["supplier_id"] == supplier_id
    assert data["warehouse_id"] == warehouse_id
    assert data["status"] == "draft"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product_id
    assert data["items"][0]["quantity"] == "100.000"
    assert data["items"][0]["unit_cost"] == "850.00"


def test_draft_purchase_does_not_change_stock(client):
    product_id = create_product(client)
    supplier_id = create_supplier(client)
    warehouse_id = create_warehouse(client)

    purchase_response = create_purchase(
        client,
        supplier_id,
        warehouse_id,
        product_id,
        quantity=100,
    )

    assert purchase_response.status_code == 201

    stock_response = get_stock(
        client,
        product_id,
        warehouse_id,
    )

    assert stock_response.status_code == 200
    assert stock_response.json()["stock_quantity"] == "0.000"


def test_submitting_purchase_increases_stock(client):
    product_id = create_product(client)
    supplier_id = create_supplier(client)
    warehouse_id = create_warehouse(client)

    purchase_response = create_purchase(
        client,
        supplier_id,
        warehouse_id,
        product_id,
        quantity=100,
    )

    assert purchase_response.status_code == 201

    purchase_id = purchase_response.json()["id"]

    submit_response = client.post(
        f"/api/v1/purchases/{purchase_id}/submit"
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
    assert stock_response.json()["stock_quantity"] == "100.000"


def test_submitting_purchase_creates_stock_transaction(client):
    product_id = create_product(client)
    supplier_id = create_supplier(client)
    warehouse_id = create_warehouse(client)

    purchase_response = create_purchase(
        client,
        supplier_id,
        warehouse_id,
        product_id,
        quantity=75,
    )

    purchase_id = purchase_response.json()["id"]

    submit_response = client.post(
        f"/api/v1/purchases/{purchase_id}/submit"
    )

    assert submit_response.status_code == 200

    response = client.get(
        "/api/v1/stock-transactions"
    )

    assert response.status_code == 200

    transactions = response.json()

    assert len(transactions) == 1
    assert transactions[0]["transaction_type"] == "purchase"
    assert transactions[0]["quantity"] == "75.000"
    assert transactions[0]["product_id"] == product_id
    assert transactions[0]["warehouse_id"] == warehouse_id


def test_purchase_cannot_be_submitted_twice(client):
    product_id = create_product(client)
    supplier_id = create_supplier(client)
    warehouse_id = create_warehouse(client)

    purchase_response = create_purchase(
        client,
        supplier_id,
        warehouse_id,
        product_id,
        quantity=50,
    )

    purchase_id = purchase_response.json()["id"]

    first_submit = client.post(
        f"/api/v1/purchases/{purchase_id}/submit"
    )

    second_submit = client.post(
        f"/api/v1/purchases/{purchase_id}/submit"
    )

    assert first_submit.status_code == 200
    assert second_submit.status_code == 409

    assert second_submit.json()["detail"] == (
        "Purchase has already been submitted."
    )


def test_purchase_with_missing_supplier_is_rejected(client):
    product_id = create_product(client)
    warehouse_id = create_warehouse(client)

    response = create_purchase(
        client,
        supplier_id=9999,
        warehouse_id=warehouse_id,
        product_id=product_id,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found."


def test_purchase_with_missing_warehouse_is_rejected(client):
    product_id = create_product(client)
    supplier_id = create_supplier(client)

    response = create_purchase(
        client,
        supplier_id=supplier_id,
        warehouse_id=9999,
        product_id=product_id,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Warehouse not found."


def test_purchase_with_missing_product_is_rejected(client):
    supplier_id = create_supplier(client)
    warehouse_id = create_warehouse(client)

    response = create_purchase(
        client,
        supplier_id=supplier_id,
        warehouse_id=warehouse_id,
        product_id=9999,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Product 9999 not found."
    )


def test_purchase_requires_at_least_one_item(client):
    supplier_id = create_supplier(client)
    warehouse_id = create_warehouse(client)

    response = client.post(
        "/api/v1/purchases",
        json={
            "supplier_id": supplier_id,
            "warehouse_id": warehouse_id,
            "items": [],
        },
    )

    assert response.status_code == 422