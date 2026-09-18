import csv
import statistics
from io import StringIO

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import func

from app.ai_copilot import generate_ai_recruiter_pitch
from app.auth.routes import role_required
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

tpo_bp = Blueprint(
    "tpo",
    __name__,
    url_prefix="/tpo",
    template_folder="templates",
)


@tpo_bp.get("/")
def index():
    return redirect(url_for("tpo.dashboard"))


def _student_gap(student_id, profile):
    target_job_role = profile.target_job_role if profile else None
    skills = target_job_role.skills if target_job_role else []

    if not skills:
        return target_job_role, None

    skill_ids = [skill.id for skill in skills]
    effective_level_by_skill = {}
    assessments = Assessment.query.filter(
        Assessment.student_id == student_id,
        Assessment.skill_id.in_(skill_ids),
    ).all()

    for assessment in assessments:
        if (
            assessment.skill_id not in effective_level_by_skill
            or assessment.source == "mentor"
        ):
            effective_level_by_skill[assessment.skill_id] = assessment.level

    not_confident_count = sum(
        effective_level_by_skill.get(skill.id, "not_started") != "confident"
        for skill in skills
    )
    gap_percentage = round((not_confident_count / len(skills)) * 100, 2)
    return target_job_role, gap_percentage


def _student_rows():
    students = User.query.filter_by(role="student").order_by(User.name).all()
    student_rows = []

    for student in students:
        profile = StudentProfile.query.filter_by(user_id=student.id).first()
        target_job_role, gap_percentage = _student_gap(student.id, profile)

        # Retrieve mentor assignment
        assignment = MentorAssignment.query.filter_by(student_id=student.id).first()
        mentor = assignment.mentor if assignment else None

        # Determine at-risk status from latest mentor note
        latest_note = MentorNote.query.filter_by(
            student_id=student.id
        ).order_by(MentorNote.created_at.desc(), MentorNote.id.desc()).first()

        at_risk = latest_note.at_risk if latest_note else False

        student_rows.append(
            {
                "student": student,
                "profile": profile,
                "target_job_role": target_job_role,
                "gap_percentage": gap_percentage,
                "mentor": mentor,
                "at_risk": at_risk,
                "latest_note": latest_note,
            }
        )

    return student_rows


@tpo_bp.get("/dashboard")
@login_required
@role_required("tpo")
def dashboard():
    all_rows = _student_rows()

    # Filter params
    selected_role_id = request.args.get("role_id", type=int)
    selected_branch = request.args.get("branch", "").strip()
    status_filter = request.args.get("status", "").strip()
    search_query = request.args.get("q", "").strip().lower()

    filtered_rows = all_rows
    if selected_role_id:
        filtered_rows = [
            r for r in filtered_rows
            if r["target_job_role"] and r["target_job_role"].id == selected_role_id
        ]
    if selected_branch:
        filtered_rows = [
            r for r in filtered_rows
            if r["profile"] and r["profile"].branch == selected_branch
        ]
    if status_filter == "at_risk":
        filtered_rows = [r for r in filtered_rows if r["at_risk"]]
    elif status_filter == "ready":
        filtered_rows = [
            r for r in filtered_rows
            if r["gap_percentage"] is not None and r["gap_percentage"] <= 30
        ]
    if search_query:
        filtered_rows = [
            r for r in filtered_rows
            if search_query in r["student"].name.lower() or search_query in r["student"].email.lower()
        ]

    # Predictive Corporate Tier Segmentation
    # Tier-1: Readiness >= 80%
    # Tier-2: Readiness 60% - 79%
    # Tier-3: Readiness 40% - 59%
    # Remedial: Readiness < 40%
    tier_counts = {"tier1": 0, "tier2": 0, "tier3": 0, "remedial": 0}
    for r in all_rows:
        readiness = round(100 - (r["gap_percentage"] or 100), 1)
        r["readiness"] = readiness
        if readiness >= 80:
            r["hiring_tier"] = "Tier-1 Product (15+ LPA)"
            r["hiring_tier_short"] = "Tier 1"
            r["hiring_tier_badge"] = "success"
            tier_counts["tier1"] += 1
        elif readiness >= 60:
            r["hiring_tier"] = "Tier-2 Scaleup (8–15 LPA)"
            r["hiring_tier_short"] = "Tier 2"
            r["hiring_tier_badge"] = "primary"
            tier_counts["tier2"] += 1
        elif readiness >= 40:
            r["hiring_tier"] = "Tier-3 Services (4–8 LPA)"
            r["hiring_tier_short"] = "Tier 3"
            r["hiring_tier_badge"] = "warning"
            tier_counts["tier3"] += 1
        else:
            r["hiring_tier"] = "Remedial Intervention (<40%)"
            r["hiring_tier_short"] = "Remedial"
            r["hiring_tier_badge"] = "danger"
            tier_counts["remedial"] += 1

    selected_tier = request.args.get("tier", "").strip()
    if selected_tier:
        filtered_rows = [
            r for r in filtered_rows
            if r.get("hiring_tier_short") == selected_tier or r.get("hiring_tier") == selected_tier
        ]

    # Analytics computation
    total_students = len(all_rows)
    with_target_role = sum(1 for r in all_rows if r["target_job_role"] is not None)
    at_risk_rows = [r for r in all_rows if r["at_risk"]]
    at_risk_count = len(at_risk_rows)
    ready_count = sum(
        1 for r in all_rows
        if r["gap_percentage"] is not None and r["gap_percentage"] <= 30
    )

    valid_gaps = [r["gap_percentage"] for r in all_rows if r["gap_percentage"] is not None]
    average_gap = round(sum(valid_gaps) / len(valid_gaps), 1) if valid_gaps else None

    # Branch-wise statistics
    branch_map = {}
    for r in all_rows:
        branch_name = r["profile"].branch if (r["profile"] and r["profile"].branch) else "Not Specified"
        if branch_name not in branch_map:
            branch_map[branch_name] = {"students": 0, "gaps": [], "at_risk": 0}
        branch_map[branch_name]["students"] += 1
        if r["gap_percentage"] is not None:
            branch_map[branch_name]["gaps"].append(r["gap_percentage"])
        if r["at_risk"]:
            branch_map[branch_name]["at_risk"] += 1

    branch_stats = []
    for b_name, b_info in sorted(branch_map.items()):
        median_gap = (
            round(statistics.median(b_info["gaps"]), 1)
            if b_info["gaps"]
            else None
        )
        branch_stats.append({
            "name": b_name,
            "students": b_info["students"],
            "median_gap": median_gap,
            "at_risk": b_info["at_risk"],
        })

    # Available roles and branches for filters
    job_roles = JobRole.query.order_by(JobRole.name).all()
    available_branches = sorted(
        list({r["profile"].branch for r in all_rows if r["profile"] and r["profile"].branch})
    )

    kpis = {
        "total_students": total_students,
        "with_target_role": with_target_role,
        "at_risk_count": at_risk_count,
        "ready_count": ready_count,
        "average_gap": average_gap,
        "role_count": len(job_roles),
    }

    ai_recruiter_pitch = generate_ai_recruiter_pitch(
        total_students=total_students,
        ready_count=ready_count,
        avg_gap=average_gap or 0,
        branch_data=branch_stats,
        tier_counts=tier_counts,
    )

    return render_template(
        "tpo/dashboard.html",
        student_rows=filtered_rows,
        all_rows=all_rows,
        at_risk_rows=at_risk_rows,
        branch_stats=branch_stats,
        kpis=kpis,
        job_roles=job_roles,
        available_branches=available_branches,
        selected_role_id=selected_role_id,
        selected_branch=selected_branch,
        selected_tier=selected_tier,
        status_filter=status_filter,
        search_query=search_query,
        tier_counts=tier_counts,
        ai_recruiter_pitch=ai_recruiter_pitch,
    )


@tpo_bp.get("/export")
@login_required
@role_required("tpo")
def export_csv():
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Student", "Email", "Target Role", "Skill Gap"])

    for row in _student_rows():
        if row["gap_percentage"] is not None:
            skill_gap = f"{row['gap_percentage']:g}%"
        elif row["target_job_role"] is not None:
            skill_gap = "Undefined (no required skills)"
        else:
            skill_gap = "Undefined (no target role)"

        writer.writerow(
            [
                row["student"].name,
                row["student"].email,
                row["target_job_role"].name
                if row["target_job_role"] is not None
                else "",
                skill_gap,
            ]
        )

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=employability_readiness.csv"
        },
    )


@tpo_bp.get("/export-at-risk")
@login_required
@role_required("tpo")
def export_at_risk_csv():
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Student", "Email", "Branch", "Target Role", "Skill Gap", "Mentor", "Latest Review Note"])

    for row in _student_rows():
        if not row["at_risk"]:
            continue

        skill_gap = f"{row['gap_percentage']:g}%" if row["gap_percentage"] is not None else "Undefined"
        branch = row["profile"].branch if row["profile"] else ""
        role_name = row["target_job_role"].name if row["target_job_role"] else ""
        mentor_name = row["mentor"].name if row["mentor"] else "Unassigned"
        note_text = row["latest_note"].note_text if row["latest_note"] else ""

        writer.writerow([
            row["student"].name,
            row["student"].email,
            branch,
            role_name,
            skill_gap,
            mentor_name,
            note_text,
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=at_risk_students.csv"
        },
    )


@tpo_bp.route("/roles", methods=["GET", "POST"])
@login_required
@role_required("tpo")
def roles():
    if request.method == "POST":
        role_name = request.form.get("name", "").strip()

        if not role_name:
            flash("Role name cannot be empty.", "error")
            return render_template("tpo/roles.html", roles=JobRole.query.all()), 400

        existing_role = JobRole.query.filter(
            func.lower(JobRole.name) == role_name.lower()
        ).first()
        if existing_role is not None:
            flash("A job role with that name already exists.", "error")
            return render_template("tpo/roles.html", roles=JobRole.query.all()), 400

        db.session.add(JobRole(name=role_name))
        db.session.commit()
        flash("Job role created successfully.", "success")
        return redirect(url_for("tpo.roles"))

    return render_template(
        "tpo/roles.html",
        roles=JobRole.query.order_by(JobRole.name).all(),
    )


@tpo_bp.route("/roles/<int:role_id>/skills", methods=["GET", "POST"])
@login_required
@role_required("tpo")
def role_skills(role_id):
    role = db.session.get(JobRole, role_id)
    if role is None:
        abort(404)

    if request.method == "POST":
        skill_name = request.form.get("name", "").strip()

        if not skill_name:
            flash("Skill name cannot be empty.", "error")
            return (
                render_template("tpo/role_skills.html", role=role),
                400,
            )

        existing_skill = Skill.query.filter(
            Skill.job_role_id == role.id,
            func.lower(Skill.name) == skill_name.lower(),
        ).first()
        if existing_skill is not None:
            flash("That skill already exists for this job role.", "error")
            return (
                render_template("tpo/role_skills.html", role=role),
                400,
            )

        db.session.add(Skill(name=skill_name, job_role_id=role.id))
        db.session.commit()
        flash("Skill added.", "success")
        return redirect(url_for("tpo.role_skills", role_id=role.id))

    return render_template("tpo/role_skills.html", role=role)


@tpo_bp.post("/roles/<int:role_id>/skills/<int:skill_id>/delete")
@login_required
@role_required("tpo")
def delete_skill(role_id, skill_id):
    role = db.session.get(JobRole, role_id)
    if role is None:
        abort(404)

    skill = db.session.get(Skill, skill_id)
    if skill is None or skill.job_role_id != role.id:
        abort(404)

    db.session.delete(skill)
    db.session.commit()
    flash(f"Skill '{skill.name}' deleted successfully.", "success")
    return redirect(url_for("tpo.role_skills", role_id=role.id))
