from flask import Blueprint, request, jsonify
from studysphere.app import db
from studysphere.models import Course, Prerequisite, Review, Waitlist
from studysphere.services.auth_service import login_required

courses_bp = Blueprint("courses", __name__, url_prefix="/api/courses")


def course_to_dict(c):
    reviews = Review.query.filter_by(course_number=c.course_number).all()
    avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
    waitlist_count = Waitlist.query.filter_by(course_number=c.course_number).count()

    prereqs = Prerequisite.query.filter_by(course_number=c.course_number).all()
    prereq_list = [p.prerequisite_number for p in prereqs]

    return {
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
        "avg_rating": avg_rating,
        "review_count": len(reviews),
        "waitlist_count": waitlist_count,
        "prerequisites": prereq_list,
    }


@courses_bp.route("", methods=["GET"])
@login_required
def search_courses():
    query = request.args.get("q", "")
    semester = request.args.get("semester")
    level = request.args.get("level")
    mode = request.args.get("mode", "keyword")

    courses = []
    if mode == "semantic" and query:
        try:
            from studysphere.services.embedding_service import semantic_search
            courses = semantic_search(query, n_results=50, semester=semester, level=level)
        except Exception:
            pass

    if not courses:
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

    return jsonify([course_to_dict(c) for c in courses])


@courses_bp.route("/<course_number>", methods=["GET"])
@login_required
def get_course(course_number):
    course = db.session.get(Course, course_number)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    data = course_to_dict(course)
    data["description"] = course.description
    return jsonify(data)


@courses_bp.route("/ingest", methods=["POST"])
@login_required
def ingest():
    from studysphere.services.embedding_service import ingest_courses
    count = ingest_courses()
    return jsonify({"message": f"Ingested {count} courses into ChromaDB"})
