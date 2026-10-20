"""Core tool implementations used by both the MCP server and tests."""
import json
from studysphere.app import db
from studysphere.models import Course, Student, Enrollment
from studysphere.services.enrollment_service import (
    check_time_conflict as _check_conflict,
    enroll_student as _enroll,
    drop_course as _drop,
)


def tool_search_courses(query, semester="", level=""):
    results = []
    try:
        from studysphere.services.embedding_service import semantic_search
        courses = semantic_search(query, n_results=10, semester=semester or None, level=level or None)
        results = courses
    except Exception:
        pass

    if not results:
        filters = []
        if query:
            pattern = f"%{query}%"
            filters.append(
                (Course.course_number.ilike(pattern))
                | (Course.course_name.ilike(pattern))
                | (Course.professor_name.ilike(pattern))
            )
        if semester:
            filters.append(Course.semester == semester)
        if level:
            filters.append(Course.level == level)
        results = Course.query.filter(*filters).limit(10).all()

    return json.dumps([
        {
            "course_number": c.course_number,
            "course_name": c.course_name,
            "professor_name": c.professor_name,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "days": c.days,
            "level": c.level,
            "credits": c.credits,
            "available_seats": c.available_seats,
            "semester": c.semester,
        }
        for c in results
    ], indent=2)


def tool_check_time_conflict(student_id, course_number):
    has_conflict, conflict_course = _check_conflict(student_id, course_number)
    if has_conflict:
        return json.dumps({"conflict": True, "conflicting_course": conflict_course})
    return json.dumps({"conflict": False})


def tool_enroll_student(student_id, course_number):
    success, message = _enroll(student_id, course_number)
    return json.dumps({"success": success, "message": message})


def tool_drop_course(student_id, course_number):
    success, message = _drop(student_id, course_number)
    return json.dumps({"success": success, "message": message})


def tool_get_schedule(student_id):
    enrollments = Enrollment.query.filter_by(
        student_id=student_id, status="active"
    ).all()

    schedule = []
    for e in enrollments:
        c = e.course
        schedule.append({
            "course_number": c.course_number,
            "course_name": c.course_name,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "days": c.days,
            "credits": c.credits,
        })
    return json.dumps(schedule, indent=2)


def tool_get_academic_info(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        return json.dumps({"error": "Student not found"})

    active_enrollments = Enrollment.query.filter_by(
        student_id=student_id, status="active"
    ).all()

    total_credits = sum(e.course.credits for e in active_enrollments)

    return json.dumps({
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "program": student.program,
        "degree_status": student.degree_status,
        "status": student.status,
        "enrolled_courses": len(active_enrollments),
        "total_credits": total_credits,
    }, indent=2)
