from flask import Blueprint, request, jsonify
from studysphere.app import db
from studysphere.models import Student, Enrollment
from studysphere.services.auth_service import (
    hash_password,
    verify_password,
    create_token,
    create_refresh_token,
    decode_token,
    login_required,
)
from jose import JWTError

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    required = ["student_id", "name", "email", "password", "program", "degree_status", "status"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    if db.session.get(Student, data["student_id"]):
        return jsonify({"error": "Student ID already exists"}), 409

    if Student.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    student = Student(
        student_id=data["student_id"],
        name=data["name"],
        email=data["email"],
        program=data["program"],
        degree_status=data["degree_status"],
        status=data["status"],
        password_hash=hash_password(data["password"]),
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Registered successfully", "student_id": student.student_id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "student_id" not in data or "password" not in data:
        return jsonify({"error": "student_id and password required"}), 400

    student = db.session.get(Student, data["student_id"])
    if not student or not verify_password(data["password"], student.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "access_token": create_token(student.student_id),
        "refresh_token": create_refresh_token(student.student_id),
        "student_id": student.student_id,
        "is_admin": student.is_admin,
    })


@auth_bp.route("/profile", methods=["GET"])
@login_required
def profile():
    student = db.session.get(Student, request.student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    active_count = Enrollment.query.filter_by(
        student_id=student.student_id, status="active"
    ).count()

    return jsonify({
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "program": student.program,
        "degree_status": student.degree_status,
        "status": student.status,
        "max_courses": student.max_courses,
        "enrolled_count": active_count,
        "fee_per_credit": student.fee_per_credit,
        "is_admin": student.is_admin,
    })


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json()
    if not data or "refresh_token" not in data:
        return jsonify({"error": "refresh_token required"}), 400

    try:
        payload = decode_token(data["refresh_token"])
        return jsonify({
            "access_token": create_token(payload["sub"]),
        })
    except JWTError:
        return jsonify({"error": "Invalid or expired refresh token"}), 401
