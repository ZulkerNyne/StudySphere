from functools import wraps
from flask import Blueprint, request, jsonify
from studysphere.app import db
from studysphere.models import Student, Course, Enrollment, Review, Waitlist
from studysphere.services.auth_service import login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        student = db.session.get(Student, request.student_id)
        if not student or not student.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    total_students = Student.query.count()
    total_courses = Course.query.count()
    active_enrollments = Enrollment.query.filter_by(status="active").count()
    total_waitlisted = Waitlist.query.count()
    total_reviews = Review.query.count()

    undergrad = Student.query.filter_by(degree_status="Undergraduate").count()
    grad = Student.query.filter_by(degree_status="Graduate").count()
    fulltime = Student.query.filter_by(status="Full-time").count()
    parttime = Student.query.filter_by(status="Part-time").count()

    top_courses = (
        db.session.query(
            Course.course_number,
            Course.course_name,
            db.func.count(Enrollment.id).label("enrollment_count"),
        )
        .join(Enrollment, Course.course_number == Enrollment.course_number)
        .filter(Enrollment.status == "active")
        .group_by(Course.course_number, Course.course_name)
        .order_by(db.func.count(Enrollment.id).desc())
        .limit(10)
        .all()
    )

    full_courses = Course.query.filter(Course.available_seats <= 0).count()

    dept_stats = (
        db.session.query(
            db.func.substr(Course.course_number, 1, 4).label("dept"),
            db.func.count(Course.course_number).label("count"),
        )
        .group_by("dept")
        .all()
    )

    return jsonify({
        "total_students": total_students,
        "total_courses": total_courses,
        "active_enrollments": active_enrollments,
        "total_waitlisted": total_waitlisted,
        "total_reviews": total_reviews,
        "full_courses": full_courses,
        "students_by_degree": {"Undergraduate": undergrad, "Graduate": grad},
        "students_by_status": {"Full-time": fulltime, "Part-time": parttime},
        "top_courses": [
            {"course_number": c[0], "course_name": c[1], "enrollments": c[2]}
            for c in top_courses
        ],
        "departments": [
            {"name": d[0].strip(), "courses": d[1]} for d in dept_stats
        ],
    })


@admin_bp.route("/students", methods=["GET"])
@admin_required
def list_students():
    students = Student.query.all()
    result = []
    for s in students:
        active = Enrollment.query.filter_by(student_id=s.student_id, status="active").count()
        result.append({
            "student_id": s.student_id,
            "name": s.name,
            "email": s.email,
            "program": s.program,
            "degree_status": s.degree_status,
            "status": s.status,
            "is_admin": s.is_admin,
            "enrolled_count": active,
        })
    return jsonify(result)


@admin_bp.route("/students/<student_id>/toggle-admin", methods=["POST"])
@admin_required
def toggle_admin(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    if student.student_id == request.student_id:
        return jsonify({"error": "Cannot change your own admin status"}), 400

    student.is_admin = not student.is_admin
    db.session.commit()
    return jsonify({
        "message": f"{'Granted' if student.is_admin else 'Revoked'} admin for {student.name}",
        "is_admin": student.is_admin,
    })


@admin_bp.route("/courses", methods=["GET"])
@admin_required
def list_courses():
    courses = Course.query.order_by(Course.course_number).all()
    result = []
    for c in courses:
        active = Enrollment.query.filter_by(course_number=c.course_number, status="active").count()
        waitlisted = Waitlist.query.filter_by(course_number=c.course_number).count()
        reviews = Review.query.filter_by(course_number=c.course_number).all()
        avg = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
        result.append({
            "course_number": c.course_number,
            "course_name": c.course_name,
            "professor_name": c.professor_name,
            "level": c.level,
            "semester": c.semester,
            "total_seats": c.total_seats,
            "available_seats": c.available_seats,
            "enrolled": active,
            "waitlisted": waitlisted,
            "avg_rating": avg,
        })
    return jsonify(result)


@admin_bp.route("/courses/<course_number>/update", methods=["PUT"])
@admin_required
def update_course(course_number):
    course = db.session.get(Course, course_number)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json()
    for field in ["professor_name", "total_seats", "available_seats", "start_time", "end_time", "days"]:
        if field in data:
            setattr(course, field, data[field])

    db.session.commit()
    return jsonify({"message": f"Course {course_number} updated"})


@admin_bp.route("/enrollments", methods=["GET"])
@admin_required
def all_enrollments():
    enrollments = Enrollment.query.filter_by(status="active").all()
    return jsonify([
        {
            "student_id": e.student_id,
            "student_name": e.student.name,
            "course_number": e.course_number,
            "course_name": e.course.course_name,
            "enrolled_at": e.enrolled_at.isoformat(),
        }
        for e in enrollments
    ])
