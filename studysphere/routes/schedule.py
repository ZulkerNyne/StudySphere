from datetime import datetime, timedelta
from flask import Blueprint, jsonify, Response
from studysphere.models import Enrollment
from studysphere.services.auth_service import login_required

schedule_bp = Blueprint("schedule", __name__, url_prefix="/api/schedule")

DAY_MAP = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2,
    "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6,
}

ICAL_DAY = {
    "Monday": "MO", "Tuesday": "TU", "Wednesday": "WE",
    "Thursday": "TH", "Friday": "FR", "Saturday": "SA", "Sunday": "SU",
}


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


@schedule_bp.route("/<student_id>/export", methods=["GET"])
@login_required
def export_schedule(student_id):
    enrollments = Enrollment.query.filter_by(
        student_id=student_id, status="active"
    ).all()

    if not enrollments:
        return jsonify({"error": "No active enrollments to export"}), 404

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//StudySphere//Course Schedule//EN",
        "CALSCALE:GREGORIAN",
    ]

    today = datetime.now()

    for e in enrollments:
        course = e.course
        days = [d.strip() for d in course.days.split(",")]
        ical_days = ",".join(ICAL_DAY.get(d, "") for d in days if d in ICAL_DAY)

        start_time = datetime.strptime(course.start_time.strip(), "%I:%M %p")
        end_time = datetime.strptime(course.end_time.strip(), "%I:%M %p")

        first_day_name = days[0]
        first_day_num = DAY_MAP.get(first_day_name, 0)
        days_ahead = first_day_num - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        first_date = today + timedelta(days=days_ahead)

        dtstart = first_date.replace(
            hour=start_time.hour, minute=start_time.minute, second=0
        )
        dtend = first_date.replace(
            hour=end_time.hour, minute=end_time.minute, second=0
        )

        semester_end = dtstart + timedelta(weeks=16)

        uid = f"{course.course_number.replace(' ', '-')}@studysphere"

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{dtend.strftime('%Y%m%dT%H%M%S')}",
            f"RRULE:FREQ=WEEKLY;BYDAY={ical_days};UNTIL={semester_end.strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{course.course_number} - {course.course_name}",
            f"DESCRIPTION:Professor: {course.professor_name}\\nCredits: {course.credits}",
            f"LOCATION:University of Calgary",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    ical_content = "\r\n".join(lines)

    return Response(
        ical_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=schedule.ics"},
    )
