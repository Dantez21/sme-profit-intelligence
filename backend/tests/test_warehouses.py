def create_warehouse(
    client,
    name="Main Warehouse",
    code="MAIN",
):
    response = client.post(
        "/api/v1/warehouses",
        json={
            "name": name,
            "code": code,
            "description": "Primary business warehouse",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_warehouse(client):
    response = client.post(
        "/api/v1/warehouses",
        json={
            "name": "Main Warehouse",
            "code": "MAIN",
            "description": "Primary business warehouse",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Main Warehouse"
    assert data["code"] == "MAIN"
    assert data["description"] == "Primary business warehouse"
    assert data["is_active"] is True


def test_list_warehouses(client):
    create_warehouse(client)

    response = client.get("/api/v1/warehouses")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Main Warehouse"


def test_get_warehouse(client):
    warehouse = create_warehouse(client)

    warehouse_id = warehouse["id"]

    response = client.get(
        f"/api/v1/warehouses/{warehouse_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == warehouse_id
    assert data["name"] == "Main Warehouse"
    assert data["code"] == "MAIN"


def test_update_warehouse(client):
    warehouse = create_warehouse(client)

    warehouse_id = warehouse["id"]

    response = client.put(
        f"/api/v1/warehouses/{warehouse_id}",
        json={
            "name": "Central Warehouse",
            "code": "CENTRAL",
            "description": "Updated warehouse",
            "is_active": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Central Warehouse"
    assert data["code"] == "CENTRAL"
    assert data["description"] == "Updated warehouse"
    assert data["is_active"] is False


def test_delete_warehouse(client):
    warehouse = create_warehouse(client)

    warehouse_id = warehouse["id"]

    response = client.delete(
        f"/api/v1/warehouses/{warehouse_id}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/warehouses/{warehouse_id}"
    )

    assert get_response.status_code == 404


def test_duplicate_warehouse_name_is_rejected(client):
    create_warehouse(client)

    response = client.post(
        "/api/v1/warehouses",
        json={
            "name": "Main Warehouse",
            "code": "MAIN-2",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A warehouse with this name or code already exists."
    )


def test_duplicate_warehouse_code_is_rejected(client):
    create_warehouse(client)

    response = client.post(
        "/api/v1/warehouses",
        json={
            "name": "Secondary Warehouse",
            "code": "MAIN",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A warehouse with this name or code already exists."
    )


def test_warehouse_not_found(client):
    response = client.get("/api/v1/warehouses/9999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Warehouse not found."


def test_update_warehouse_not_found(client):
    response = client.put(
        "/api/v1/warehouses/9999",
        json={
            "name": "Updated Warehouse",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Warehouse not found."


def test_delete_warehouse_not_found(client):
    response = client.delete(
        "/api/v1/warehouses/9999"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Warehouse not found."


def test_update_duplicate_warehouse_name_is_rejected(client):
    create_warehouse(
        client,
        name="Main Warehouse",
        code="MAIN",
    )

    second = create_warehouse(
        client,
        name="Secondary Warehouse",
        code="SECONDARY",
    )

    response = client.put(
        f"/api/v1/warehouses/{second['id']}",
        json={
            "name": "Main Warehouse",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A warehouse with this name already exists."
    )


def test_update_duplicate_warehouse_code_is_rejected(client):
    create_warehouse(
        client,
        name="Main Warehouse",
        code="MAIN",
    )

    second = create_warehouse(
        client,
        name="Secondary Warehouse",
        code="SECONDARY",
    )

    response = client.put(
        f"/api/v1/warehouses/{second['id']}",
        json={
            "code": "MAIN",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A warehouse with this code already exists."
    )