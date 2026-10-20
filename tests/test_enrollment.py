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


def seed_courses(db):
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
            course_number="CMPUT201",
            course_name="Data Structures",
            professor_name="Dr. Brown",
            start_time="09:30 AM",
            end_time="11:00 AM",
            level="Undergraduate",
            credits=3,
            total_seats=35,
            available_seats=5,
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
            available_seats=1,
            semester="Fall",
            days="Tuesday, Thursday",
        ),
        Course(
            course_number="PHYS100",
            course_name="Physics Intro",
            professor_name="Dr. Patel",
            start_time="09:00 AM",
            end_time="10:00 AM",
            level="Undergraduate",
            credits=3,
            total_seats=20,
            available_seats=0,
            semester="Fall",
            days="Friday",
        ),
    ]
    for c in courses:
        db.session.add(c)
    db.session.commit()


def test_enroll_success(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    resp = client.post("/api/enrollment/enroll", json={"course_number": "CMPUT101"}, headers=headers)
    assert resp.status_code == 201


def test_enroll_duplicate(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    client.post("/api/enrollment/enroll", json={"course_number": "CMPUT101"}, headers=headers)
    resp = client.post("/api/enrollment/enroll", json={"course_number": "CMPUT101"}, headers=headers)
    assert resp.status_code == 409
    assert "Already enrolled" in resp.get_json()["error"]


def test_enroll_time_conflict(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    client.post("/api/enrollment/enroll", json={"course_number": "CMPUT101"}, headers=headers)
    resp = client.post("/api/enrollment/enroll", json={"course_number": "CMPUT201"}, headers=headers)
    assert resp.status_code == 409
    assert "conflict" in resp.get_json()["error"].lower()


def test_enroll_no_seats(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    resp = client.post("/api/enrollment/enroll", json={"course_number": "PHYS100"}, headers=headers)
    assert resp.status_code == 409
    assert "seats" in resp.get_json()["error"].lower()


def test_drop_success(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    client.post("/api/enrollment/enroll", json={"course_number": "CMPUT101"}, headers=headers)
    resp = client.post("/api/enrollment/drop", json={"course_number": "CMPUT101"}, headers=headers)
    assert resp.status_code == 200


def test_drop_not_enrolled(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    resp = client.post("/api/enrollment/drop", json={"course_number": "CMPUT101"}, headers=headers)
    assert resp.status_code == 404


def test_list_enrollments(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    client.post("/api/enrollment/enroll", json={"course_number": "CMPUT101"}, headers=headers)
    client.post("/api/enrollment/enroll", json={"course_number": "MATH101"}, headers=headers)
    resp = client.get("/api/enrollment/STU001", headers=headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2
