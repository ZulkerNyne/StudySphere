from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
from flask import request, jsonify, current_app
from jose import jwt, JWTError


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_token(student_id, expires_minutes=60):
    payload = {
        "sub": student_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def create_refresh_token(student_id):
    return create_token(student_id, expires_minutes=7 * 24 * 60)


def decode_token(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
            request.student_id = payload["sub"]
        except JWTError:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(*args, **kwargs)
    return decorated
