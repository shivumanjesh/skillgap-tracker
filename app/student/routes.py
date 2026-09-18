from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.ai_copilot import (
    generate_interview_questions,
    generate_resume_bullets,
    generate_student_roadmap,
    get_student_roadmap_data,
)
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

student_bp = Blueprint(
    "student",
    __name__,
    url_prefix="/student",
    template_folder="templates",
)


@student_bp.get("/")
def index():
    return redirect(url_for("student.dashboard"))


@student_bp.get("/dashboard")
@login_required
@role_required("student")
def dashboard():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    target_job_role = profile.target_job_role if profile else None
    skills = target_job_role.skills if target_job_role else []

    effective_level_by_skill = {}
    proficiency_by_skill = {}
    level_counts = {
        "confident": 0,
        "comfortable": 0,
        "learning": 0,
        "not_started": 0,
    }

    if skills:
        skill_ids = [skill.id for skill in skills]
        assessments = Assessment.query.filter(
            Assessment.student_id == current_user.id,
            Assessment.skill_id.in_(skill_ids),
        ).all()

        for assessment in assessments:
            if (
                assessment.skill_id not in effective_level_by_skill
                or assessment.source == "mentor"
            ):
                effective_level_by_skill[assessment.skill_id] = assessment.level

        proficiency_by_skill = {
            skill_id: level.replace("_", " ").title()
            for skill_id, level in effective_level_by_skill.items()
        }

        for skill in skills:
            lvl = effective_level_by_skill.get(skill.id, "not_started")
            level_counts[lvl] = level_counts.get(lvl, 0) + 1

    gap_percentage = None
    if skills:
        not_confident_count = sum(
            effective_level_by_skill.get(skill.id, "not_started") != "confident"
            for skill in skills
        )
        gap_percentage = round((not_confident_count / len(skills)) * 100, 2)

    # Priority Skills (skills needing improvement)
    priority_order = {"not_started": 1, "learning": 2, "comfortable": 3}
    priority_skills = []
    if skills:
        for skill in skills:
            lvl = effective_level_by_skill.get(skill.id, "not_started")
            if lvl != "confident":
                priority_skills.append({
                    "skill": skill,
                    "level": lvl,
                    "level_title": lvl.replace("_", " ").title(),
                    "priority": priority_order.get(lvl, 99),
                })
        priority_skills.sort(key=lambda x: x["priority"])

    # Mentor info and feedback
    assignment = MentorAssignment.query.filter_by(student_id=current_user.id).first()
    mentor = assignment.mentor if assignment else None
    mentor_notes = MentorNote.query.filter_by(
        student_id=current_user.id
    ).order_by(MentorNote.created_at.desc()).all()

    # AI Career Copilot Data
    target_role_name = target_job_role.name if target_job_role else "Software Engineering"
    deficit_skills_list = [
        (item["skill"].name, item["level"])
        for item in priority_skills
    ]
    roadmap_md = generate_student_roadmap(current_user.name, target_role_name, deficit_skills_list)
    roadmap_weeks = get_student_roadmap_data(current_user.name, target_role_name, deficit_skills_list)
    interview_questions = generate_interview_questions(target_role_name)
    resume_bullets = generate_resume_bullets(target_role_name, skills, effective_level_by_skill)

    return render_template(
        "student/dashboard.html",
        profile=profile,
        target_job_role=target_job_role,
        skills=skills,
        proficiency_by_skill=proficiency_by_skill,
        gap_percentage=gap_percentage,
        level_counts=level_counts,
        priority_skills=priority_skills,
        mentor=mentor,
        mentor_notes=mentor_notes,
        roadmap_md=roadmap_md,
        roadmap_weeks=roadmap_weeks,
        interview_questions=interview_questions,
        resume_bullets=resume_bullets,
    )


@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("student")
def profile():
    prof = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if prof is None:
        prof = StudentProfile(
            user_id=current_user.id,
            branch="Not specified",
            year=0,
        )
        db.session.add(prof)
        db.session.commit()

    if request.method == "POST":
        branch = request.form.get("branch", "").strip()
        year = request.form.get("year", type=int)

        if not branch:
            flash("Please provide your academic branch / department.", "error")
            return render_template("student/profile.html", profile=prof), 400

        if year is None or year < 1 or year > 4:
            flash("Please select a valid academic year (1 to 4).", "error")
            return render_template("student/profile.html", profile=prof), 400

        prof.branch = branch
        prof.year = year
        db.session.commit()
        flash("Academic profile updated successfully.", "success")
        return redirect(url_for("student.dashboard"))

    return render_template("student/profile.html", profile=prof)


@student_bp.route("/target-role", methods=["GET", "POST"])
@login_required
@role_required("student")
def target_role():
    job_roles = JobRole.query.order_by(JobRole.name).all()
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        selected_role_id = request.form.get("job_role_id", type=int)
        selected_role = db.session.get(JobRole, selected_role_id)

        if selected_role is None:
            flash("Please select a valid target job role.", "error")
            return (
                render_template(
                    "student/target_role.html",
                    job_roles=job_roles,
                    selected_role_id=None,
                ),
                400,
            )

        if profile is None:
            profile = StudentProfile(
                user_id=current_user.id,
                branch="Not specified",
                year=0,
            )
            db.session.add(profile)

        profile.target_job_role_id = selected_role.id
        db.session.commit()
        flash("Target job role updated.", "success")
        return redirect(url_for("student.dashboard"))

    return render_template(
        "student/target_role.html",
        job_roles=job_roles,
        selected_role_id=profile.target_job_role_id if profile else None,
    )


@student_bp.route("/assessment", methods=["GET", "POST"])
@login_required
@role_required("student")
def assessment():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()

    if profile is None or profile.target_job_role_id is None:
        flash("Select a target job role before updating assessments.", "error")
        return redirect(url_for("student.target_role"))

    skills = Skill.query.filter_by(job_role_id=profile.target_job_role_id).all()
    proficiency_by_skill = {
        item.skill_id: item.level
        for item in Assessment.query.filter_by(
            student_id=current_user.id,
            source="self",
        ).all()
        if item.skill_id in {skill.id for skill in skills}
    }
    levels = ["not_started", "learning", "comfortable", "confident"]

    if request.method == "POST":
        is_batch = request.form.get("is_batch") == "1"

        if is_batch:
            # Batch update all skills
            updated_count = 0
            for skill in skills:
                submitted_level = request.form.get(f"level_{skill.id}", "")
                if submitted_level in levels:
                    existing = Assessment.query.filter_by(
                        student_id=current_user.id,
                        skill_id=skill.id,
                        source="self",
                    ).first()
                    if existing is None:
                        existing = Assessment(
                            student_id=current_user.id,
                            skill_id=skill.id,
                            source="self",
                        )
                        db.session.add(existing)
                    existing.level = submitted_level
                    existing.updated_at = datetime.now(timezone.utc)
                    updated_count += 1

            db.session.commit()
            flash(f"Updated proficiencies for {updated_count} skills.", "success")
            return redirect(url_for("student.dashboard"))

        # Single skill update (backward compatibility)
        skill_id = request.form.get("skill_id", type=int)
        level = request.form.get("level", "")
        skill = db.session.get(Skill, skill_id)

        if skill is None or skill.job_role_id != profile.target_job_role_id:
            flash("That skill is not part of your selected target role.", "error")
            return (
                render_template(
                    "student/assessment.html",
                    skills=skills,
                    levels=levels,
                    proficiency_by_skill=proficiency_by_skill,
                ),
                400,
            )

        if level not in levels:
            flash("Please select a valid proficiency level.", "error")
            return (
                render_template(
                    "student/assessment.html",
                    skills=skills,
                    levels=levels,
                    proficiency_by_skill=proficiency_by_skill,
                ),
                400,
            )

        existing_assessment = Assessment.query.filter_by(
            student_id=current_user.id,
            skill_id=skill.id,
            source="self",
        ).first()

        if existing_assessment is None:
            existing_assessment = Assessment(
                student_id=current_user.id,
                skill_id=skill.id,
                source="self",
            )
            db.session.add(existing_assessment)

        existing_assessment.level = level
        existing_assessment.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash(f"Updated proficiency for {skill.name}.", "success")
        return redirect(url_for("student.dashboard"))

    return render_template(
        "student/assessment.html",
        skills=skills,
        levels=levels,
        proficiency_by_skill=proficiency_by_skill,
    )
