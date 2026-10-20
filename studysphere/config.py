import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///studysphere.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")
