from flask import Blueprint, request, jsonify
from studysphere.services.auth_service import login_required
from studysphere.services.advisor_service import chat_with_advisor

advisor_bp = Blueprint("advisor", __name__, url_prefix="/api/advisor")


@advisor_bp.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message required"}), 400

    history = data.get("history", [])
    history.append({"role": "user", "content": data["message"]})

    response_text, updated_history = chat_with_advisor(request.student_id, history)

    if isinstance(response_text, dict) and "error" in response_text:
        return jsonify(response_text), 503

    serializable_history = []
    for msg in updated_history:
        if msg["role"] == "user" and isinstance(msg["content"], list):
            serializable_history.append({
                "role": "user",
                "content": [
                    {
                        "type": item["type"],
                        "tool_use_id": item["tool_use_id"],
                        "content": item["content"],
                    }
                    if item.get("type") == "tool_result"
                    else item
                    for item in msg["content"]
                ],
            })
        elif msg["role"] == "assistant" and not isinstance(msg["content"], str):
            serialized_blocks = []
            for block in msg["content"]:
                if getattr(block, "type", None) == "text":
                    serialized_blocks.append({"type": "text", "text": block.text})
                elif getattr(block, "type", None) == "tool_use":
                    serialized_blocks.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })
            serializable_history.append({
                "role": "assistant",
                "content": serialized_blocks,
            })
        else:
            serializable_history.append(msg)

    return jsonify({
        "response": response_text,
        "history": serializable_history,
    })
