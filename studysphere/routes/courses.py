from flask import Blueprint, request, jsonify
from studysphere.app import db
from studysphere.models import Course
from studysphere.services.auth_service import login_required

courses_bp = Blueprint("courses", __name__, url_prefix="/api/courses")


@courses_bp.route("", methods=["GET"])
@login_required
def search_courses():
    query = request.args.get("q", "")
    semester = request.args.get("semester")
    level = request.args.get("level")

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

    courses = Course.query.filter(*filters).limit(50).all()

    return jsonify([
        {
            "course_number": c.course_number,
            "course_name": c.course_name,
            "professor_name": c.professor_name,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "level": c.level,
            "credits": c.credits,
            "total_seats": c.total_seats,
            "available_seats": c.available_seats,
            "semester": c.semester,
            "days": c.days,
        }
        for c in courses
    ])


@courses_bp.route("/<course_number>", methods=["GET"])
@login_required
def get_course(course_number):
    course = db.session.get(Course, course_number)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    return jsonify({
        "course_number": course.course_number,
        "course_name": course.course_name,
        "professor_name": course.professor_name,
        "start_time": course.start_time,
        "end_time": course.end_time,
        "level": course.level,
        "credits": course.credits,
        "total_seats": course.total_seats,
        "available_seats": course.available_seats,
        "semester": course.semester,
        "days": course.days,
        "description": course.description,
    })
