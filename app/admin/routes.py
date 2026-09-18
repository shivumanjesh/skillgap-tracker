import csv
from collections import defaultdict
from io import StringIO

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.ai_copilot import generate_ai_curriculum_analysis
from app.auth.routes import role_required
from app.models import Assessment, MentorAssignment, StudentProfile, User, db

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
)


@admin_bp.get("/")
def index():
    return redirect(url_for("admin.trends"))


@admin_bp.route("/assign-mentors", methods=["GET", "POST"])
@login_required
@role_required("admin")
def assign_mentors():
    mentors = User.query.filter_by(role="mentor").order_by(User.name).all()
    students = User.query.filter_by(role="student").order_by(User.name).all()

    if request.method == "POST":
        mentor_id = request.form.get("mentor_id", type=int)
        raw_student_ids = request.form.getlist("student_ids")

        try:
            student_ids = list(
                dict.fromkeys(int(value) for value in raw_student_ids)
            )
        except (TypeError, ValueError):
            flash("Student selection contains an invalid ID.", "error")
            return render_template(
                "admin/assign_mentors.html",
                mentors=mentors,
                students=students,
                assignment_pairs=set(),
            ), 400

        mentor = db.session.get(User, mentor_id) if mentor_id else None
        if mentor is None or mentor.role != "mentor":
            flash("Please select a valid mentor.", "error")
            return render_template(
                "admin/assign_mentors.html",
                mentors=mentors,
                students=students,
                assignment_pairs=set(),
            ), 400

        if not student_ids:
            flash("Select at least one student.", "error")
            return render_template(
                "admin/assign_mentors.html",
                mentors=mentors,
                students=students,
                assignment_pairs=set(),
            ), 400

        selected_students = User.query.filter(User.id.in_(student_ids)).all()
        students_by_id = {student.id: student for student in selected_students}
        if len(students_by_id) != len(student_ids) or any(
            students_by_id[student_id].role != "student"
            for student_id in student_ids
            if student_id in students_by_id
        ):
            flash("Every selected user must be a valid student.", "error")
            return render_template(
                "admin/assign_mentors.html",
                mentors=mentors,
                students=students,
                assignment_pairs=set(),
            ), 400

        existing_assignments = {
            assignment.student_id
            for assignment in MentorAssignment.query.filter_by(
                mentor_id=mentor.id,
            ).filter(MentorAssignment.student_id.in_(student_ids)).all()
        }
        new_assignments = [
            MentorAssignment(mentor_id=mentor.id, student_id=student_id)
            for student_id in student_ids
            if student_id not in existing_assignments
        ]

        if new_assignments:
            db.session.add_all(new_assignments)
            db.session.commit()
            flash(
                f"Assigned {len(new_assignments)} student(s) to {mentor.name}.",
                "success",
            )
        else:
            flash(
                "All selected students are already assigned to that mentor.",
                "info",
            )

        return redirect(url_for("admin.assign_mentors"))

    all_assignments = MentorAssignment.query.all()
    assignment_pairs = {
        (assignment.mentor_id, assignment.student_id)
        for assignment in all_assignments
    }

    # Assigned students set for quick filtering
    assigned_student_ids = {assignment.student_id for assignment in all_assignments}

    return render_template(
        "admin/assign_mentors.html",
        mentors=mentors,
        students=students,
        assignment_pairs=assignment_pairs,
        assigned_student_ids=assigned_student_ids,
        all_assignments=all_assignments,
    )


@admin_bp.post("/bulk-assign-mentors")
@login_required
@role_required("admin")
def bulk_assign_mentors():
    file = request.files.get("csv_file")
    if not file or file.filename == "":
        flash("Please select a CSV file to upload.", "error")
        return redirect(url_for("admin.assign_mentors"))

    try:
        content = file.stream.read().decode("utf-8")
        reader = csv.reader(StringIO(content))
        rows = list(reader)
    except Exception as e:
        flash(f"Failed to read CSV file: {str(e)}", "error")
        return redirect(url_for("admin.assign_mentors"))

    if not rows:
        flash("The uploaded CSV file is empty.", "error")
        return redirect(url_for("admin.assign_mentors"))

    # Skip header if present
    start_index = 0
    header = [col.strip().lower() for col in rows[0]]
    if "mentor" in header[0] or "mentor_email" in header[0]:
        start_index = 1

    success_count = 0
    skipped_count = 0
    errors = []

    for idx, row in enumerate(rows[start_index:], start=start_index + 1):
        if not row or len(row) < 2:
            continue
        mentor_email = row[0].strip().lower()
        student_email = row[1].strip().lower()

        if not mentor_email or not student_email:
            continue

        mentor = User.query.filter_by(email=mentor_email, role="mentor").first()
        student = User.query.filter_by(email=student_email, role="student").first()

        if not mentor:
            errors.append(f"Row {idx}: Mentor with email '{mentor_email}' not found.")
            continue
        if not student:
            errors.append(f"Row {idx}: Student with email '{student_email}' not found.")
            continue

        existing = MentorAssignment.query.filter_by(
            mentor_id=mentor.id,
            student_id=student.id,
        ).first()

        if existing:
            skipped_count += 1
            continue

        db.session.add(MentorAssignment(mentor_id=mentor.id, student_id=student.id))
        success_count += 1

    if success_count > 0:
        db.session.commit()
        flash(f"Successfully processed CSV: {success_count} new assignment(s) created.", "success")
    if skipped_count > 0:
        flash(f"{skipped_count} assignment(s) already existed and were skipped.", "info")
    if errors:
        for err in errors[:5]:
            flash(err, "error")
        if len(errors) > 5:
            flash(f"...and {len(errors) - 5} more row errors.", "error")

    return redirect(url_for("admin.assign_mentors"))


@admin_bp.post("/unassign-mentor/<int:mentor_id>/<int:student_id>")
@login_required
@role_required("admin")
def unassign_mentor(mentor_id, student_id):
    assignment = MentorAssignment.query.filter_by(
        mentor_id=mentor_id,
        student_id=student_id,
    ).first()

    if assignment:
        db.session.delete(assignment)
        db.session.commit()
        flash("Mentor assignment removed successfully.", "success")
    else:
        flash("Assignment record not found.", "error")

    return redirect(url_for("admin.assign_mentors"))


def _student_gap_data(student, profile):
    target_job_role = profile.target_job_role if profile else None
    skills = target_job_role.skills if target_job_role else []
    effective_levels = {}

    if skills:
        skill_ids = [skill.id for skill in skills]
        assessments = Assessment.query.filter(
            Assessment.student_id == student.id,
            Assessment.skill_id.in_(skill_ids),
        ).all()
        for assessment in assessments:
            if (
                assessment.skill_id not in effective_levels
                or assessment.source == "mentor"
            ):
                effective_levels[assessment.skill_id] = assessment.level

    gap_percentage = None
    if skills:
        not_confident_count = sum(
            effective_levels.get(skill.id, "not_started") != "confident"
            for skill in skills
        )
        gap_percentage = round((not_confident_count / len(skills)) * 100, 2)

    return target_job_role, skills, effective_levels, gap_percentage


@admin_bp.get("/trends")
@login_required
@role_required("admin")
def trends():
    students = User.query.filter_by(role="student").order_by(User.name).all()
    student_rows = []
    role_data = defaultdict(lambda: {"name": "", "student_count": 0, "gaps": []})
    skill_data = defaultdict(
        lambda: {
            "not_started": 0,
            "learning": 0,
            "comfortable": 0,
            "confident": 0,
        }
    )

    for student in students:
        profile = StudentProfile.query.filter_by(user_id=student.id).first()
        target_job_role, skills, effective_levels, gap_percentage = (
            _student_gap_data(student, profile)
        )
        student_rows.append(
            {
                "student": student,
                "target_job_role": target_job_role,
                "gap_percentage": gap_percentage,
            }
        )

        if target_job_role is None:
            continue

        role_entry = role_data[target_job_role.id]
        role_entry["name"] = target_job_role.name
        role_entry["student_count"] += 1
        if gap_percentage is not None:
            role_entry["gaps"].append(gap_percentage)

        for skill in skills:
            level = effective_levels.get(skill.id, "not_started")
            skill_data[(skill.id, skill.name)][level] += 1

    role_rows = [
        {
            "name": values["name"],
            "student_count": values["student_count"],
            "average_gap": round(sum(values["gaps"]) / len(values["gaps"]), 2)
            if values["gaps"]
            else None,
        }
        for values in sorted(role_data.values(), key=lambda item: item["name"])
    ]
    skill_rows = [
        {"name": skill_name, **counts}
        for (_, skill_name), counts in sorted(skill_data.items(), key=lambda item: item[0][1])
    ]

    student_overview = {
        "total": len(students),
        "with_target_role": sum(
            row["target_job_role"] is not None for row in student_rows
        ),
        "without_target_role": sum(
            row["target_job_role"] is None for row in student_rows
        ),
        "mentor_count": User.query.filter_by(role="mentor").count(),
        "total_assignments": MentorAssignment.query.count(),
    }

    ai_curriculum_plan = generate_ai_curriculum_analysis(role_rows)

    return render_template(
        "admin/trends.html",
        student_overview=student_overview,
        role_rows=role_rows,
        skill_rows=skill_rows,
        ai_curriculum_plan=ai_curriculum_plan,
    )


@admin_bp.get("/users")
@login_required
@role_required("admin")
def users():
    role_filter = request.args.get("role", "").strip().lower()
    query = User.query.order_by(User.role, User.name)
    if role_filter in ["student", "mentor", "tpo", "admin"]:
        query = query.filter_by(role=role_filter)
    all_users = query.all()

    counts = {
        "all": User.query.count(),
        "student": User.query.filter_by(role="student").count(),
        "mentor": User.query.filter_by(role="mentor").count(),
        "tpo": User.query.filter_by(role="tpo").count(),
        "admin": User.query.filter_by(role="admin").count(),
    }

    return render_template(
        "admin/users.html",
        users=all_users,
        counts=counts,
        active_role=role_filter,
    )
