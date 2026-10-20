from datetime import datetime, timezone
from studysphere.app import db


FEE_PER_CREDIT = {
    "Full-time": {"Undergraduate": 350, "Graduate": 500},
    "Part-time": {"Undergraduate": 450, "Graduate": 600},
}

MAX_COURSES = {"Full-time": 5, "Part-time": 3}


class Student(db.Model):
    __tablename__ = "students"

    student_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    program = db.Column(db.String, nullable=False)
    degree_status = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default="Full-time")
    password_hash = db.Column(db.String, nullable=False)

    enrollments = db.relationship("Enrollment", back_populates="student")

    @property
    def max_courses(self):
        return MAX_COURSES.get(self.status, 5)

    @property
    def fee_per_credit(self):
        return FEE_PER_CREDIT.get(self.status, {}).get(self.degree_status, 400)


class Course(db.Model):
    __tablename__ = "courses"

    course_number = db.Column(db.String, primary_key=True)
    course_name = db.Column(db.String, nullable=False)
    professor_name = db.Column(db.String, nullable=False)
    start_time = db.Column(db.String, nullable=False)
    end_time = db.Column(db.String, nullable=False)
    level = db.Column(db.String, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.String, nullable=False)
    days = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, default="")
    embedding_id = db.Column(db.String, nullable=True)

    enrollments = db.relationship("Enrollment", back_populates="course")


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String, db.ForeignKey("students.student_id"), nullable=False)
    course_number = db.Column(db.String, db.ForeignKey("courses.course_number"), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    dropped_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String, nullable=False, default="active")

    student = db.relationship("Student", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")

    __table_args__ = (
        db.UniqueConstraint("student_id", "course_number", name="uq_active_enrollment"),
    )
