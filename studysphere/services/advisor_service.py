import json
from anthropic import Anthropic
from flask import current_app
from studysphere.app import db
from studysphere.models import Course, Student, Enrollment
from studysphere.services.enrollment_service import (
    check_time_conflict,
    enroll_student,
    drop_course,
)

TOOLS = [
    {
        "name": "search_courses",
        "description": "Search the course catalog by keyword. Matches against course number, name, and professor. Optionally filter by semester and level.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword (course name, number, or professor)",
                },
                "semester": {
                    "type": "string",
                    "enum": ["Fall", "Winter"],
                    "description": "Filter by semester",
                },
                "level": {
                    "type": "string",
                    "enum": ["Undergraduate", "Graduate"],
                    "description": "Filter by course level",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "check_time_conflict",
        "description": "Check if enrolling in a course would conflict with the student's current schedule.",
        "input_schema": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "The student's ID",
                },
                "course_number": {
                    "type": "string",
                    "description": "The course to check",
                },
            },
            "required": ["student_id", "course_number"],
        },
    },
    {
        "name": "enroll_student",
        "description": "Enroll the student in a course. Checks for time conflicts, seat availability, and duplicate enrollment automatically.",
        "input_schema": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "The student's ID",
                },
                "course_number": {
                    "type": "string",
                    "description": "The course to enroll in",
                },
            },
            "required": ["student_id", "course_number"],
        },
    },
    {
        "name": "drop_course",
        "description": "Drop a course the student is currently enrolled in.",
        "input_schema": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "The student's ID",
                },
                "course_number": {
                    "type": "string",
                    "description": "The course to drop",
                },
            },
            "required": ["student_id", "course_number"],
        },
    },
    {
        "name": "get_schedule",
        "description": "Get the student's current class schedule, listing all active enrollments with times and days.",
        "input_schema": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "The student's ID",
                },
            },
            "required": ["student_id"],
        },
    },
]

SYSTEM_PROMPT = """You are Study Sphere's AI course advisor. You help students find courses, check schedule conflicts, enroll in classes, and manage their schedule.

Guidelines:
- Always search for courses before recommending them.
- Always check for time conflicts before enrolling a student.
- Explain WHY a course might be a good fit, not just list results.
- Respect degree level restrictions: don't suggest graduate courses to undergrads unless they ask.
- Always confirm with the student before enrolling or dropping a course.
- When a course is full or conflicts, suggest alternatives.
- Be concise and helpful. Use the student's name when you know it.

You have access to these tools: search_courses, check_time_conflict, enroll_student, drop_course, get_schedule.
The student's ID is provided in each conversation. Use it when calling tools."""


def execute_tool(tool_name, tool_input):
    if tool_name == "search_courses":
        return _search_courses(tool_input)
    elif tool_name == "check_time_conflict":
        return _check_time_conflict(tool_input)
    elif tool_name == "enroll_student":
        return _enroll_student(tool_input)
    elif tool_name == "drop_course":
        return _drop_course(tool_input)
    elif tool_name == "get_schedule":
        return _get_schedule(tool_input)
    return {"error": f"Unknown tool: {tool_name}"}


def _search_courses(params):
    query = params.get("query", "")
    semester = params.get("semester")
    level = params.get("level")

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

    courses = Course.query.filter(*filters).limit(10).all()
    return [
        {
            "course_number": c.course_number,
            "course_name": c.course_name,
            "professor_name": c.professor_name,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "days": c.days,
            "level": c.level,
            "credits": c.credits,
            "available_seats": c.available_seats,
            "semester": c.semester,
        }
        for c in courses
    ]


def _check_time_conflict(params):
    has_conflict, conflict_course = check_time_conflict(
        params["student_id"], params["course_number"]
    )
    if has_conflict:
        return {"conflict": True, "conflicting_course": conflict_course}
    return {"conflict": False}


def _enroll_student(params):
    success, message = enroll_student(params["student_id"], params["course_number"])
    return {"success": success, "message": message}


def _drop_course(params):
    success, message = drop_course(params["student_id"], params["course_number"])
    return {"success": success, "message": message}


def _get_schedule(params):
    enrollments = Enrollment.query.filter_by(
        student_id=params["student_id"], status="active"
    ).all()

    schedule = []
    for e in enrollments:
        c = e.course
        schedule.append({
            "course_number": c.course_number,
            "course_name": c.course_name,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "days": c.days,
            "credits": c.credits,
        })
    return schedule


def chat_with_advisor(student_id, messages):
    api_key = current_app.config.get("CLAUDE_API_KEY")
    if not api_key:
        return {"error": "Claude API key not configured"}, []

    student = db.session.get(Student, student_id)
    student_context = ""
    if student:
        student_context = f"\n\nCurrent student: {student.name} (ID: {student_id}, Program: {student.program}, Level: {student.degree_status})"

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT + student_context,
        tools=TOOLS,
        messages=messages,
    )

    while response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        messages = messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results},
        ]

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT + student_context,
            tools=TOOLS,
            messages=messages,
        )

    assistant_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            assistant_text += block.text

    return assistant_text, messages + [{"role": "assistant", "content": response.content}]
