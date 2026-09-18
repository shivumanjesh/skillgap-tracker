import csv
from io import BytesIO, StringIO

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


def create_user(name, email, role, password="password"):
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def login(client, email, password="password"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def seed_test_ecosystem():
    student = create_user("Alice Student", "alice@example.com", "student")
    mentor = create_user("Bob Mentor", "bob@example.com", "mentor")
    other_mentor = create_user("Charlie Mentor", "charlie@example.com", "mentor")
    tpo = create_user("Diana TPO", "diana@example.com", "tpo")
    admin = create_user("Edward Admin", "edward@example.com", "admin")

    role = JobRole(name="Full-Stack Engineer")
    skills = [
        Skill(name="Python", job_role=role),
        Skill(name="SQL", job_role=role),
        Skill(name="React", job_role=role),
    ]
    db.session.add_all([role, *skills])
    db.session.flush()

    profile = StudentProfile(
        user_id=student.id,
        branch="Computer Science & Engineering",
        year=3,
        target_job_role_id=role.id,
    )
    db.session.add(profile)

    assignment = MentorAssignment(mentor_id=mentor.id, student_id=student.id)
    db.session.add(assignment)
    db.session.commit()

    return {
        "student": student,
        "mentor": mentor,
        "other_mentor": other_mentor,
        "tpo": tpo,
        "admin": admin,
        "role": role,
        "skills": skills,
    }


def test_landing_page_and_smart_redirects(client, app):
    # Guest visiting /
    response = client.get("/")
    assert response.status_code == 200
    assert b"SkillGap" in response.data
    assert b"Close the" in response.data

    data = seed_test_ecosystem()

    # Authenticated student visiting / redirects to student dashboard
    login(client, data["student"].email)
    res = client.get("/")
    assert res.status_code == 302
    assert "/student/dashboard" in res.headers["Location"]
    client.get("/logout")

    # Authenticated mentor visiting / redirects to mentor dashboard
    login(client, data["mentor"].email)
    res = client.get("/")
    assert res.status_code == 302
    assert "/mentor/dashboard" in res.headers["Location"]
    client.get("/logout")

    # Authenticated TPO visiting / redirects to tpo dashboard
    login(client, data["tpo"].email)
    res = client.get("/")
    assert res.status_code == 302
    assert "/tpo/dashboard" in res.headers["Location"]
    client.get("/logout")

    # Authenticated Admin visiting / redirects to admin trends
    login(client, data["admin"].email)
    res = client.get("/")
    assert res.status_code == 302
    assert "/admin/trends" in res.headers["Location"]
    client.get("/logout")


def test_custom_error_handlers(client, app):
    # 404 page
    res_404 = client.get("/non-existent-page-url")
    assert res_404.status_code == 404
    assert b"Page Not Found" in res_404.data

    data = seed_test_ecosystem()

    # 403 Forbidden page
    login(client, data["student"].email)
    res_403 = client.get("/admin/trends")
    assert res_403.status_code == 403
    assert b"Access Restricted" in res_403.data


def test_student_profile_update(client, app):
    data = seed_test_ecosystem()
    login(client, data["student"].email)

    # GET profile page
    res = client.get("/student/profile")
    assert res.status_code == 200
    assert b"Academic Profile" in res.data

    # POST valid update
    res = client.post(
        "/student/profile",
        data={
            "branch": "Information Science & Engineering",
            "year": "4",
        },
    )
    assert res.status_code == 302

    profile = StudentProfile.query.filter_by(user_id=data["student"].id).one()
    assert profile.branch == "Information Science & Engineering"
    assert profile.year == 4

    # POST invalid updates
    res_bad_year = client.post(
        "/student/profile",
        data={"branch": "CSE", "year": "10"},
    )
    assert res_bad_year.status_code == 400

    res_empty_branch = client.post(
        "/student/profile",
        data={"branch": "", "year": "2"},
    )
    assert res_empty_branch.status_code == 400


def test_student_batch_assessment(client, app):
    data = seed_test_ecosystem()
    skills = data["skills"]
    login(client, data["student"].email)

    res = client.post(
        "/student/assessment",
        data={
            "is_batch": "1",
            f"level_{skills[0].id}": "confident",
            f"level_{skills[1].id}": "comfortable",
            f"level_{skills[2].id}": "learning",
        },
    )
    assert res.status_code == 302

    # Verify updated assessments
    a0 = Assessment.query.filter_by(student_id=data["student"].id, skill_id=skills[0].id, source="self").one()
    a1 = Assessment.query.filter_by(student_id=data["student"].id, skill_id=skills[1].id, source="self").one()
    assert a0.level == "confident"
    assert a1.level == "comfortable"

    # Dashboard reflects 1 of 3 confident -> 66.67% gap
    dashboard = client.get("/student/dashboard")
    assert b"Skill Gap: 66.67%" in dashboard.data


def test_mentor_verified_assessment_override(client, app):
    data = seed_test_ecosystem()
    student = data["student"]
    mentor = data["mentor"]
    skills = data["skills"]

    # Student self-assesses all 3 as learning (100% gap)
    for skill in skills:
        db.session.add(Assessment(student_id=student.id, skill_id=skill.id, level="learning", source="self"))
    db.session.commit()

    # Mentor logs in and views mentee
    login(client, mentor.email)
    mentee_page = client.get(f"/mentor/mentee/{student.id}/note")
    assert mentee_page.status_code == 200

    # Mentor verifies skills[0] as confident
    res = client.post(
        f"/mentor/mentee/{student.id}/note",
        data={
            "action": "verify_skill",
            "skill_id": skills[0].id,
            "level": "confident",
        },
    )
    assert res.status_code == 302

    # Check that mentor assessment exists in DB
    verified_assessment = Assessment.query.filter_by(
        student_id=student.id,
        skill_id=skills[0].id,
        source="mentor",
    ).one()
    assert verified_assessment.level == "confident"

    # Now verify gap score recalculation: 1 confident of 3 -> 66.67% gap
    client.get("/logout")
    login(client, student.email)
    dash = client.get("/student/dashboard")
    assert b"Skill Gap: 66.67%" in dash.data



def test_tpo_at_risk_detection_and_exports(client, app):
    data = seed_test_ecosystem()
    student = data["student"]
    mentor = data["mentor"]
    tpo = data["tpo"]

    # Mentor logs at-risk note
    login(client, mentor.email)
    client.post(
        f"/mentor/mentee/{student.id}/note",
        data={"note_text": "Student struggling with core algorithms", "at_risk": "on"},
    )
    client.get("/logout")

    # TPO logs in
    login(client, tpo.email)
    dash = client.get("/tpo/dashboard")
    assert dash.status_code == 200
    assert b"At Risk" in dash.data
    assert b"Flagged Candidates for Early Intervention" in dash.data

    # Export at-risk CSV
    export_res = client.get("/tpo/export-at-risk")
    assert export_res.status_code == 200
    assert export_res.content_type.startswith("text/csv")
    reader = list(csv.reader(StringIO(export_res.get_data(as_text=True))))
    assert reader[0] == ["Student", "Email", "Branch", "Target Role", "Skill Gap", "Mentor", "Latest Review Note"]
    assert reader[1][0] == student.name
    assert reader[1][1] == student.email
    assert "algorithms" in reader[1][6]

    # Delete skill route
    role = data["role"]
    skill_to_delete = data["skills"][2]
    delete_res = client.post(f"/tpo/roles/{role.id}/skills/{skill_to_delete.id}/delete")
    assert delete_res.status_code == 302
    assert db.session.get(Skill, skill_to_delete.id) is None


def test_admin_bulk_csv_and_unassign(client, app):
    data = seed_test_ecosystem()
    admin = data["admin"]
    mentor = data["mentor"]

    # Create two unassigned students
    s1 = create_user("Student One", "s1@example.com", "student")
    s2 = create_user("Student Two", "s2@example.com", "student")
    db.session.commit()

    login(client, admin.email)

    # User directory
    users_page = client.get("/admin/users")
    assert users_page.status_code == 200
    assert b"Student One" in users_page.data

    # Upload bulk CSV
    csv_content = f"mentor_email,student_email\n{mentor.email},{s1.email}\n{mentor.email},{s2.email}\n"
    res = client.post(
        "/admin/bulk-assign-mentors",
        data={
            "csv_file": (BytesIO(csv_content.encode("utf-8")), "mentors.csv"),
        },
        content_type="multipart/form-data",
    )
    assert res.status_code == 302

    assert MentorAssignment.query.filter_by(mentor_id=mentor.id, student_id=s1.id).first() is not None
    assert MentorAssignment.query.filter_by(mentor_id=mentor.id, student_id=s2.id).first() is not None

    # Unassign mentor route
    unassign_res = client.post(f"/admin/unassign-mentor/{mentor.id}/{s1.id}")
    assert unassign_res.status_code == 302
    assert MentorAssignment.query.filter_by(mentor_id=mentor.id, student_id=s1.id).first() is None
