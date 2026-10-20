from datetime import datetime, timezone
from studysphere.app import db
from studysphere.models import Course, Enrollment, Student


def parse_time_to_minutes(time_str):
    """Convert '09:30 AM' to minutes past midnight."""
    from datetime import datetime as dt
    t = dt.strptime(time_str.strip(), "%I:%M %p")
    return t.hour * 60 + t.minute


def times_overlap(start1, end1, start2, end2):
    return start1 < end2 and start2 < end1


def check_time_conflict(student_id, course_number, exclude_course=None):
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
        if exclude_course and enrollment.course_number == exclude_course:
            continue
        existing = enrollment.course
        existing_days = set(d.strip() for d in existing.days.split(","))

        if not new_days.intersection(existing_days):
            continue

        ex_start = parse_time_to_minutes(existing.start_time)
        ex_end = parse_time_to_minutes(existing.end_time)

        if times_overlap(new_start, new_end, ex_start, ex_end):
            return True, existing.course_number

    return False, None


def active_enrollment_count(student_id):
    return Enrollment.query.filter_by(student_id=student_id, status="active").count()


def enroll_student(student_id, course_number):
    student = db.session.get(Student, student_id)
    if not student:
        return False, "Student not found"

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

    if student.degree_status == "Undergraduate" and course.level == "Graduate":
        return False, "Undergraduates cannot enroll in graduate courses"
    if student.degree_status == "Graduate" and course.level == "Undergraduate":
        return False, "Graduates cannot enroll in undergraduate courses"

    count = active_enrollment_count(student_id)
    if count >= student.max_courses:
        return False, f"Maximum {student.max_courses} courses allowed for {student.status} students"

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


def swap_course(student_id, drop_number, enroll_number):
    """Atomically drop one course and enroll in another."""
    student = db.session.get(Student, student_id)
    if not student:
        return False, "Student not found"

    drop_enrollment = Enrollment.query.filter_by(
        student_id=student_id, course_number=drop_number, status="active"
    ).first()
    if not drop_enrollment:
        return False, f"Not enrolled in {drop_number}"

    new_course = db.session.get(Course, enroll_number)
    if not new_course:
        return False, f"Course {enroll_number} not found"

    if new_course.available_seats <= 0:
        return False, f"No seats available in {enroll_number}"

    if student.degree_status == "Undergraduate" and new_course.level == "Graduate":
        return False, "Undergraduates cannot enroll in graduate courses"
    if student.degree_status == "Graduate" and new_course.level == "Undergraduate":
        return False, "Graduates cannot enroll in undergraduate courses"

    existing = Enrollment.query.filter_by(
        student_id=student_id, course_number=enroll_number, status="active"
    ).first()
    if existing:
        return False, f"Already enrolled in {enroll_number}"

    has_conflict, conflict = check_time_conflict(student_id, enroll_number, exclude_course=drop_number)
    if has_conflict:
        return False, f"Time conflict with {conflict}"

    drop_enrollment.status = "dropped"
    drop_enrollment.dropped_at = datetime.now(timezone.utc)
    drop_enrollment.course.available_seats += 1

    enrollment = Enrollment(student_id=student_id, course_number=enroll_number)
    new_course.available_seats -= 1
    db.session.add(enrollment)
    db.session.commit()

    return True, f"Swapped {drop_number} for {enroll_number}"


def calculate_fees(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        return None

    active = Enrollment.query.filter_by(student_id=student_id, status="active").all()

    total_credits = 0
    course_fees = []
    for e in active:
        c = e.course
        fee = c.credits * student.fee_per_credit
        total_credits += c.credits
        course_fees.append({
            "course_number": c.course_number,
            "course_name": c.course_name,
            "credits": c.credits,
            "fee": fee,
        })

    return {
        "status": student.status,
        "degree_status": student.degree_status,
        "fee_per_credit": student.fee_per_credit,
        "total_credits": total_credits,
        "total_fee": total_credits * student.fee_per_credit,
        "courses": course_fees,
    }
