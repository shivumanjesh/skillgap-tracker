from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(20),
        db.CheckConstraint("role IN ('student', 'mentor', 'tpo', 'admin')"),
        nullable=False,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class JobRole(db.Model):
    __tablename__ = "job_role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    skills = db.relationship(
        "Skill",
        back_populates="job_role",
        cascade="all, delete-orphan",
    )


class Skill(db.Model):
    __tablename__ = "skill"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    job_role_id = db.Column(
        db.Integer,
        db.ForeignKey("job_role.id"),
        nullable=False,
    )
    job_role = db.relationship("JobRole", back_populates="skills")


class StudentProfile(db.Model):
    __tablename__ = "student_profile"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True,
    )
    branch = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    target_job_role_id = db.Column(
        db.Integer,
        db.ForeignKey("job_role.id"),
        nullable=True,
    )
    user = db.relationship(
        "User",
        backref=db.backref("student_profile", uselist=False),
    )
    target_job_role = db.relationship(
        "JobRole",
        backref="student_profiles",
    )


class Assessment(db.Model):
    __tablename__ = "assessment"

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True,
    )
    skill_id = db.Column(
        db.Integer,
        db.ForeignKey("skill.id"),
        primary_key=True,
    )
    level = db.Column(
        db.String(20),
        db.CheckConstraint(
            "level IN ('not_started', 'learning', 'comfortable', 'confident')"
        ),
        nullable=False,
    )
    source = db.Column(
        db.String(20),
        db.CheckConstraint("source IN ('self', 'mentor')"),
        primary_key=True,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    student = db.relationship(
        "User",
        backref="assessments",
        foreign_keys=[student_id],
    )
    skill = db.relationship(
        "Skill",
        backref="assessments",
    )


class MentorAssignment(db.Model):
    __tablename__ = "mentor_assignment"

    mentor_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True,
    )
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True,
    )
    mentor = db.relationship(
        "User",
        foreign_keys=[mentor_id],
        backref="mentor_assignments",
    )
    student = db.relationship(
        "User",
        foreign_keys=[student_id],
        backref="assigned_mentor_assignments",
    )


class MentorNote(db.Model):
    __tablename__ = "mentor_note"

    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
    )
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
    )
    note_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    at_risk = db.Column(db.Boolean, default=False, nullable=False)
    mentor = db.relationship(
        "User",
        foreign_keys=[mentor_id],
        backref="mentor_notes",
    )
    student = db.relationship(
        "User",
        foreign_keys=[student_id],
        backref="student_notes",
    )