from datetime import datetime, timezone

from app import create_app
from app.models import (
    Assessment,
    JobRole,
    MentorAssignment,
    MentorNote,
    Skill,
    StudentProfile,
    User,
    db,
)

CORE_USERS = [
    {
        "name": "Test Student",
        "email": "student@example.com",
        "password": "student123",
        "role": "student",
    },
    {
        "name": "Test Mentor",
        "email": "mentor@example.com",
        "password": "mentor123",
        "role": "mentor",
    },
    {
        "name": "Test TPO",
        "email": "tpo@example.com",
        "password": "tpo123",
        "role": "tpo",
    },
    {
        "name": "Test Admin",
        "email": "admin@example.com",
        "password": "admin123",
        "role": "admin",
    },
]

ADDITIONAL_USERS = [
    {
        "name": "Rahul Sharma",
        "email": "rahul.sharma@example.com",
        "password": "password123",
        "role": "student",
    },
    {
        "name": "Priya Patel",
        "email": "priya.patel@example.com",
        "password": "password123",
        "role": "student",
    },
    {
        "name": "Ananya Rao",
        "email": "ananya.rao@example.com",
        "password": "password123",
        "role": "student",
    },
    {
        "name": "Karthik Nair",
        "email": "karthik.nair@example.com",
        "password": "password123",
        "role": "student",
    },
    {
        "name": "Sneha Kulkarni",
        "email": "sneha.k@example.com",
        "password": "password123",
        "role": "student",
    },
    {
        "name": "Dr. Rajesh Kumar",
        "email": "rajesh.kumar@example.com",
        "password": "password123",
        "role": "mentor",
    },
]

JOB_ROLES_DATA = [
    {
        "name": "Full-Stack Web Developer",
        "skills": [
            "Data Structures & Algorithms",
            "Python & Flask APIs",
            "JavaScript & Modern Frontend",
            "SQL Database Optimization",
            "HTML5, CSS3 & Responsive UI",
            "Git & Version Control",
            "RESTful API Architecture",
        ],
    },
    {
        "name": "Data Analyst & Engineer",
        "skills": [
            "Advanced SQL & Relational Schema",
            "Python for Data Science (Pandas/NumPy)",
            "Data Visualization & Dashboards",
            "ETL Pipeline Design",
            "Statistical Modeling & Analysis",
            "Big Data Fundamentals",
        ],
    },
    {
        "name": "Cloud & DevOps Engineer",
        "skills": [
            "Linux System Administration",
            "Docker & Container Orchestration",
            "Kubernetes Cluster Architecture",
            "CI/CD Pipeline Automation",
            "Cloud Infrastructure (AWS/GCP)",
            "Networking & Cloud Security",
        ],
    },
    {
        "name": "AI/ML Specialist",
        "skills": [
            "Machine Learning Algorithms",
            "Deep Learning with PyTorch",
            "Natural Language Processing (NLP)",
            "Model Evaluation & Tuning",
            "Computer Vision Fundamentals",
        ],
    },
]


def seed_database():
    app = create_app()

    with app.app_context():
        db.create_all()

        # 1. Seed Users
        user_cache = {}
        for user_data in CORE_USERS + ADDITIONAL_USERS:
            user = User.query.filter_by(email=user_data["email"]).first()
            if user is None:
                user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    role=user_data["role"],
                )
                user.set_password(user_data["password"])
                db.session.add(user)
                db.session.flush()
                print(f"Created user: {user.name} ({user.email})")
            else:
                user.set_password(user_data["password"])
            user_cache[user.email] = user

        db.session.commit()

        # 2. Seed Job Roles & Skills
        role_cache = {}
        skill_cache = {}
        for role_data in JOB_ROLES_DATA:
            role = JobRole.query.filter_by(name=role_data["name"]).first()
            if role is None:
                role = JobRole(name=role_data["name"])
                db.session.add(role)
                db.session.flush()
                print(f"Created job role: {role.name}")
            role_cache[role.name] = role

            for skill_name in role_data["skills"]:
                skill = Skill.query.filter_by(job_role_id=role.id, name=skill_name).first()
                if skill is None:
                    skill = Skill(name=skill_name, job_role_id=role.id)
                    db.session.add(skill)
                    db.session.flush()
                    print(f"  Added skill: {skill.name} to {role.name}")
                skill_cache[(role.name, skill.name)] = skill

        db.session.commit()

        # 3. Seed Student Profiles
        profiles_data = [
            ("student@example.com", "Computer Science & Engineering", 3, "Full-Stack Web Developer"),
            ("rahul.sharma@example.com", "Computer Science & Engineering", 4, "Full-Stack Web Developer"),
            ("priya.patel@example.com", "Information Science & Engineering", 3, "Data Analyst & Engineer"),
            ("ananya.rao@example.com", "Electronics & Communication Engineering", 3, "Cloud & DevOps Engineer"),
            ("karthik.nair@example.com", "Computer Science & Engineering", 4, "Full-Stack Web Developer"),
            ("sneha.k@example.com", "Artificial Intelligence & Machine Learning", 2, "AI/ML Specialist"),
        ]

        for email, branch, year, role_name in profiles_data:
            user = user_cache.get(email)
            role = role_cache.get(role_name)
            if user and role:
                prof = StudentProfile.query.filter_by(user_id=user.id).first()
                if prof is None:
                    prof = StudentProfile(
                        user_id=user.id,
                        branch=branch,
                        year=year,
                        target_job_role_id=role.id,
                    )
                    db.session.add(prof)
                else:
                    prof.branch = branch
                    prof.year = year
                    prof.target_job_role_id = role.id

        db.session.commit()

        # 4. Seed Assessments
        assessments_map = {
            "student@example.com": {
                "Full-Stack Web Developer": {
                    "Data Structures & Algorithms": "learning",
                    "Python & Flask APIs": "confident",
                    "JavaScript & Modern Frontend": "comfortable",
                    "SQL Database Optimization": "learning",
                    "HTML5, CSS3 & Responsive UI": "confident",
                    "Git & Version Control": "confident",
                    "RESTful API Architecture": "comfortable",
                }
            },
            "rahul.sharma@example.com": {
                "Full-Stack Web Developer": {
                    "Data Structures & Algorithms": "confident",
                    "Python & Flask APIs": "confident",
                    "JavaScript & Modern Frontend": "confident",
                    "SQL Database Optimization": "confident",
                    "HTML5, CSS3 & Responsive UI": "confident",
                    "Git & Version Control": "confident",
                    "RESTful API Architecture": "comfortable",
                }
            },
            "priya.patel@example.com": {
                "Data Analyst & Engineer": {
                    "Advanced SQL & Relational Schema": "comfortable",
                    "Python for Data Science (Pandas/NumPy)": "confident",
                    "Data Visualization & Dashboards": "confident",
                    "ETL Pipeline Design": "learning",
                    "Statistical Modeling & Analysis": "learning",
                    "Big Data Fundamentals": "not_started",
                }
            },
            "ananya.rao@example.com": {
                "Cloud & DevOps Engineer": {
                    "Linux System Administration": "confident",
                    "Docker & Container Orchestration": "learning",
                    "Kubernetes Cluster Architecture": "not_started",
                    "CI/CD Pipeline Automation": "not_started",
                    "Cloud Infrastructure (AWS/GCP)": "learning",
                    "Networking & Cloud Security": "learning",
                }
            },
            "karthik.nair@example.com": {
                "Full-Stack Web Developer": {
                    "Data Structures & Algorithms": "confident",
                    "Python & Flask APIs": "confident",
                    "JavaScript & Modern Frontend": "confident",
                    "SQL Database Optimization": "confident",
                    "HTML5, CSS3 & Responsive UI": "confident",
                    "Git & Version Control": "confident",
                    "RESTful API Architecture": "confident",
                }
            },
        }

        for email, roles_dict in assessments_map.items():
            user = user_cache.get(email)
            if not user:
                continue
            for role_name, skills_dict in roles_dict.items():
                for skill_name, level in skills_dict.items():
                    skill = skill_cache.get((role_name, skill_name))
                    if skill:
                        existing = Assessment.query.filter_by(
                            student_id=user.id,
                            skill_id=skill.id,
                            source="self",
                        ).first()
                        if existing is None:
                            existing = Assessment(
                                student_id=user.id,
                                skill_id=skill.id,
                                level=level,
                                source="self",
                            )
                            db.session.add(existing)
                        else:
                            existing.level = level

        db.session.commit()

        # 5. Seed Mentor Assignments
        primary_mentor = user_cache["mentor@example.com"]
        dr_kumar = user_cache["rajesh.kumar@example.com"]

        pairings = [
            (primary_mentor, user_cache["student@example.com"]),
            (primary_mentor, user_cache["rahul.sharma@example.com"]),
            (primary_mentor, user_cache["ananya.rao@example.com"]),
            (dr_kumar, user_cache["priya.patel@example.com"]),
            (dr_kumar, user_cache["karthik.nair@example.com"]),
            (dr_kumar, user_cache["sneha.k@example.com"]),
        ]

        for mentor_user, student_user in pairings:
            existing = MentorAssignment.query.filter_by(
                mentor_id=mentor_user.id,
                student_id=student_user.id,
            ).first()
            if existing is None:
                db.session.add(
                    MentorAssignment(
                        mentor_id=mentor_user.id,
                        student_id=student_user.id,
                    )
                )

        db.session.commit()

        # 6. Seed Mentor Notes & Flags
        notes_data = [
            (
                primary_mentor.id,
                user_cache["student@example.com"].id,
                "Initial semester review: Student is progressing well on backend Flask APIs. Advised to focus on SQL indexing and DSA graph traversal before upcoming campus drives.",
                False,
            ),
            (
                primary_mentor.id,
                user_cache["student@example.com"].id,
                "Follow-up session: Full-stack portfolio project reviewed. Student has comfortable command of frontend, but needs 15 more practice problems in algorithmic complexity.",
                False,
            ),
            (
                primary_mentor.id,
                user_cache["ananya.rao@example.com"].id,
                "Mid-term assessment: Student has an 83% skill gap on Cloud & DevOps competencies. Falling behind in containerization and networking. Flagging for early placement intervention and remedial lab sessions.",
                True,
            ),
            (
                primary_mentor.id,
                user_cache["rahul.sharma@example.com"].id,
                "Mock technical interview completed. Student scored high in DSA and SQL optimization. Recommended for Tier-1 recruitment drive.",
                False,
            ),
            (
                dr_kumar.id,
                user_cache["priya.patel@example.com"].id,
                "Discussed data analytics capstone project. Advised student to build a real-time ETL dashboard to showcase during placement interviews.",
                False,
            ),
        ]

        for m_id, s_id, text, at_risk in notes_data:
            existing_note = MentorNote.query.filter_by(
                mentor_id=m_id,
                student_id=s_id,
                note_text=text,
            ).first()
            if existing_note is None:
                db.session.add(
                    MentorNote(
                        mentor_id=m_id,
                        student_id=s_id,
                        note_text=text,
                        at_risk=at_risk,
                        created_at=datetime.now(timezone.utc),
                    )
                )

        db.session.commit()
        print("Database successfully seeded with realistic academic cohort data!")


if __name__ == "__main__":
    seed_database()
