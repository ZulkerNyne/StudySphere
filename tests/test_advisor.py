from unittest.mock import patch, MagicMock
from studysphere.models import Course


def setup_auth(client, db):
    client.post("/api/auth/register", json={
        "student_id": "STU001",
        "name": "Test Student",
        "email": "test@example.com",
        "password": "pass123",
        "program": "Computer Science",
        "degree_status": "Undergraduate",
        "status": "Full-time",
    })
    resp = client.post("/api/auth/login", json={
        "student_id": "STU001",
        "password": "pass123",
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def seed_courses(db):
    c = Course(
        course_number="CMPUT101",
        course_name="Intro to Computing",
        professor_name="Dr. Smith",
        start_time="09:00 AM",
        end_time="10:30 AM",
        level="Undergraduate",
        credits=3,
        total_seats=40,
        available_seats=10,
        semester="Fall",
        days="Monday, Wednesday",
    )
    db.session.add(c)
    db.session.commit()


def make_text_response(text):
    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = text
    mock_response.content = [text_block]
    return mock_response


def make_tool_use_response(tool_name, tool_input, tool_id="tool_1"):
    mock_response = MagicMock()
    mock_response.stop_reason = "tool_use"
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = tool_name
    tool_block.input = tool_input
    tool_block.id = tool_id
    mock_response.content = [tool_block]
    return mock_response


def test_advisor_no_api_key(client, db):
    headers = setup_auth(client, db)
    resp = client.post("/api/advisor/chat", json={
        "message": "Hello",
    }, headers=headers)
    assert resp.status_code == 503


def test_advisor_missing_message(client, db):
    headers = setup_auth(client, db)
    resp = client.post("/api/advisor/chat", json={}, headers=headers)
    assert resp.status_code == 400


@patch("studysphere.services.advisor_service.Anthropic")
def test_advisor_simple_response(mock_anthropic_cls, client, db):
    headers = setup_auth(client, db)
    app = client.application
    app.config["CLAUDE_API_KEY"] = "test-key"

    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = make_text_response(
        "Hello! I'm your course advisor. How can I help?"
    )

    resp = client.post("/api/advisor/chat", json={
        "message": "Hello",
    }, headers=headers)

    assert resp.status_code == 200
    data = resp.get_json()
    assert "Hello" in data["response"]
    assert "history" in data


@patch("studysphere.services.advisor_service.Anthropic")
def test_advisor_tool_calling(mock_anthropic_cls, client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    app = client.application
    app.config["CLAUDE_API_KEY"] = "test-key"

    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client

    tool_response = make_tool_use_response(
        "search_courses", {"query": "computing"}
    )
    text_response = make_text_response(
        "I found CMPUT101 Intro to Computing with Dr. Smith."
    )
    mock_client.messages.create.side_effect = [tool_response, text_response]

    resp = client.post("/api/advisor/chat", json={
        "message": "Find me a computing course",
    }, headers=headers)

    assert resp.status_code == 200
    data = resp.get_json()
    assert "CMPUT101" in data["response"]
    assert mock_client.messages.create.call_count == 2


@patch("studysphere.services.advisor_service.Anthropic")
def test_advisor_enroll_tool(mock_anthropic_cls, client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    app = client.application
    app.config["CLAUDE_API_KEY"] = "test-key"

    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client

    tool_response = make_tool_use_response(
        "enroll_student", {"student_id": "STU001", "course_number": "CMPUT101"}
    )
    text_response = make_text_response("You're enrolled in CMPUT101!")
    mock_client.messages.create.side_effect = [tool_response, text_response]

    resp = client.post("/api/advisor/chat", json={
        "message": "Enroll me in CMPUT101",
    }, headers=headers)

    assert resp.status_code == 200
    assert "enrolled" in resp.get_json()["response"].lower()


@patch("studysphere.services.advisor_service.Anthropic")
def test_advisor_get_schedule_tool(mock_anthropic_cls, client, db):
    headers = setup_auth(client, db)
    seed_courses(db)
    app = client.application
    app.config["CLAUDE_API_KEY"] = "test-key"

    client.post("/api/enrollment/enroll", json={"course_number": "CMPUT101"}, headers=headers)

    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client

    tool_response = make_tool_use_response(
        "get_schedule", {"student_id": "STU001"}
    )
    text_response = make_text_response("Your schedule shows CMPUT101 on Monday and Wednesday.")
    mock_client.messages.create.side_effect = [tool_response, text_response]

    resp = client.post("/api/advisor/chat", json={
        "message": "Show my schedule",
    }, headers=headers)

    assert resp.status_code == 200
    assert "schedule" in resp.get_json()["response"].lower()
