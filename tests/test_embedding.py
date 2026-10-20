import os
import tempfile
import shutil

from studysphere.models import Course
from studysphere.services.embedding_service import (
    build_course_document,
    ingest_courses,
    semantic_search,
    get_collection,
)


def seed_courses(db):
    courses = [
        Course(
            course_number="CMPUT466",
            course_name="Machine Learning",
            professor_name="Dr. Smith",
            start_time="09:00 AM",
            end_time="10:30 AM",
            level="Undergraduate",
            credits=3,
            total_seats=40,
            available_seats=10,
            semester="Fall",
            days="Tuesday, Thursday",
            description="Covers supervised and unsupervised learning, neural networks, decision trees.",
        ),
        Course(
            course_number="CMPUT551",
            course_name="Deep Learning",
            professor_name="Dr. Brown",
            start_time="01:00 PM",
            end_time="02:30 PM",
            level="Graduate",
            credits=3,
            total_seats=25,
            available_seats=5,
            semester="Fall",
            days="Monday, Wednesday",
            description="Advanced neural network architectures including CNNs, RNNs, and transformers.",
        ),
        Course(
            course_number="MATH201",
            course_name="Linear Algebra",
            professor_name="Dr. Lee",
            start_time="11:00 AM",
            end_time="12:30 PM",
            level="Undergraduate",
            credits=4,
            total_seats=30,
            available_seats=15,
            semester="Winter",
            days="Monday, Wednesday, Friday",
            description="Vectors, matrices, eigenvalues, and applications to data science.",
        ),
        Course(
            course_number="BIOL101",
            course_name="Intro to Biology",
            professor_name="Dr. Patel",
            start_time="02:00 PM",
            end_time="03:30 PM",
            level="Undergraduate",
            credits=3,
            total_seats=35,
            available_seats=20,
            semester="Fall",
            days="Tuesday, Thursday",
            description="Fundamentals of cell biology, genetics, and ecology.",
        ),
    ]
    for c in courses:
        db.session.add(c)
    db.session.commit()
    return courses


def test_build_course_document(app, db):
    with app.app_context():
        seed_courses(db)
        course = db.session.get(Course, "CMPUT466")
        doc = build_course_document(course)
        assert "CMPUT466" in doc
        assert "Machine Learning" in doc
        assert "Dr. Smith" in doc
        assert "neural networks" in doc


def test_ingest_courses(app, db):
    tmpdir = tempfile.mkdtemp()
    try:
        app.config["CHROMA_PERSIST_DIR"] = tmpdir
        with app.app_context():
            seed_courses(db)
            count = ingest_courses()
            assert count == 4
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_semantic_search_ai(app, db):
    tmpdir = tempfile.mkdtemp()
    try:
        app.config["CHROMA_PERSIST_DIR"] = tmpdir
        with app.app_context():
            seed_courses(db)
            ingest_courses()

            results = semantic_search("artificial intelligence and neural networks")
            course_numbers = [c.course_number for c in results]
            assert "CMPUT466" in course_numbers or "CMPUT551" in course_numbers
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_semantic_search_with_semester_filter(app, db):
    tmpdir = tempfile.mkdtemp()
    try:
        app.config["CHROMA_PERSIST_DIR"] = tmpdir
        with app.app_context():
            seed_courses(db)
            ingest_courses()

            results = semantic_search("math", semester="Winter")
            course_numbers = [c.course_number for c in results]
            assert "MATH201" in course_numbers
            assert "CMPUT466" not in course_numbers
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_semantic_search_biology(app, db):
    tmpdir = tempfile.mkdtemp()
    try:
        app.config["CHROMA_PERSIST_DIR"] = tmpdir
        with app.app_context():
            seed_courses(db)
            ingest_courses()

            results = semantic_search("cell biology and genetics")
            course_numbers = [c.course_number for c in results]
            assert "BIOL101" in course_numbers
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
