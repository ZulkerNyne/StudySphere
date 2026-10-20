"""Seed the database with real University of Calgary courses and ingest into ChromaDB."""
import random

from studysphere.app import create_app, db
from studysphere.models import Course
from studysphere.services.embedding_service import ingest_courses

FIRST_NAMES = [
    "James", "Sarah", "Michael", "Emily", "David", "Jessica", "Robert", "Jennifer",
    "William", "Lisa", "Richard", "Karen", "Joseph", "Nancy", "Thomas", "Betty",
    "Charles", "Margaret", "Daniel", "Sandra", "Matthew", "Ashley", "Anthony", "Dorothy",
    "Mark", "Kimberly", "Steven", "Donna", "Paul", "Carol", "Wei", "Priya",
    "Ahmed", "Fatima", "Yuki", "Raj", "Elena", "Omar", "Mei", "Amir",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
    "Jackson", "Martin", "Lee", "Thompson", "White", "Harris", "Clark", "Lewis",
    "Robinson", "Chen", "Patel", "Kim", "Singh", "Nakamura", "Khan",
]

# (course_number, course_name, level, credits, semester, days, start_time, end_time, description)
UCALGARY_COURSES = [
    # ── CPSC (Computer Science) ── Undergraduate ──
    ("CPSC 217", "Introduction to Computer Science for Multidisciplinary Studies I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "09:00 AM", "09:50 AM",
     "Introduction to problem solving, the analysis and design of small-scale computational systems, and implementation using a procedural programming language. For students outside computer science."),
    ("CPSC 219", "Introduction to Computer Science for Multidisciplinary Studies II", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Continuation of CPSC 217. Emphasis on object-oriented analysis and design of small-scale computational systems and implementation using an object-oriented language."),
    ("CPSC 231", "Introduction to Computer Science for Computer Science Majors I", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Introduction to problem solving, the analysis and design of small-scale computational systems, and implementation using a procedural programming language. For computer science majors."),
    ("CPSC 233", "Introduction to Computer Science for Computer Science Majors II", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Continuation of CPSC 231. Emphasis on object-oriented analysis and design of small-scale computational systems and implementation using an object-oriented language such as Java."),
    ("CPSC 251", "Theoretical Foundations of Computer Science I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Proof techniques. Recursion and iteration. Specification of algorithmic problems and correctness of algorithms. Logic. Basics of combinatorics and graph theory."),
    ("CPSC 313", "Introduction to Computability", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "An introduction to abstract models of sequential computation including finite automata, regular expressions, context-free grammars, and Turing machines."),
    ("CPSC 319", "Data Structures, Algorithms, and Their Applications", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Fundamental data structures and algorithms. Design paradigms: divide and conquer, greedy, dynamic programming. Graph algorithms. Applications to real-world problems."),
    ("CPSC 329", "Explorations in Information Security and Privacy", "Undergraduate", 3, "Fall", "Monday, Wednesday", "02:00 PM", "03:15 PM",
     "A broad survey of topics in information security and privacy including basic cryptography, network security, software security, and privacy technologies."),
    ("CPSC 331", "Data Structures, Algorithms, and Their Analysis", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Systematic study of data structures and algorithms, analysis of their efficiency. Stacks, queues, trees, hash tables, heaps, graphs. Sorting and searching."),
    ("CPSC 355", "Computing Machinery I", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "An introduction to computing machinery including computer architecture, assembly language programming, and the relationship between high-level languages and machine code."),
    ("CPSC 359", "Computing Machinery II", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "Continuation of CPSC 355. Input/output, interrupts, memory hierarchy, concurrency, and interaction between hardware and software systems."),
    ("CPSC 413", "Design and Analysis of Algorithms I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "02:00 PM", "02:50 PM",
     "Techniques for the analysis of algorithms including counting, summation, recurrences, and asymptotic relations. Algorithm design paradigms and NP-completeness."),
    ("CPSC 418", "Introduction to Cryptography", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Symmetric-key cryptography, public-key cryptography, hash functions, digital signatures, key management, and protocols for secure communication."),
    ("CPSC 433", "Artificial Intelligence", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "An introduction to the science of artificial intelligence. Topics include search, knowledge representation, planning, reasoning under uncertainty, and machine learning."),
    ("CPSC 441", "Computer Networks", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Principles of computer networks. Protocol architectures, physical links, switching, internetworking, transport, naming and content distribution, network applications."),
    ("CPSC 449", "Programming Paradigms", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "Examination of the basic principles of the major programming language paradigms: procedural, object-oriented, functional, and logic programming."),
    ("CPSC 457", "Principles of Operating Systems", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "02:00 PM", "02:50 PM",
     "Operating system principles. Processes, threads, synchronization, scheduling, memory management, file systems, device management, and security."),
    ("CPSC 471", "Data Base Management Systems", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "03:30 PM", "04:45 PM",
     "Databases from a user's perspective: the relational data model, SQL, entity-relationship modelling, normalization, transactions, and database application programming."),
    ("CPSC 481", "Human-Computer Interaction I", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "Fundamental theory and practice of the design, implementation, and evaluation of human-computer interfaces. User-centred design methodologies and usability testing."),

    # ── CPSC Graduate ──
    ("CPSC 501", "Advanced Programming Techniques", "Graduate", 3, "Fall", "Monday, Wednesday", "04:00 PM", "05:15 PM",
     "Advanced concepts in software design and development. Design patterns, refactoring, software architecture, and advanced object-oriented programming."),
    ("CPSC 502", "Research Project in Computer Science", "Graduate", 3, "Winter", "Thursday", "02:00 PM", "04:50 PM",
     "A supervised research project in an area of computer science culminating in a written report and oral presentation."),
    ("CPSC 517", "Design and Analysis of Algorithms II", "Graduate", 3, "Fall", "Tuesday, Thursday", "05:00 PM", "06:15 PM",
     "Advanced algorithm design: approximation algorithms, randomized algorithms, amortized analysis, linear programming, and advanced graph algorithms."),
    ("CPSC 526", "Network Systems Security", "Graduate", 3, "Winter", "Monday, Wednesday", "04:00 PM", "05:15 PM",
     "Security threats in networked systems. Firewalls, intrusion detection, VPNs, secure protocols, and analysis of network-based attacks."),
    ("CPSC 531", "Systems Modelling and Simulation", "Graduate", 3, "Fall", "Monday, Wednesday", "05:30 PM", "06:45 PM",
     "Discrete and continuous simulation methods, statistical analysis of simulation data, random number generation, and performance modelling."),
    ("CPSC 544", "Machine Learning", "Graduate", 3, "Winter", "Tuesday, Thursday", "03:30 PM", "04:45 PM",
     "Supervised and unsupervised learning, neural networks, support vector machines, ensemble methods, deep learning, and applications to real-world data."),
    ("CPSC 550", "Systems Software", "Graduate", 3, "Fall", "Tuesday, Thursday", "03:30 PM", "04:45 PM",
     "Advanced topics in operating systems, compilers, and runtime environments. Concurrency, memory management, and modern systems programming."),
    ("CPSC 559", "Introduction to Distributed Systems", "Graduate", 3, "Winter", "Monday, Wednesday", "05:30 PM", "06:45 PM",
     "Distributed computing fundamentals: communication, coordination, consistency, replication, fault tolerance, and distributed algorithms."),
    ("CPSC 571", "Design and Implementation of Database Systems", "Graduate", 3, "Fall", "Monday, Wednesday", "05:30 PM", "06:45 PM",
     "Internal architecture of database systems: storage, indexing, query processing, query optimization, transaction management, and recovery."),
    ("CPSC 583", "Introduction to Information Visualization", "Graduate", 3, "Winter", "Tuesday, Thursday", "05:00 PM", "06:15 PM",
     "Principles of information visualization. Visual encoding, interaction, and the design and evaluation of visualization systems for complex data."),
    ("CPSC 601", "Topics in Artificial Intelligence", "Graduate", 3, "Fall", "Thursday", "06:00 PM", "08:50 PM",
     "Advanced topics in AI including deep reinforcement learning, generative models, large language models, and AI safety."),
    ("CPSC 619", "Quantum Computation", "Graduate", 3, "Winter", "Tuesday", "06:00 PM", "08:50 PM",
     "Quantum computing fundamentals: qubits, quantum gates, quantum algorithms (Shor's, Grover's), quantum error correction, and applications."),

    # ── ENSF (Software Engineering) ──
    ("ENSF 300", "Software Engineering Fundamentals", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Fundamentals of software engineering including requirements, design, implementation, testing, and project management."),
    ("ENSF 310", "Fundamentals of Software Design and Development", "Undergraduate", 4, "Fall", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Object-oriented design principles, UML modelling, version control, software testing, and collaborative development practices."),
    ("ENSF 380", "Data Structures and Algorithms for Engineers", "Undergraduate", 4, "Winter", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Data structures and algorithms with emphasis on engineering applications. Trees, graphs, sorting, searching, and complexity analysis."),
    ("ENSF 409", "Principles of Software Development", "Undergraduate", 4, "Winter", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Advanced software development using Java. Database connectivity, GUI programming, design patterns, and software architecture."),
    ("ENSF 480", "Principles of Software Design", "Undergraduate", 4, "Fall", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "Software design patterns, architectural patterns, design principles (SOLID), refactoring, and framework design."),
    ("ENSF 607", "Advanced Software Engineering", "Graduate", 3, "Winter", "Monday, Wednesday", "05:30 PM", "06:45 PM",
     "Advanced topics in software engineering: agile at scale, continuous integration/deployment, microservices, and software quality assurance."),
    ("ENSF 612", "Advanced Database Management and Applications", "Graduate", 3, "Fall", "Tuesday, Thursday", "05:00 PM", "06:15 PM",
     "Advanced database concepts: distributed databases, NoSQL, data warehousing, big data analytics, and cloud data management."),

    # ── DATA (Data Science) ──
    ("DATA 201", "Thinking with Data", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "09:00 AM", "09:50 AM",
     "Introduction to data literacy and computational thinking. Data collection, visualization, and basic statistical reasoning."),
    ("DATA 211", "Programming for Data Science", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Programming in Python for data science: data manipulation, visualization, and introduction to machine learning libraries."),
    ("DATA 311", "Statistical Methods for Data Science", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Statistical modelling for data science: regression, classification, resampling methods, and model selection."),
    ("DATA 411", "Machine Learning for Data Science", "Graduate", 3, "Winter", "Tuesday, Thursday", "03:30 PM", "04:45 PM",
     "Applied machine learning: supervised learning, unsupervised learning, feature engineering, model evaluation, and deployment."),
    ("DATA 601", "Working with Data and Visualization", "Graduate", 3, "Fall", "Monday, Wednesday", "05:30 PM", "06:45 PM",
     "Data wrangling, cleaning, and transformation. Advanced visualization techniques and tools for exploring complex datasets."),

    # ── MATH (Mathematics) ── Undergraduate ──
    ("MATH 211", "Linear Methods I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "08:00 AM", "08:50 AM",
     "Systems of linear equations, matrices, determinants, vectors in R^n, eigenvalues and eigenvectors, and applications."),
    ("MATH 213", "Calculus and Introductory Analysis I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "09:00 AM", "09:50 AM",
     "Limits, continuity, derivatives, applications of differentiation, and introduction to integration."),
    ("MATH 249", "Introductory Calculus", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "08:00 AM", "09:15 AM",
     "Review of functions, limits, differentiation and its applications, integration. For students with limited high school math."),
    ("MATH 253", "Calculus II", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "09:00 AM", "09:50 AM",
     "Techniques of integration, improper integrals, sequences and series, Taylor polynomials, parametric equations, and polar coordinates."),
    ("MATH 265", "University Calculus I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Limits, derivatives, applications of differentiation, the definite integral, and the fundamental theorem of calculus."),
    ("MATH 267", "University Calculus II", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Techniques of integration, applications of integration, differential equations, sequences and series, and parametric equations."),
    ("MATH 271", "Discrete Mathematics", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Logic, proof techniques, sets, functions, relations, counting principles, graph theory, and elementary number theory."),
    ("MATH 311", "Linear Methods II", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Abstract vector spaces, linear transformations, inner product spaces, spectral theorem, and quadratic forms."),
    ("MATH 315", "Differential Equations I", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "First-order differential equations, linear differential equations, systems of ODEs, Laplace transforms, and applications."),
    ("MATH 375", "Differential Equations II", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "Partial differential equations, Fourier series, boundary value problems, and special functions."),
    ("MATH 381", "Introduction to Real Analysis", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "Rigorous treatment of limits, continuity, differentiation, and integration of functions of a real variable."),
    ("MATH 413", "Introduction to Abstract Algebra", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "02:00 PM", "02:50 PM",
     "Groups, rings, fields, and homomorphisms with emphasis on proof techniques and structural properties."),
    ("MATH 415", "Introduction to Number Theory", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "Divisibility, prime numbers, modular arithmetic, quadratic residues, Diophantine equations, and cryptographic applications."),

    # ── MATH Graduate ──
    ("MATH 501", "Measure Theory and Integration", "Graduate", 3, "Fall", "Monday, Wednesday", "04:00 PM", "05:15 PM",
     "Lebesgue measure and integration, convergence theorems, L^p spaces, and applications to probability."),
    ("MATH 511", "Linear Algebra II", "Graduate", 3, "Winter", "Tuesday, Thursday", "04:00 PM", "05:15 PM",
     "Advanced linear algebra: canonical forms, multilinear algebra, tensor products, and applications."),
    ("MATH 607", "Algebraic Topology", "Graduate", 3, "Fall", "Tuesday, Thursday", "05:00 PM", "06:15 PM",
     "Fundamental group, covering spaces, homology theory, and cohomology. Applications to geometry and algebra."),

    # ── STAT (Statistics) ──
    ("STAT 205", "Introduction to Statistics", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Descriptive statistics, probability, random variables, sampling distributions, confidence intervals, and hypothesis testing."),
    ("STAT 213", "Introduction to Statistics I", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Data collection, descriptive statistics, probability models, statistical inference, and regression for science and engineering students."),
    ("STAT 321", "Introduction to Probability", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "Probability spaces, random variables, expectation, moment generating functions, limit theorems, and common distributions."),
    ("STAT 323", "Introduction to Statistical Methods", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Multiple regression, ANOVA, experimental design, nonparametric methods, and introduction to Bayesian statistics."),
    ("STAT 421", "Mathematical Statistics", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "02:00 PM", "02:50 PM",
     "Sampling distributions, point and interval estimation, hypothesis testing, likelihood methods, and decision theory."),
    ("STAT 517", "Bayesian Statistics", "Graduate", 3, "Winter", "Tuesday, Thursday", "05:00 PM", "06:15 PM",
     "Bayesian inference, prior distributions, MCMC methods, hierarchical models, and Bayesian computation."),
    ("STAT 521", "Multivariate Analysis", "Graduate", 3, "Fall", "Monday, Wednesday", "05:30 PM", "06:45 PM",
     "Multivariate normal distribution, principal components, factor analysis, discriminant analysis, and clustering."),

    # ── PHYS (Physics) ── Undergraduate ──
    ("PHYS 211", "Mechanics", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "08:00 AM", "08:50 AM",
     "Newtonian mechanics: kinematics, forces, energy, momentum, rotational dynamics, oscillations, and gravitation."),
    ("PHYS 221", "Waves, Electricity, and Magnetism", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "08:00 AM", "08:50 AM",
     "Wave phenomena, electrostatics, electric circuits, magnetism, electromagnetic induction, and Maxwell's equations."),
    ("PHYS 259", "Electricity and Magnetism", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Electrostatics, Gauss's law, electric potential, capacitance, dielectrics, magnetic fields, Faraday's law, and AC circuits."),
    ("PHYS 301", "Quantum Physics I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Wave-particle duality, Schrodinger equation, potential wells, harmonic oscillator, hydrogen atom, and angular momentum."),
    ("PHYS 321", "Classical Mechanics I", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "Lagrangian and Hamiltonian mechanics, central force problems, rigid body dynamics, and coupled oscillations."),
    ("PHYS 323", "Electromagnetic Theory I", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Electrostatics, magnetostatics, electromagnetic wave propagation, and introduction to special relativity."),
    ("PHYS 343", "Statistical and Thermal Physics", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Thermodynamics, statistical mechanics, kinetic theory, entropy, and applications to systems of particles."),
    ("PHYS 355", "Optics", "Undergraduate", 3, "Fall", "Monday, Wednesday", "02:00 PM", "03:15 PM",
     "Geometrical optics, wave optics, interference, diffraction, polarization, and modern optical instruments."),
    ("PHYS 443", "Quantum Physics II", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "Perturbation theory, identical particles, scattering theory, and applications to atomic and molecular physics."),

    # ── PHYS Graduate ──
    ("PHYS 521", "Classical Mechanics II", "Graduate", 3, "Fall", "Monday, Wednesday", "04:00 PM", "05:15 PM",
     "Advanced classical mechanics: Hamilton-Jacobi theory, canonical transformations, nonlinear dynamics, and chaos."),
    ("PHYS 541", "Quantum Mechanics I", "Graduate", 3, "Fall", "Tuesday, Thursday", "04:00 PM", "05:15 PM",
     "Mathematical foundations of quantum mechanics, Hilbert spaces, operator theory, and approximation methods."),
    ("PHYS 631", "Particle Physics", "Graduate", 3, "Winter", "Thursday", "06:00 PM", "08:50 PM",
     "Standard model of particle physics, gauge theories, symmetry breaking, Feynman diagrams, and current experimental results."),

    # ── CHEM (Chemistry) ── Undergraduate ──
    ("CHEM 201", "General Chemistry I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "09:00 AM", "09:50 AM",
     "Atomic structure, chemical bonding, molecular geometry, stoichiometry, thermochemistry, and introduction to chemical equilibrium."),
    ("CHEM 203", "General Chemistry II", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "09:00 AM", "09:50 AM",
     "Chemical equilibrium, acids and bases, electrochemistry, kinetics, and introduction to organic chemistry."),
    ("CHEM 211", "Analytical Chemistry I", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Quantitative analysis, gravimetric and volumetric methods, equilibrium calculations, and introduction to spectroscopy."),
    ("CHEM 351", "Organic Chemistry I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Structure, nomenclature, and reactions of aliphatic hydrocarbons, stereochemistry, and substitution and elimination reactions."),
    ("CHEM 353", "Organic Chemistry II", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Reactions of aromatic compounds, carbonyl chemistry, amines, carbohydrates, amino acids, and spectroscopic identification."),
    ("CHEM 401", "Physical Chemistry I", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "Chemical thermodynamics, phase equilibria, electrochemistry, and surface chemistry."),
    ("CHEM 403", "Physical Chemistry II", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "Chemical kinetics, quantum chemistry, molecular spectroscopy, and statistical thermodynamics."),
    ("CHEM 431", "Inorganic Chemistry I", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "02:00 PM", "02:50 PM",
     "Coordination chemistry, crystal field theory, organometallic chemistry, and bioinorganic chemistry."),

    # ── CHEM Graduate ──
    ("CHEM 501", "Advanced Physical Chemistry", "Graduate", 3, "Fall", "Monday, Wednesday", "04:00 PM", "05:15 PM",
     "Advanced thermodynamics, statistical mechanics, and quantum chemistry for graduate students."),
    ("CHEM 525", "Advanced Organic Synthesis", "Graduate", 3, "Winter", "Tuesday, Thursday", "04:00 PM", "05:15 PM",
     "Retrosynthetic analysis, modern synthetic methods, catalysis, and total synthesis of complex molecules."),

    # ── BIOL (Biology) ── Undergraduate ──
    ("BIOL 205", "Concepts in Biology I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "09:00 AM", "09:50 AM",
     "Cell biology, genetics, molecular biology, and evolution. Lecture-based introduction to fundamental biological concepts."),
    ("BIOL 207", "Concepts in Biology II", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "09:00 AM", "09:50 AM",
     "Ecology, diversity of life, plant and animal physiology, and evolutionary biology."),
    ("BIOL 211", "Principles of Cell Biology", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Cell structure and function, membranes, organelles, cell cycle, signal transduction, and gene expression."),
    ("BIOL 213", "Principles of Genetics and Evolution", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Mendelian genetics, molecular genetics, population genetics, evolutionary theory, and phylogenetics."),
    ("BIOL 311", "Molecular Biology", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "DNA replication, transcription, translation, gene regulation, recombinant DNA technology, and genomics."),
    ("BIOL 313", "Microbiology", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Microbial diversity, structure, physiology, genetics, pathogenesis, immunology, and applied microbiology."),
    ("BIOL 331", "Ecology", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Population ecology, community ecology, ecosystem ecology, biodiversity, and conservation biology."),
    ("BIOL 371", "Biochemistry I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "02:00 PM", "02:50 PM",
     "Amino acids, protein structure, enzymes, carbohydrate metabolism, citric acid cycle, and electron transport."),
    ("BIOL 373", "Biochemistry II", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "02:00 PM", "02:50 PM",
     "Lipid metabolism, amino acid metabolism, nucleotide biosynthesis, molecular biology of gene expression, and signal transduction."),
    ("BIOL 401", "Neurobiology", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "03:30 PM", "04:45 PM",
     "Neural signalling, synaptic transmission, sensory systems, motor systems, and neural development."),

    # ── BIOL Graduate ──
    ("BIOL 501", "Advanced Molecular Biology", "Graduate", 3, "Fall", "Monday, Wednesday", "05:30 PM", "06:45 PM",
     "Advanced molecular biology techniques: CRISPR, next-generation sequencing, proteomics, and functional genomics."),
    ("BIOL 519", "Advanced Ecology", "Graduate", 3, "Winter", "Tuesday, Thursday", "05:00 PM", "06:15 PM",
     "Advanced topics in ecology: metacommunities, landscape ecology, global change biology, and quantitative ecology."),

    # ── ECON (Economics) ── Undergraduate ──
    ("ECON 201", "Introduction to Microeconomics", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Consumer theory, firm behaviour, market structures, welfare economics, and government intervention in markets."),
    ("ECON 203", "Introduction to Macroeconomics", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "National income, unemployment, inflation, monetary and fiscal policy, economic growth, and international trade."),
    ("ECON 295", "Introduction to Mathematical Economics", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Mathematical methods for economics: optimization, linear algebra, differential equations applied to economic models."),
    ("ECON 301", "Intermediate Microeconomics", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "Advanced consumer and producer theory, general equilibrium, market failures, externalities, and public goods."),
    ("ECON 303", "Intermediate Macroeconomics", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "IS-LM model, AD-AS framework, monetary policy transmission, fiscal policy, and economic fluctuations."),
    ("ECON 395", "Econometrics", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "Regression analysis, hypothesis testing, multicollinearity, heteroskedasticity, time series, and panel data methods."),
    ("ECON 413", "Game Theory", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "Strategic interaction, Nash equilibrium, extensive form games, repeated games, bargaining, and mechanism design."),
    ("ECON 421", "International Economics", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "International trade theory, trade policy, exchange rates, balance of payments, and international monetary systems."),
    ("ECON 441", "Financial Economics", "Undergraduate", 3, "Fall", "Monday, Wednesday", "02:00 PM", "03:15 PM",
     "Asset pricing, portfolio theory, CAPM, efficient markets, derivatives, and corporate finance fundamentals."),

    # ── ECON Graduate ──
    ("ECON 501", "Microeconomic Theory I", "Graduate", 3, "Fall", "Tuesday, Thursday", "05:00 PM", "06:15 PM",
     "Advanced consumer theory, general equilibrium, welfare theorems, and market design."),
    ("ECON 503", "Macroeconomic Theory I", "Graduate", 3, "Winter", "Tuesday, Thursday", "05:00 PM", "06:15 PM",
     "Dynamic stochastic general equilibrium models, growth theory, and monetary and fiscal policy in a rigorous framework."),
    ("ECON 609", "Advanced Econometrics", "Graduate", 3, "Fall", "Monday, Wednesday", "05:30 PM", "06:45 PM",
     "Maximum likelihood estimation, GMM, instrumental variables, limited dependent variables, and treatment effects."),

    # ── PHIL (Philosophy) ──
    ("PHIL 201", "History of Philosophy I", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Ancient and medieval philosophy: Socrates, Plato, Aristotle, Stoicism, and major medieval thinkers."),
    ("PHIL 203", "History of Philosophy II", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Modern philosophy: Descartes, Hume, Kant, and their influence on contemporary philosophical thought."),
    ("PHIL 249", "Morality and Society", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "Introduction to ethical theory and its application to contemporary moral and social issues."),
    ("PHIL 267", "Introduction to Logic", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "Formal logic: propositional and predicate logic, proof techniques, validity, and applications to everyday reasoning."),
    ("PHIL 279", "Scientific and Critical Reasoning", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Logic of scientific reasoning, induction, probability, causal inference, and critical evaluation of arguments."),
    ("PHIL 314", "Epistemology", "Undergraduate", 3, "Winter", "Monday, Wednesday", "02:00 PM", "03:15 PM",
     "Nature of knowledge, justification, skepticism, perception, memory, and theories of truth."),
    ("PHIL 367", "Formal Logic", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "Advanced formal logic: meta-theory, completeness, soundness, first-order theories, and computability."),
    ("PHIL 411", "Philosophy of Mind", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "03:30 PM", "04:45 PM",
     "Consciousness, mental causation, personal identity, artificial intelligence, and the mind-body problem."),
    ("PHIL 413", "Ethics of Artificial Intelligence", "Undergraduate", 3, "Fall", "Monday, Wednesday", "03:30 PM", "04:45 PM",
     "Ethical frameworks for AI development: bias, fairness, transparency, autonomy, and responsible innovation."),

    # ── POLI (Political Science) ──
    ("POLI 201", "Introduction to Government and Politics", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Political institutions, democracy, authoritarianism, elections, political parties, and government structures."),
    ("POLI 213", "Introduction to International Relations", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Theories of international relations, global governance, conflict and cooperation, and contemporary global issues."),
    ("POLI 279", "Introduction to Political Theory", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "Classical and contemporary political thought: liberty, justice, equality, democracy, and human rights."),
    ("POLI 283", "Introduction to Comparative Politics", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "Comparative analysis of political systems, institutions, and processes across different countries and regimes."),
    ("POLI 381", "Canadian Politics", "Undergraduate", 3, "Fall", "Monday, Wednesday", "02:00 PM", "03:15 PM",
     "Canadian political institutions, federalism, parliamentary government, political parties, and policy-making."),
    ("POLI 423", "International Security", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "Theories and practices of international security, conflict resolution, arms control, and emerging security threats."),

    # ── SOCI (Sociology) ──
    ("SOCI 201", "Introduction to Sociology", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "09:00 AM", "09:50 AM",
     "Sociological perspectives, social structure, culture, socialization, inequality, and social institutions."),
    ("SOCI 301", "Sociological Theory", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "Classical and contemporary sociological theories: Marx, Weber, Durkheim, functionalism, conflict theory, and symbolic interactionism."),
    ("SOCI 311", "Social Research Methods", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "02:00 PM", "02:50 PM",
     "Quantitative and qualitative research methods, survey design, sampling, data analysis, and research ethics."),
    ("SOCI 325", "Sociology of Health and Illness", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Social determinants of health, health care systems, medicalization, and sociological perspectives on illness."),
    ("SOCI 401", "Advanced Sociological Theory", "Undergraduate", 3, "Fall", "Monday, Wednesday", "03:30 PM", "04:45 PM",
     "Contemporary theoretical debates: postmodernism, critical race theory, feminist theory, and global sociology."),

    # ── ENGG (Engineering) ──
    ("ENGG 201", "Statics", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "08:00 AM", "08:50 AM",
     "Force systems, equilibrium, trusses, frames, centroids, moments of inertia, and friction."),
    ("ENGG 202", "Engineering Dynamics", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "08:00 AM", "08:50 AM",
     "Kinematics and kinetics of particles and rigid bodies, work-energy methods, and impulse-momentum methods."),
    ("ENGG 225", "Fundamentals of Electrical Circuits", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "DC and AC circuit analysis, network theorems, operational amplifiers, capacitors, inductors, and transient analysis."),
    ("ENGG 233", "Computing for Engineers", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Computational problem solving using MATLAB and C. Structured programming, arrays, functions, and file I/O for engineers."),
    ("ENGG 311", "Engineering Thermodynamics", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "First and second laws, entropy, thermodynamic cycles, mixtures, and combustion processes."),
    ("ENGG 319", "Probability and Statistics for Engineers", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Probability, random variables, distributions, confidence intervals, hypothesis testing, and regression for engineering applications."),
    ("ENGG 349", "Fluid Mechanics", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Fluid properties, fluid statics, fluid dynamics, Bernoulli equation, viscous flow, and pipe flow."),
    ("ENGG 407", "Control Systems", "Undergraduate", 3, "Fall", "Monday, Wednesday", "02:00 PM", "03:15 PM",
     "Feedback control systems, transfer functions, Bode plots, root locus, stability, and PID controllers."),
    ("ENGG 461", "Structural Analysis", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "02:00 PM", "03:15 PM",
     "Analysis of statically determinate and indeterminate structures, energy methods, and matrix methods of structural analysis."),

    # ── ENGG Graduate ──
    ("ENGG 601", "Advanced Fluid Dynamics", "Graduate", 3, "Fall", "Monday, Wednesday", "05:30 PM", "06:45 PM",
     "Navier-Stokes equations, turbulence, boundary layers, compressible flow, and computational fluid dynamics."),
    ("ENGG 609", "Finite Element Methods", "Graduate", 3, "Winter", "Tuesday, Thursday", "05:00 PM", "06:15 PM",
     "Finite element formulation, element types, mesh generation, convergence, and applications to structural and thermal problems."),
    ("ENGG 619", "Advanced Control Systems", "Graduate", 3, "Winter", "Monday, Wednesday", "04:00 PM", "05:15 PM",
     "State-space methods, optimal control, robust control, nonlinear systems, and adaptive control."),

    # ── PSYC (Psychology) ──
    ("PSYC 200", "Principles of Psychology", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "10:00 AM", "10:50 AM",
     "Introduction to psychological science: learning, memory, cognition, development, personality, and abnormal behaviour."),
    ("PSYC 203", "Psychology of Thinking", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Cognitive psychology: perception, attention, memory, problem solving, decision making, and reasoning."),
    ("PSYC 312", "Developmental Psychology", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "11:00 AM", "12:15 PM",
     "Physical, cognitive, and social development from infancy through adolescence."),
    ("PSYC 375", "Abnormal Psychology", "Undergraduate", 3, "Winter", "Monday, Wednesday, Friday", "01:00 PM", "01:50 PM",
     "Classification, etiology, and treatment of psychological disorders: anxiety, mood, psychotic, and personality disorders."),
    ("PSYC 401", "Cognitive Neuroscience", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "03:30 PM", "04:45 PM",
     "Neural basis of cognition: attention, perception, memory, language, and executive functions."),

    # ── LING (Linguistics) ──
    ("LING 201", "Introduction to Linguistics", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "11:00 AM", "11:50 AM",
     "Overview of linguistic theory: phonetics, phonology, morphology, syntax, semantics, and language variation."),
    ("LING 301", "Syntax", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "Syntactic theory and analysis: phrase structure, transformations, constraints, and cross-linguistic variation."),

    # ── GRST (Greek and Roman Studies) ──
    ("GRST 211", "Greek Civilization", "Undergraduate", 3, "Fall", "Tuesday, Thursday", "12:30 PM", "01:45 PM",
     "Ancient Greek civilization: literature, philosophy, politics, art, and daily life from the Bronze Age to the Hellenistic period."),

    # ── GLGY (Geology) ──
    ("GLGY 209", "Introduction to Geology", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "09:00 AM", "09:50 AM",
     "Earth materials, plate tectonics, geological time, surface processes, and Earth's internal structure."),
    ("GLGY 301", "Sedimentology and Stratigraphy", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Sedimentary processes, depositional environments, stratigraphic principles, and basin analysis."),

    # ── KNES (Kinesiology) ──
    ("KNES 200", "Human Anatomy", "Undergraduate", 3, "Fall", "Monday, Wednesday, Friday", "08:00 AM", "08:50 AM",
     "Structure of the human body: musculoskeletal, nervous, cardiovascular, respiratory, and digestive systems."),
    ("KNES 259", "Biomechanics", "Undergraduate", 3, "Winter", "Tuesday, Thursday", "09:30 AM", "10:45 AM",
     "Mechanical principles applied to human movement: kinematics, kinetics, and analysis of sport and exercise."),
]


def random_professor():
    return f"Dr. {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def build_courses():
    courses = []
    for row in UCALGARY_COURSES:
        number, name, level, credits, semester, days, start, end, desc = row
        total_seats = random.randint(30, 120) if level == "Undergraduate" else random.randint(15, 40)
        available = random.randint(0, total_seats)
        courses.append(Course(
            course_number=number,
            course_name=name,
            professor_name=random_professor(),
            start_time=start,
            end_time=end,
            level=level,
            credits=credits,
            total_seats=total_seats,
            available_seats=available,
            semester=semester,
            days=days,
            description=desc,
        ))
    return courses


def seed():
    app = create_app()
    with app.app_context():
        existing = Course.query.count()
        if existing > 0:
            print(f"Clearing {existing} existing courses...")
            db.session.query(Course).delete()
            db.session.commit()

        courses = build_courses()
        for c in courses:
            db.session.add(c)
        db.session.commit()
        print(f"Seeded {len(courses)} real UCalgary courses into database.")

        count = ingest_courses()
        print(f"Ingested {count} courses into ChromaDB.")


if __name__ == "__main__":
    seed()
