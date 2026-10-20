from studysphere.models import Course


def setup_auth(client, db):
    """Register and login, return auth header."""
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
            course_number="CMPUT401",
            course_name="Software Engineering",
            professor_name="Dr. Jones",
            start_time="01:00 PM",
            end_time="02:30 PM",
            level="Undergraduate",
            credits=3,
            total_seats=30,
            available_seats=0,
            semester="Fall",
            days="Tuesday, Thursday",
        ),
        Course(
            course_number="MATH201",
            course_name="Linear Algebra",
            professor_name="Dr. Lee",
            start_time="11:00 AM",
            end_time="12:30 PM",
            level="Graduate",
            credits=4,
            total_seats=25,
            available_seats=5,
            semester="Winter",
            days="Monday, Wednesday, Friday",
        ),
    ]
    for c in courses:
        db.session.add(c)
    db.session.commit()
    return courses


def test_search_no_auth(client, db):
    resp = client.get("/api/courses")
    assert resp.status_code == 401


def test_search_all(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    resp = client.get("/api/courses", headers=headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 3


def test_search_by_query(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    resp = client.get("/api/courses?q=Software", headers=headers)
    assert resp.status_code == 200
    results = resp.get_json()
    assert len(results) == 1
    assert results[0]["course_number"] == "CMPUT401"


def test_search_by_semester(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    resp = client.get("/api/courses?semester=Winter", headers=headers)
    results = resp.get_json()
    assert len(results) == 1
    assert results[0]["course_number"] == "MATH201"


def test_get_course_detail(client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    resp = client.get("/api/courses/CMPUT101", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["course_name"] == "Intro to Computing"


def test_get_course_not_found(client, db):
    headers = setup_auth(client, db)
    resp = client.get("/api/courses/FAKE999", headers=headers)
    assert resp.status_code == 404
