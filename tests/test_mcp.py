import json
from studysphere.models import Course, Student
from studysphere.services.auth_service import hash_password
from studysphere.services.mcp_tools import (
    tool_search_courses,
    tool_check_time_conflict,
    tool_enroll_student,
    tool_drop_course,
    tool_get_schedule,
    tool_get_academic_info,
)


def seed_data(db):
    student = Student(
        student_id="STU001",
        name="Test Student",
        email="test@example.com",
        program="Computer Science",
        degree_status="Undergraduate",
        status="Full-time",
        password_hash=hash_password("pass123"),
    )
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
            course_number="MATH201",
            course_name="Linear Algebra",
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
    db.session.add(student)
    for c in courses:
        db.session.add(c)
    db.session.commit()


def test_mcp_search_courses(app, db):
    with app.app_context():
        seed_data(db)
        result = json.loads(tool_search_courses("computing"))
        assert len(result) == 1
        assert result[0]["course_number"] == "CMPUT101"


def test_mcp_check_no_conflict(app, db):
    with app.app_context():
        seed_data(db)
        result = json.loads(tool_check_time_conflict("STU001", "CMPUT101"))
        assert result["conflict"] is False


def test_mcp_enroll_and_schedule(app, db):
    with app.app_context():
        seed_data(db)
        result = json.loads(tool_enroll_student("STU001", "CMPUT101"))
        assert result["success"] is True

        schedule = json.loads(tool_get_schedule("STU001"))
        assert len(schedule) == 1
        assert schedule[0]["course_number"] == "CMPUT101"


def test_mcp_drop_course(app, db):
    with app.app_context():
        seed_data(db)
        tool_enroll_student("STU001", "CMPUT101")
        result = json.loads(tool_drop_course("STU001", "CMPUT101"))
        assert result["success"] is True


def test_mcp_academic_info(app, db):
    with app.app_context():
        seed_data(db)
        tool_enroll_student("STU001", "CMPUT101")
        tool_enroll_student("STU001", "MATH201")

        info = json.loads(tool_get_academic_info("STU001"))
        assert info["name"] == "Test Student"
        assert info["enrolled_courses"] == 2
        assert info["total_credits"] == 7


def test_mcp_academic_info_not_found(app, db):
    with app.app_context():
        seed_data(db)
        info = json.loads(tool_get_academic_info("FAKE999"))
        assert "error" in info
