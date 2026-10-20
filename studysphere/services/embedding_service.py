import chromadb
from flask import current_app
from studysphere.app import db
from studysphere.models import Course


def get_chroma_client():
    persist_dir = current_app.config.get("CHROMA_PERSIST_DIR", "data/chroma")
    return chromadb.PersistentClient(path=persist_dir)


def get_collection(client=None):
    if client is None:
        client = get_chroma_client()
    return client.get_or_create_collection(
        name="course_descriptions",
        metadata={"hnsw:space": "cosine"},
    )


def build_course_document(course):
    parts = [
        f"{course.course_number}: {course.course_name}",
        f"Professor: {course.professor_name}",
        f"Level: {course.level}",
        f"Credits: {course.credits}",
        f"Semester: {course.semester}",
        f"Days: {course.days}",
        f"Time: {course.start_time} - {course.end_time}",
    ]
    if course.description:
        parts.append(f"Description: {course.description}")
    return " | ".join(parts)


def ingest_courses():
    collection = get_collection()
    courses = Course.query.all()

    documents = []
    ids = []
    metadatas = []

    for course in courses:
        doc = build_course_document(course)
        documents.append(doc)
        ids.append(course.course_number)
        metadatas.append({
            "course_number": course.course_number,
            "course_name": course.course_name,
            "semester": course.semester,
            "level": course.level,
            "available_seats": course.available_seats,
        })

    if documents:
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            collection.upsert(
                documents=documents[i:i + batch_size],
                ids=ids[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
            )

    return len(documents)


def semantic_search(query, n_results=10, semester=None, level=None):
    collection = get_collection()

    where_filters = {}
    if semester:
        where_filters["semester"] = semester
    if level:
        where_filters["level"] = level

    kwargs = {
        "query_texts": [query],
        "n_results": n_results,
    }
    if where_filters:
        if len(where_filters) == 1:
            key, val = next(iter(where_filters.items()))
            kwargs["where"] = {key: val}
        else:
            kwargs["where"] = {
                "$and": [{k: v} for k, v in where_filters.items()]
            }

    results = collection.query(**kwargs)

    courses = []
    if results["ids"] and results["ids"][0]:
        for course_number in results["ids"][0]:
            course = db.session.get(Course, course_number)
            if course:
                courses.append(course)

    return courses
