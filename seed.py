"""Seed the database with 500 courses and ingest them into ChromaDB."""
import random
from datetime import datetime, timedelta

from studysphere.app import create_app, db
from studysphere.models import Course
from studysphere.services.embedding_service import ingest_courses

DEPARTMENTS = ["CMPUT", "MATH", "PHYS", "BIOL", "CHEM", "ENGR", "ECON"]

SUBJECTS = {
    "CMPUT": [
        "Intro to Computing", "Data Structures", "Algorithms", "Machine Learning",
        "Artificial Intelligence", "Software Engineering", "Database Systems",
        "Computer Networks", "Operating Systems", "Web Development",
        "Cryptography", "Computer Graphics", "Natural Language Processing",
        "Deep Learning", "Cloud Computing", "Cybersecurity",
    ],
    "MATH": [
        "Calculus I", "Calculus II", "Linear Algebra", "Differential Equations",
        "Probability and Statistics", "Discrete Mathematics", "Number Theory",
        "Abstract Algebra", "Real Analysis", "Numerical Methods",
    ],
    "PHYS": [
        "General Physics I", "General Physics II", "Quantum Mechanics",
        "Thermodynamics", "Electromagnetism", "Astrophysics",
        "Optics", "Particle Physics", "Computational Physics",
    ],
    "BIOL": [
        "Intro to Biology", "Molecular Biology", "Genetics", "Ecology",
        "Biotechnology", "Neurobiology", "Microbiology", "Biochemistry",
    ],
    "CHEM": [
        "General Chemistry", "Organic Chemistry", "Inorganic Chemistry",
        "Analytical Chemistry", "Physical Chemistry", "Environmental Chemistry",
    ],
    "ENGR": [
        "Engineering Design", "Fluid Mechanics", "Structural Analysis",
        "Control Systems", "Electrical Circuits", "Mechanical Design",
        "Robotics", "Signal Processing",
    ],
    "ECON": [
        "Microeconomics", "Macroeconomics", "Econometrics", "Game Theory",
        "International Economics", "Financial Economics", "Public Policy",
    ],
}

DESCRIPTIONS = {
    "Machine Learning": "Covers supervised and unsupervised learning, neural networks, decision trees, SVMs, and model evaluation techniques.",
    "Artificial Intelligence": "Foundations of AI including search algorithms, knowledge representation, planning, and intelligent agents.",
    "Deep Learning": "Advanced neural network architectures including CNNs, RNNs, transformers, and generative models.",
    "Natural Language Processing": "Text processing, sentiment analysis, language models, and conversational AI systems.",
    "Data Structures": "Arrays, linked lists, trees, graphs, hash tables, and algorithm complexity analysis.",
    "Algorithms": "Sorting, searching, dynamic programming, greedy algorithms, and graph algorithms.",
    "Software Engineering": "Software development lifecycle, agile methodologies, testing, and project management.",
    "Database Systems": "Relational databases, SQL, normalization, query optimization, and NoSQL systems.",
    "Cloud Computing": "Cloud architectures, containerization, microservices, and serverless computing.",
    "Cybersecurity": "Network security, encryption, vulnerability assessment, and ethical hacking.",
    "Linear Algebra": "Vectors, matrices, eigenvalues, linear transformations, and applications to data science.",
    "Probability and Statistics": "Random variables, distributions, hypothesis testing, and regression analysis.",
    "Quantum Mechanics": "Wave functions, Schrodinger equation, quantum states, and measurement theory.",
    "Biotechnology": "Genetic engineering, CRISPR, bioinformatics, and pharmaceutical applications.",
    "Robotics": "Kinematics, sensor systems, control algorithms, and autonomous navigation.",
}

FIRST_NAMES = [
    "James", "Sarah", "Michael", "Emily", "David", "Jessica", "Robert", "Jennifer",
    "William", "Lisa", "Richard", "Karen", "Joseph", "Nancy", "Thomas", "Betty",
    "Charles", "Margaret", "Daniel", "Sandra", "Matthew", "Ashley", "Anthony", "Dorothy",
    "Mark", "Kimberly", "Steven", "Donna", "Paul", "Carol",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
]

DAYS_OPTIONS = [
    "Monday, Wednesday, Friday",
    "Monday, Wednesday",
    "Tuesday, Thursday",
    "Monday, Friday",
    "Wednesday, Friday",
    "Tuesday",
    "Thursday",
]


def random_professor():
    return f"Dr. {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_time():
    hour = random.randint(8, 18)
    minute = random.choice([0, 30])
    start = datetime(2000, 1, 1, hour, minute)
    duration = random.choice([60, 90, 120])
    end = start + timedelta(minutes=duration)
    return start.strftime("%I:%M %p"), end.strftime("%I:%M %p")


def generate_courses(count=500):
    courses = []
    used_numbers = set()

    while len(courses) < count:
        dept = random.choice(DEPARTMENTS)
        num = random.randint(100, 599)
        course_number = f"{dept}{num}"

        if course_number in used_numbers:
            continue
        used_numbers.add(course_number)

        name_list = SUBJECTS[dept]
        course_name = random.choice(name_list)
        start_time, end_time = random_time()
        level = "Graduate" if num >= 400 else "Undergraduate"
        total_seats = random.randint(25, 50)

        course = Course(
            course_number=course_number,
            course_name=course_name,
            professor_name=random_professor(),
            start_time=start_time,
            end_time=end_time,
            level=level,
            credits=random.choice([3, 4]),
            total_seats=total_seats,
            available_seats=random.randint(0, total_seats),
            semester=random.choice(["Fall", "Winter"]),
            days=random.choice(DAYS_OPTIONS),
            description=DESCRIPTIONS.get(course_name, ""),
        )
        courses.append(course)

    return courses


def seed():
    app = create_app()
    with app.app_context():
        existing = Course.query.count()
        if existing > 0:
            print(f"Database already has {existing} courses. Skipping seed.")
            return

        courses = generate_courses(500)
        for c in courses:
            db.session.add(c)
        db.session.commit()
        print(f"Seeded {len(courses)} courses into database.")

        count = ingest_courses()
        print(f"Ingested {count} courses into ChromaDB.")


if __name__ == "__main__":
    seed()
