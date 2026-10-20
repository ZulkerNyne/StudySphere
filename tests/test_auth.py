import json


def register_student(client, **overrides):
    data = {
        "student_id": "STU001",
        "name": "Test Student",
        "email": "test@example.com",
        "password": "securepass123",
        "program": "Computer Science",
        "degree_status": "Undergraduate",
        "status": "Full-time",
    }
    data.update(overrides)
    return client.post("/api/auth/register", json=data)


def test_register_success(client, db):
    resp = register_student(client)
    assert resp.status_code == 201
    assert resp.get_json()["student_id"] == "STU001"


def test_register_duplicate_id(client, db):
    register_student(client)
    resp = register_student(client, email="other@example.com")
    assert resp.status_code == 409


def test_register_missing_field(client, db):
    resp = client.post("/api/auth/register", json={"student_id": "STU001"})
    assert resp.status_code == 400


def test_login_success(client, db):
    register_student(client)
    resp = client.post("/api/auth/login", json={
        "student_id": "STU001",
        "password": "securepass123",
    })
    assert resp.status_code == 200
    body = resp.get_json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_wrong_password(client, db):
    register_student(client)
    resp = client.post("/api/auth/login", json={
        "student_id": "STU001",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_refresh_token(client, db):
    register_student(client)
    login_resp = client.post("/api/auth/login", json={
        "student_id": "STU001",
        "password": "securepass123",
    })
    refresh_token = login_resp.get_json()["refresh_token"]

    resp = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()
