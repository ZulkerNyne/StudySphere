from flask import Blueprint, request, jsonify
from studysphere.app import db
from studysphere.models import Review, Course, Enrollment
from studysphere.services.auth_service import login_required

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")


@reviews_bp.route("/<course_number>", methods=["GET"])
@login_required
def get_reviews(course_number):
    course = db.session.get(Course, course_number)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    reviews = Review.query.filter_by(course_number=course_number).order_by(
        Review.created_at.desc()
    ).all()

    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    can_review = Enrollment.query.filter_by(
        student_id=request.student_id,
        course_number=course_number,
    ).first() is not None

    return jsonify({
        "course_number": course_number,
        "average_rating": avg_rating,
        "count": len(reviews),
        "can_review": can_review,
        "reviews": [
            {
                "id": r.id,
                "student_name": r.student.name,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat(),
            }
            for r in reviews
        ],
    })


@reviews_bp.route("/<course_number>", methods=["POST"])
@login_required
def add_review(course_number):
    course = db.session.get(Course, course_number)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    ever_enrolled = Enrollment.query.filter_by(
        student_id=request.student_id,
        course_number=course_number,
    ).first()
    if not ever_enrolled:
        return jsonify({"error": "You must be enrolled (or have been enrolled) to review this course"}), 403

    data = request.get_json()
    if not data or "rating" not in data:
        return jsonify({"error": "rating required"}), 400

    rating = data["rating"]
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be 1-5"}), 400

    existing = Review.query.filter_by(
        student_id=request.student_id, course_number=course_number
    ).first()
    if existing:
        existing.rating = rating
        existing.comment = data.get("comment", "")
        db.session.commit()
        return jsonify({"message": "Review updated"})

    review = Review(
        student_id=request.student_id,
        course_number=course_number,
        rating=rating,
        comment=data.get("comment", ""),
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({"message": "Review added"}), 201


@reviews_bp.route("/<course_number>", methods=["DELETE"])
@login_required
def delete_review(course_number):
    review = Review.query.filter_by(
        student_id=request.student_id, course_number=course_number
    ).first()
    if not review:
        return jsonify({"error": "No review found"}), 404

    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted"})
