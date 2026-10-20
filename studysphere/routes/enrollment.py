from flask import Blueprint, request, jsonify
from studysphere.services.auth_service import login_required
from studysphere.services.enrollment_service import (
    enroll_student,
    drop_course,
    swap_course,
    calculate_fees,
    join_waitlist,
    leave_waitlist,
    get_waitlist_status,
)
from studysphere.models import Enrollment, Waitlist
from studysphere.app import db

enrollment_bp = Blueprint("enrollment", __name__, url_prefix="/api/enrollment")


@enrollment_bp.route("/enroll", methods=["POST"])
@login_required
def enroll():
    data = request.get_json()
    if not data or "course_number" not in data:
        return jsonify({"error": "course_number required"}), 400

    success, message = enroll_student(request.student_id, data["course_number"])
    if not success:
        return jsonify({"error": message}), 409

    return jsonify({"message": message}), 201


@enrollment_bp.route("/drop", methods=["POST"])
@login_required
def drop():
    data = request.get_json()
    if not data or "course_number" not in data:
        return jsonify({"error": "course_number required"}), 400

    success, message = drop_course(request.student_id, data["course_number"])
    if not success:
        return jsonify({"error": message}), 404

    return jsonify({"message": message})


@enrollment_bp.route("/swap", methods=["POST"])
@login_required
def swap():
    data = request.get_json()
    if not data or "drop_course" not in data or "enroll_course" not in data:
        return jsonify({"error": "drop_course and enroll_course required"}), 400

    success, message = swap_course(
        request.student_id, data["drop_course"], data["enroll_course"]
    )
    if not success:
        return jsonify({"error": message}), 409

    return jsonify({"message": message})


@enrollment_bp.route("/fees", methods=["GET"])
@login_required
def fees():
    result = calculate_fees(request.student_id)
    if not result:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(result)


@enrollment_bp.route("/waitlist/join", methods=["POST"])
@login_required
def waitlist_join():
    data = request.get_json()
    if not data or "course_number" not in data:
        return jsonify({"error": "course_number required"}), 400

    success, message = join_waitlist(request.student_id, data["course_number"])
    if not success:
        return jsonify({"error": message}), 409
    return jsonify({"message": message}), 201


@enrollment_bp.route("/waitlist/leave", methods=["POST"])
@login_required
def waitlist_leave():
    data = request.get_json()
    if not data or "course_number" not in data:
        return jsonify({"error": "course_number required"}), 400

    success, message = leave_waitlist(request.student_id, data["course_number"])
    if not success:
        return jsonify({"error": message}), 404
    return jsonify({"message": message})


@enrollment_bp.route("/waitlist/status/<course_number>", methods=["GET"])
@login_required
def waitlist_status(course_number):
    status = get_waitlist_status(request.student_id, course_number)
    if not status:
        return jsonify({"on_waitlist": False})
    return jsonify({"on_waitlist": True, **status})


@enrollment_bp.route("/<student_id>", methods=["GET"])
@login_required
def list_enrollments(student_id):
    enrollments = Enrollment.query.filter_by(
        student_id=student_id, status="active"
    ).all()

    return jsonify([
        {
            "course_number": e.course.course_number,
            "course_name": e.course.course_name,
            "professor_name": e.course.professor_name,
            "start_time": e.course.start_time,
            "end_time": e.course.end_time,
            "days": e.course.days,
            "credits": e.course.credits,
            "enrolled_at": e.enrolled_at.isoformat(),
        }
        for e in enrollments
    ])


@enrollment_bp.route("/history/<student_id>", methods=["GET"])
@login_required
def enrollment_history(student_id):
    dropped = Enrollment.query.filter_by(
        student_id=student_id, status="dropped"
    ).all()

    return jsonify([
        {
            "course_number": e.course.course_number,
            "course_name": e.course.course_name,
            "enrolled_at": e.enrolled_at.isoformat(),
            "dropped_at": e.dropped_at.isoformat() if e.dropped_at else None,
        }
        for e in dropped
    ])
