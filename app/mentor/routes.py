from datetime import datetime, timezone

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.auth.routes import role_required
from app.models import (
    Assessment,
    JobRole,
    MentorAssignment,
    MentorNote,
    Skill,
    StudentProfile,
    db,
)

mentor_bp = Blueprint(
    "mentor",
    __name__,
    url_prefix="/mentor",
    template_folder="templates",
)


@mentor_bp.get("/")
def index():
    return redirect(url_for("mentor.dashboard"))


@mentor_bp.get("/dashboard")
@login_required
@role_required("mentor")
def dashboard():
    assignments = MentorAssignment.query.filter_by(
        mentor_id=current_user.id,
    ).all()
    mentees = []

    for assignment in assignments:
        student = assignment.student
        profile = StudentProfile.query.filter_by(user_id=student.id).first()
        target_job_role = profile.target_job_role if profile else None
        skills = target_job_role.skills if target_job_role else []
        effective_level_by_skill = {}

        if skills:
            skill_ids = [skill.id for skill in skills]
            assessments = Assessment.query.filter(
                Assessment.student_id == student.id,
                Assessment.skill_id.in_(skill_ids),
            ).all()

            for assessment in assessments:
                if (
                    assessment.skill_id not in effective_level_by_skill
                    or assessment.source == "mentor"
                ):
                    effective_level_by_skill[assessment.skill_id] = assessment.level

        gap_percentage = None
        if skills:
            not_confident_count = sum(
                effective_level_by_skill.get(skill.id, "not_started")
                != "confident"
                for skill in skills
            )
            gap_percentage = round((not_confident_count / len(skills)) * 100, 2)

        # Get latest note for at-risk flag
        latest_note = MentorNote.query.filter_by(
            mentor_id=current_user.id,
            student_id=student.id,
        ).order_by(
            MentorNote.created_at.desc(),
            MentorNote.id.desc(),
        ).first()

        at_risk = latest_note.at_risk if latest_note else False
        notes_count = MentorNote.query.filter_by(
            mentor_id=current_user.id,
            student_id=student.id,
        ).count()

        mentees.append(
            {
                "student": student,
                "profile": profile,
                "target_job_role": target_job_role,
                "gap_percentage": gap_percentage,
                "at_risk": at_risk,
                "notes_count": notes_count,
                "latest_note": latest_note,
            }
        )

    # Mentor KPIs
    total_mentees = len(mentees)
    at_risk_count = sum(1 for m in mentees if m["at_risk"])
    ready_count = sum(
        1 for m in mentees if m["gap_percentage"] is not None and m["gap_percentage"] <= 30
    )
    gaps = [m["gap_percentage"] for m in mentees if m["gap_percentage"] is not None]
    average_gap = round(sum(gaps) / len(gaps), 1) if gaps else None

    kpis = {
        "total": total_mentees,
        "at_risk": at_risk_count,
        "ready": ready_count,
        "average_gap": average_gap,
    }

    return render_template(
        "mentor/dashboard.html",
        mentees=mentees,
        kpis=kpis,
    )


@mentor_bp.route("/mentee/<int:student_id>/note", methods=["GET", "POST"])
@login_required
@role_required("mentor")
def mentee_note(student_id):
    assignment = MentorAssignment.query.filter_by(
        mentor_id=current_user.id,
        student_id=student_id,
    ).first()

    if assignment is None:
        abort(403)

    student = assignment.student
    profile = StudentProfile.query.filter_by(user_id=student.id).first()
    target_job_role = profile.target_job_role if profile else None
    skills = target_job_role.skills if target_job_role else []

    if request.method == "POST":
        # Check if mentor is updating a verified skill assessment
        action = request.form.get("action")
        if action == "verify_skill":
            skill_id = request.form.get("skill_id", type=int)
            level = request.form.get("level", "")
            skill = db.session.get(Skill, skill_id)
            levels = ["not_started", "learning", "comfortable", "confident"]

            if skill and skill.job_role_id == profile.target_job_role_id and level in levels:
                verified_assessment = Assessment.query.filter_by(
                    student_id=student.id,
                    skill_id=skill.id,
                    source="mentor",
                ).first()
                if verified_assessment is None:
                    verified_assessment = Assessment(
                        student_id=student.id,
                        skill_id=skill.id,
                        source="mentor",
                    )
                    db.session.add(verified_assessment)
                verified_assessment.level = level
                verified_assessment.updated_at = datetime.now(timezone.utc)
                db.session.commit()
                flash(f"Verified assessment for {skill.name} recorded.", "success")
                return redirect(url_for("mentor.mentee_note", student_id=student.id))

        # Mentoring note submission
        note_text = request.form.get("note_text", "").strip()

        if not note_text:
            flash("Note text cannot be empty.", "error")
        else:
            note = MentorNote(
                mentor_id=current_user.id,
                student_id=student.id,
                note_text=note_text,
                created_at=datetime.now(timezone.utc),
                at_risk=request.form.get("at_risk") in {"on", "true", "1"},
            )
            db.session.add(note)
            db.session.commit()
            flash("Mentor note saved.", "success")
            return redirect(url_for("mentor.mentee_note", student_id=student.id))

    # Compute skill breakdown for mentee
    effective_level_by_skill = {}
    self_level_by_skill = {}
    mentor_level_by_skill = {}

    if skills:
        skill_ids = [s.id for s in skills]
        assessments = Assessment.query.filter(
            Assessment.student_id == student.id,
            Assessment.skill_id.in_(skill_ids),
        ).all()

        for a in assessments:
            if a.source == "self":
                self_level_by_skill[a.skill_id] = a.level
            elif a.source == "mentor":
                mentor_level_by_skill[a.skill_id] = a.level

            if a.skill_id not in effective_level_by_skill or a.source == "mentor":
                effective_level_by_skill[a.skill_id] = a.level

    gap_percentage = None
    if skills:
        not_confident_count = sum(
            effective_level_by_skill.get(skill.id, "not_started") != "confident"
            for skill in skills
        )
        gap_percentage = round((not_confident_count / len(skills)) * 100, 2)

    notes = MentorNote.query.filter_by(
        mentor_id=current_user.id,
        student_id=student.id,
    ).order_by(
        MentorNote.created_at.asc(),
        MentorNote.id.asc(),
    ).all()

    latest_note = notes[-1] if notes else None
    current_at_risk = latest_note.at_risk if latest_note else False

    return render_template(
        "mentor/mentee_note.html",
        student=student,
        profile=profile,
        target_job_role=target_job_role,
        skills=skills,
        effective_level_by_skill=effective_level_by_skill,
        self_level_by_skill=self_level_by_skill,
        mentor_level_by_skill=mentor_level_by_skill,
        gap_percentage=gap_percentage,
        notes=notes,
        current_at_risk=current_at_risk,
    )
