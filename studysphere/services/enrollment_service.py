from datetime import datetime, timezone
from studysphere.app import db
from studysphere.models import Course, Enrollment


def parse_time_to_minutes(time_str):
    """Convert '09:30 AM' to minutes past midnight."""
    from datetime import datetime as dt
    t = dt.strptime(time_str.strip(), "%I:%M %p")
    return t.hour * 60 + t.minute


def times_overlap(start1, end1, start2, end2):
    return start1 < end2 and start2 < end1


def check_time_conflict(student_id, course_number):
    new_course = db.session.get(Course, course_number)
    if not new_course:
        return False, None

    new_start = parse_time_to_minutes(new_course.start_time)
    new_end = parse_time_to_minutes(new_course.end_time)
    new_days = set(d.strip() for d in new_course.days.split(","))

    active = (
        Enrollment.query
        .filter_by(student_id=student_id, status="active")
        .all()
    )

    for enrollment in active:
        existing = enrollment.course
        existing_days = set(d.strip() for d in existing.days.split(","))

        if not new_days.intersection(existing_days):
            continue

        ex_start = parse_time_to_minutes(existing.start_time)
        ex_end = parse_time_to_minutes(existing.end_time)

        if times_overlap(new_start, new_end, ex_start, ex_end):
            return True, existing.course_number

    return False, None


def enroll_student(student_id, course_number):
    course = db.session.get(Course, course_number)
    if not course:
        return False, "Course not found"

    if course.available_seats <= 0:
        return False, "No seats available"

    existing = Enrollment.query.filter_by(
        student_id=student_id, course_number=course_number, status="active"
    ).first()
    if existing:
        return False, "Already enrolled in this course"

    has_conflict, conflict_course = check_time_conflict(student_id, course_number)
    if has_conflict:
        return False, f"Time conflict with {conflict_course}"

    enrollment = Enrollment(student_id=student_id, course_number=course_number)
    course.available_seats -= 1
    db.session.add(enrollment)
    db.session.commit()

    return True, "Enrolled successfully"


def drop_course(student_id, course_number):
    enrollment = Enrollment.query.filter_by(
        student_id=student_id, course_number=course_number, status="active"
    ).first()
    if not enrollment:
        return False, "No active enrollment found"

    enrollment.status = "dropped"
    enrollment.dropped_at = datetime.now(timezone.utc)
    enrollment.course.available_seats += 1
    db.session.commit()

    return True, "Course dropped successfully"
