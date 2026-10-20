from flask import Blueprint, jsonify
from studysphere.models import Enrollment
from studysphere.services.auth_service import login_required

schedule_bp = Blueprint("schedule", __name__, url_prefix="/api/schedule")


@schedule_bp.route("/<student_id>", methods=["GET"])
@login_required
def get_schedule(student_id):
    enrollments = Enrollment.query.filter_by(
        student_id=student_id, status="active"
    ).all()

    schedule = {}
    for e in enrollments:
        course = e.course
        days = [d.strip() for d in course.days.split(",")]
        for day in days:
            if day not in schedule:
                schedule[day] = []
            schedule[day].append({
                "course_number": course.course_number,
                "course_name": course.course_name,
                "start_time": course.start_time,
                "end_time": course.end_time,
            })

    for day in schedule:
        schedule[day].sort(key=lambda x: x["start_time"])

    return jsonify(schedule)
