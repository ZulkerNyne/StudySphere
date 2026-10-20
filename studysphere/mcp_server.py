"""MCP server exposing Study Sphere tools to any MCP-compatible LLM client."""
from mcp.server.mcpserver import MCPServer

from studysphere.app import create_app
from studysphere.services.mcp_tools import (
    tool_search_courses,
    tool_check_time_conflict,
    tool_enroll_student,
    tool_drop_course,
    tool_get_schedule,
    tool_get_academic_info,
)

mcp = MCPServer("StudySphere", instructions="Course enrollment system with AI advisor. Use these tools to search courses, manage enrollments, and view schedules.")

_app = create_app()


def _ctx(fn):
    def wrapper(*args, **kwargs):
        with _app.app_context():
            return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


@mcp.tool()
@_ctx
def search_courses(query: str, semester: str = "", level: str = "") -> str:
    """Search the course catalog by keyword. Matches course number, name, and professor.

    Args:
        query: Search keyword (course name, number, or professor)
        semester: Optional filter - 'Fall' or 'Winter'
        level: Optional filter - 'Undergraduate' or 'Graduate'
    """
    return tool_search_courses(query, semester, level)


@mcp.tool()
@_ctx
def check_time_conflict(student_id: str, course_number: str) -> str:
    """Check if enrolling in a course would conflict with the student's current schedule.

    Args:
        student_id: The student's ID
        course_number: The course to check
    """
    return tool_check_time_conflict(student_id, course_number)


@mcp.tool()
@_ctx
def enroll_student(student_id: str, course_number: str) -> str:
    """Enroll a student in a course. Checks time conflicts and seat availability automatically.

    Args:
        student_id: The student's ID
        course_number: The course to enroll in
    """
    return tool_enroll_student(student_id, course_number)


@mcp.tool()
@_ctx
def drop_course(student_id: str, course_number: str) -> str:
    """Drop a course the student is currently enrolled in.

    Args:
        student_id: The student's ID
        course_number: The course to drop
    """
    return tool_drop_course(student_id, course_number)


@mcp.tool()
@_ctx
def get_schedule(student_id: str) -> str:
    """Get a student's current class schedule with all active enrollments.

    Args:
        student_id: The student's ID
    """
    return tool_get_schedule(student_id)


@mcp.tool()
@_ctx
def get_academic_info(student_id: str) -> str:
    """Get a student's academic information: program, status, and enrolled credits.

    Args:
        student_id: The student's ID
    """
    return tool_get_academic_info(student_id)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
