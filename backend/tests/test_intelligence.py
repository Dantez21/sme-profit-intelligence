from decimal import Decimal


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


def create_product(
    client,
    name="Ribeye Steak",
    sku="INTEL-001",
    cost_price=850.00,
    selling_price=1250.00,
):
    category_id = create_category(
        client,
        name=f"Category-{sku}",
    )

    response = client.post(
        "/api/v1/products",
        json={
            "name": name,
            "sku": sku,
            "category_id": category_id,
            "unit": "kg",
            "cost_price": cost_price,
            "selling_price": selling_price,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_customer(client):
    response = client.post(
        "/api/v1/customers",
        json={
            "name": "Intelligence Customer",
            "code": "INTEL-CUST-001",
            "email": "intel@example.com",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_warehouse(client):
    response = client.post(
        "/api/v1/warehouses",
        json={
            "name": "Intelligence Warehouse",
            "code": "INTEL-WH-001",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_sale(
    client,
    customer_id,
    warehouse_id,
    product_id,
    quantity,
    unit_price,
):
    response = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer_id,
            "warehouse_id": warehouse_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                }
            ],
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_stock(
    client,
    product_id,
    warehouse_id,
    quantity,
):
    response = client.post(
        "/api/v1/stock-transactions",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "transaction_type": "opening",
            "quantity": quantity,
        },
    )

    assert response.status_code == 201


def submit_sale(client, sale_id):
    response = client.post(
        f"/api/v1/sales/{sale_id}/submit"
    )

    assert response.status_code == 200


def test_profit_summary_with_one_submitted_sale(client):
    product_id = create_product(
        client,
        cost_price=850.00,
        selling_price=1250.00,
    )

    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    create_stock(
        client,
        product_id,
        warehouse_id,
        10,
    )

    sale_id = create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
        quantity=2,
        unit_price=1250.00,
    )

    submit_sale(client, sale_id)

    response = client.get(
        "/api/v1/intelligence/profit-summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["revenue"]) == Decimal("2500.00")
    assert Decimal(data["cogs"]) == Decimal("1700.00")
    assert Decimal(data["gross_profit"]) == Decimal("800.00")
    assert Decimal(data["gross_margin"]) == Decimal("32.00")


def test_draft_sale_is_excluded_from_profit_summary(client):
    product_id = create_product(
        client,
        sku="INTEL-002",
        cost_price=500.00,
        selling_price=800.00,
    )

    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
        quantity=5,
        unit_price=800.00,
    )

    response = client.get(
        "/api/v1/intelligence/profit-summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["revenue"]) == Decimal("0")
    assert Decimal(data["cogs"]) == Decimal("0")
    assert Decimal(data["gross_profit"]) == Decimal("0")
    assert Decimal(data["gross_margin"]) == Decimal("0")


def test_multiple_submitted_sales_are_aggregated(client):
    product_id = create_product(
        client,
        sku="INTEL-003",
        cost_price=500.00,
        selling_price=800.00,
    )

    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    create_stock(
        client,
        product_id,
        warehouse_id,
        100,
    )

    first_sale = create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
        quantity=10,
        unit_price=800.00,
    )

    second_sale = create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
        quantity=5,
        unit_price=800.00,
    )

    submit_sale(client, first_sale)
    submit_sale(client, second_sale)

    response = client.get(
        "/api/v1/intelligence/profit-summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["revenue"]) == Decimal("12000.00")
    assert Decimal(data["cogs"]) == Decimal("7500.00")
    assert Decimal(data["gross_profit"]) == Decimal("4500.00")
    assert Decimal(data["gross_margin"]) == Decimal("37.50")


def test_profit_summary_with_no_sales(client):
    response = client.get(
        "/api/v1/intelligence/profit-summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["revenue"]) == Decimal("0")
    assert Decimal(data["cogs"]) == Decimal("0")
    assert Decimal(data["gross_profit"]) == Decimal("0")
    assert Decimal(data["gross_margin"]) == Decimal("0")


def test_product_profitability_ranks_by_revenue(client):
    category_id = create_category(client)

    first_product = client.post(
        "/api/v1/products",
        json={
            "name": "Ribeye Steak",
            "sku": "PROFIT-001",
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
            "sku": "PROFIT-002",
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

    create_stock(
        client,
        first_product_id,
        warehouse_id,
        100,
    )

    create_stock(
        client,
        second_product_id,
        warehouse_id,
        100,
    )

    first_sale = create_sale(
        client,
        customer_id,
        warehouse_id,
        first_product_id,
        quantity=20,
        unit_price=1250.00,
    )

    second_sale = create_sale(
        client,
        customer_id,
        warehouse_id,
        second_product_id,
        quantity=10,
        unit_price=1200.00,
    )

    submit_sale(client, first_sale)
    submit_sale(client, second_sale)

    response = client.get(
        "/api/v1/intelligence/product-profitability"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["product_id"] == first_product_id
    assert Decimal(data[0]["quantity_sold"]) == Decimal("20.000")
    assert Decimal(data[0]["revenue"]) == Decimal("25000.00")
    assert Decimal(data[0]["cogs"]) == Decimal("17000.00")
    assert Decimal(data[0]["gross_profit"]) == Decimal("8000.00")
    assert Decimal(data[0]["gross_margin"]).quantize(Decimal("0.01")) == Decimal("32.00")

    assert data[1]["product_id"] == second_product_id
    assert Decimal(data[1]["quantity_sold"]) == Decimal("10.000")
    assert Decimal(data[1]["revenue"]) == Decimal("12000.00")
    assert Decimal(data[1]["cogs"]) == Decimal("8000.00")
    assert Decimal(data[1]["gross_profit"]) == Decimal("4000.00")
    assert Decimal(data[1]["gross_margin"]).quantize(Decimal("0.01")) == Decimal("33.33")


def test_product_profitability_excludes_draft_sales(client):
    product_id = create_product(
        client,
        sku="PROFIT-003",
        cost_price=500.00,
        selling_price=800.00,
    )

    customer_id = create_customer(client)
    warehouse_id = create_warehouse(client)

    create_sale(
        client,
        customer_id,
        warehouse_id,
        product_id,
        quantity=10,
        unit_price=800.00,
    )

    response = client.get(
        "/api/v1/intelligence/product-profitability"
    )

    assert response.status_code == 200

    data = response.json()

    assert data == []