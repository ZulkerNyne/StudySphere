from datetime import datetime, timezone
from studysphere.app import db
from studysphere.models import Course, Enrollment, Student, Waitlist, Prerequisite


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


def check_prerequisites(student_id, course_number):
    prereqs = Prerequisite.query.filter_by(course_number=course_number).all()
    if not prereqs:
        return True, []

    completed = set()
    past = Enrollment.query.filter(
        Enrollment.student_id == student_id,
        Enrollment.status.in_(["active", "dropped"]),
    ).all()
    for e in past:
        completed.add(e.course_number)

    missing = []
    for p in prereqs:
        if p.prerequisite_number not in completed:
            missing.append(p.prerequisite_number)

    return len(missing) == 0, missing


def enroll_student(student_id, course_number):
    student = db.session.get(Student, student_id)
    if not student:
        return False, "Student not found"

    course = db.session.get(Course, course_number)
    if not course:
        return False, "Course not found"

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

    prereq_ok, missing = check_prerequisites(student_id, course_number)
    if not prereq_ok:
        return False, f"Missing prerequisites: {', '.join(missing)}"

    has_conflict, conflict_course = check_time_conflict(student_id, course_number)
    if has_conflict:
        return False, f"Time conflict with {conflict_course}"

    if course.available_seats <= 0:
        return False, "No seats available. Use waitlist to be notified when a seat opens."

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

    promote_from_waitlist(course_number)

    return True, "Course dropped successfully"


def promote_from_waitlist(course_number):
    """Auto-enroll the next waitlisted student when a seat opens."""
    course = db.session.get(Course, course_number)
    if not course or course.available_seats <= 0:
        return

    next_entry = (
        Waitlist.query
        .filter_by(course_number=course_number)
        .order_by(Waitlist.position)
        .first()
    )
    if not next_entry:
        return

    student = db.session.get(Student, next_entry.student_id)
    count = active_enrollment_count(next_entry.student_id)
    if count >= student.max_courses:
        db.session.delete(next_entry)
        reorder_waitlist(course_number)
        db.session.commit()
        return

    has_conflict, _ = check_time_conflict(next_entry.student_id, course_number)
    if has_conflict:
        db.session.delete(next_entry)
        reorder_waitlist(course_number)
        db.session.commit()
        return

    enrollment = Enrollment(student_id=next_entry.student_id, course_number=course_number)
    course.available_seats -= 1
    db.session.add(enrollment)
    db.session.delete(next_entry)
    reorder_waitlist(course_number)
    db.session.commit()


def join_waitlist(student_id, course_number):
    student = db.session.get(Student, student_id)
    if not student:
        return False, "Student not found"

    course = db.session.get(Course, course_number)
    if not course:
        return False, "Course not found"

    if course.available_seats > 0:
        return False, "Course has seats available. Enroll directly instead."

    existing_enroll = Enrollment.query.filter_by(
        student_id=student_id, course_number=course_number, status="active"
    ).first()
    if existing_enroll:
        return False, "Already enrolled in this course"

    existing_wait = Waitlist.query.filter_by(
        student_id=student_id, course_number=course_number
    ).first()
    if existing_wait:
        return False, f"Already on waitlist at position {existing_wait.position}"

    max_pos = db.session.query(db.func.max(Waitlist.position)).filter_by(
        course_number=course_number
    ).scalar() or 0

    entry = Waitlist(
        student_id=student_id,
        course_number=course_number,
        position=max_pos + 1,
    )
    db.session.add(entry)
    db.session.commit()

    return True, f"Added to waitlist at position {entry.position}"


def leave_waitlist(student_id, course_number):
    entry = Waitlist.query.filter_by(
        student_id=student_id, course_number=course_number
    ).first()
    if not entry:
        return False, "Not on the waitlist for this course"

    db.session.delete(entry)
    reorder_waitlist(course_number)
    db.session.commit()

    return True, "Removed from waitlist"


def reorder_waitlist(course_number):
    entries = (
        Waitlist.query
        .filter_by(course_number=course_number)
        .order_by(Waitlist.position)
        .all()
    )
    for i, entry in enumerate(entries, 1):
        entry.position = i


def get_waitlist_status(student_id, course_number):
    entry = Waitlist.query.filter_by(
        student_id=student_id, course_number=course_number
    ).first()
    if not entry:
        return None
    total = Waitlist.query.filter_by(course_number=course_number).count()
    return {"position": entry.position, "total": total}


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

    prereq_ok, missing = check_prerequisites(student_id, enroll_number)
    if not prereq_ok:
        return False, f"Missing prerequisites: {', '.join(missing)}"

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

    promote_from_waitlist(drop_number)

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
