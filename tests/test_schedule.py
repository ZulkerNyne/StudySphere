from studysphere.models import Course


def setup_auth(client, db):
    client.post("/api/auth/register", json={
        "student_id": "STU001",
        "name": "Test Student",
        "email": "test@example.com",
        "password": "pass123",
        "program": "Computer Science",
        "degree_status": "Undergraduate",
        "status": "Full-time",
    })
    resp = client.post("/api/auth/login", json={
        "student_id": "STU001",
        "password": "pass123",
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def seed_and_enroll(client, db, headers):
    courses = [
        Course(
            course_number="CMPUT101",
            course_name="Intro to Computing",
            professor_name="Dr. Smith",
            start_time="09:00 AM",
            end_time="10:30 AM",
            level="Undergraduate",
            credits=3,
            total_seats=40,
            available_seats=10,
            semester="Fall",
            days="Monday, Wednesday",
        ),
        Course(
            course_number="MATH101",
            course_name="Calculus I",
            professor_name="Dr. Lee",
            start_time="02:00 PM",
            end_time="03:30 PM",
            level="Undergraduate",
            credits=4,
            total_seats=30,
            available_seats=5,
            semester="Fall",
            days="Tuesday, Thursday",
        ),
    ]
    for c in courses:
        db.session.add(c)
    db.session.commit()

    client.post("/api/enrollment/enroll", json={"course_number": "CMPUT101"}, headers=headers)
    client.post("/api/enrollment/enroll", json={"course_number": "MATH101"}, headers=headers)


def test_schedule_returns_by_day(client, db):
    headers = setup_auth(client, db)
    seed_and_enroll(client, db, headers)

    resp = client.get("/api/schedule/STU001", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Monday" in data
    assert "Tuesday" in data
    assert data["Monday"][0]["course_number"] == "CMPUT101"


def test_schedule_empty(client, db):
    headers = setup_auth(client, db)
    resp = client.get("/api/schedule/STU001", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json() == {}
