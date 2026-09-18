import csv
from io import StringIO

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


def seed_accounts():
    return {
        "student": create_user("Student", "student@example.com", "student"),
        "mentor": create_user("Mentor", "mentor@example.com", "mentor"),
        "other_mentor": create_user("Other Mentor", "other@example.com", "mentor"),
        "tpo": create_user("TPO", "tpo@example.com", "tpo"),
        "admin": create_user("Admin", "admin@example.com", "admin"),
    }


def test_student_workflow_and_cross_role_protection(client, app):
    accounts = seed_accounts()
    role = JobRole(name="Backend Developer")
    skills = [Skill(name=name, job_role=role) for name in ["Python", "SQL", "DSA"]]
    db.session.add_all([role, *skills])
    db.session.flush()
    db.session.add(
        StudentProfile(
            user_id=accounts["student"].id,
            branch="CS",
            year=3,
            target_job_role_id=role.id,
        )
    )
    db.session.commit()

    assert login(client, "student@example.com").status_code == 302
    assert client.get("/student/dashboard").status_code == 200
    assert client.get("/student/target-role").status_code == 200
    assert client.get("/student/assessment").status_code == 200
    assert client.post(
        "/student/assessment",
        data={"skill_id": skills[0].id, "level": "confident"},
    ).status_code == 302
    assert b"Skill Gap: 66.67%" in client.get("/student/dashboard").data
    assert client.get("/mentor/dashboard").status_code == 403
    assert client.get("/tpo/roles").status_code == 403
    assert client.get("/admin/trends").status_code == 403

    client.get("/logout")
    assert client.get("/student/dashboard").status_code == 302


def test_mentor_assignment_notes_and_idor_protection(client, app):
    accounts = seed_accounts()
    db.session.add(
        MentorAssignment(
            mentor_id=accounts["mentor"].id,
            student_id=accounts["student"].id,
        )
    )
    db.session.commit()

    assert login(client, "mentor@example.com").status_code == 302
    assert client.get("/mentor/dashboard").status_code == 200
    note_response = client.post(
        f"/mentor/mentee/{accounts['student'].id}/note",
        data={"note_text": "Review progress", "at_risk": "on"},
    )
    assert note_response.status_code == 302
    note = MentorNote.query.one()
    assert note.mentor_id == accounts["mentor"].id
    assert note.student_id == accounts["student"].id
    assert note.at_risk is True
    assert b"Review progress" in client.get(
        f"/mentor/mentee/{accounts['student'].id}/note"
    ).data
    assert client.post(
        f"/mentor/mentee/{accounts['student'].id}/note",
        data={"note_text": "   "},
    ).status_code == 200
    assert MentorNote.query.count() == 1
    client.get("/logout")

    login(client, "other@example.com")
    assert client.get(
        f"/mentor/mentee/{accounts['student'].id}/note"
    ).status_code == 403


def test_tpo_management_dashboard_and_csv(client, app):
    accounts = seed_accounts()
    assert login(client, "tpo@example.com").status_code == 302
    assert client.post("/tpo/roles", data={"name": "Data Analyst"}).status_code == 302
    role = JobRole.query.filter_by(name="Data Analyst").one()
    assert client.post(
        f"/tpo/roles/{role.id}/skills", data={"name": "SQL"}
    ).status_code == 302
    skill = Skill.query.filter_by(job_role_id=role.id, name="SQL").one()
    assert skill.job_role_id == role.id
    assert client.post("/tpo/roles", data={"name": " data analyst "}).status_code == 400
    assert client.post(
        f"/tpo/roles/{role.id}/skills", data={"name": " sql "}
    ).status_code == 400
    assert client.get(f"/tpo/roles/999999/skills").status_code == 404

    db.session.add(
        StudentProfile(
            user_id=accounts["student"].id,
            branch="CS",
            year=3,
            target_job_role_id=role.id,
        )
    )
    db.session.commit()
    dashboard = client.get("/tpo/dashboard")
    export = client.get("/tpo/export")
    rows = list(csv.reader(StringIO(export.get_data(as_text=True))))
    assert dashboard.status_code == 200
    assert export.content_type.startswith("text/csv")
    assert rows[0] == ["Student", "Email", "Target Role", "Skill Gap"]
    assert rows[1][1] == "student@example.com"
    assert rows[1][2] == "Data Analyst"
    assert rows[1][3] == "100%"

    client.get("/logout")
    for email, role_name in [
        ("student@example.com", "student"),
        ("mentor@example.com", "mentor"),
        ("admin@example.com", "admin"),
    ]:
        login(client, email)
        assert client.get("/tpo/dashboard").status_code == 403
        client.get("/logout")


def test_admin_bulk_assignment_and_trends(client, app):
    accounts = seed_accounts()
    assert login(client, "admin@example.com").status_code == 302
    assert client.get("/admin/trends").status_code == 200
    assert client.get("/admin/assign-mentors").status_code == 200

    response = client.post(
        "/admin/assign-mentors",
        data={
            "mentor_id": accounts["mentor"].id,
            "student_ids": [accounts["student"].id],
        },
    )
    assert response.status_code == 302
    assert MentorAssignment.query.count() == 1
    assert client.post(
        "/admin/assign-mentors",
        data={
            "mentor_id": accounts["mentor"].id,
            "student_ids": [accounts["student"].id],
        },
    ).status_code == 302
    assert MentorAssignment.query.count() == 1
    assert client.post(
        "/admin/assign-mentors",
        data={"mentor_id": accounts["student"].id, "student_ids": [accounts["student"].id]},
    ).status_code == 400
    assert client.post(
        "/admin/assign-mentors",
        data={"mentor_id": accounts["mentor"].id},
    ).status_code == 400

    client.get("/logout")
    login(client, "mentor@example.com")
    assert b"Student" in client.get("/mentor/dashboard").data


def test_gap_edge_cases_are_safe(app, client):
    accounts = seed_accounts()
    role = JobRole(name="Empty Role")
    db.session.add(role)
    db.session.flush()
    db.session.add(
        StudentProfile(
            user_id=accounts["student"].id,
            branch="CS",
            year=3,
            target_job_role_id=role.id,
        )
    )
    db.session.commit()
    login(client, "student@example.com")
    response = client.get("/student/dashboard")
    assert response.status_code == 200
    assert b"no required skills" in response.data.lower()
    assert b"Skill Gap: 0%" not in response.data


def test_protected_route_matrix(client, app):
    accounts = seed_accounts()
    role = JobRole(name="Protected Role")
    skill = Skill(name="Protected Skill", job_role=role)
    db.session.add_all([role, skill])
    db.session.flush()
    db.session.add(
        StudentProfile(
            user_id=accounts["student"].id,
            branch="CS",
            year=3,
            target_job_role_id=role.id,
        )
    )
    db.session.add(
        MentorAssignment(
            mentor_id=accounts["mentor"].id,
            student_id=accounts["student"].id,
        )
    )
    db.session.commit()

    protected_paths = [
        "/student/dashboard",
        "/student/target-role",
        "/student/assessment",
        "/mentor/dashboard",
        f"/mentor/mentee/{accounts['student'].id}/note",
        "/tpo/dashboard",
        "/tpo/roles",
        f"/tpo/roles/{role.id}/skills",
        "/tpo/export",
        "/admin/trends",
        "/admin/assign-mentors",
    ]

    for path in protected_paths:
        assert client.get(path).status_code == 302

    allowed_paths = {
        "student": protected_paths[:3],
        "mentor": protected_paths[3:5],
        "tpo": protected_paths[5:9],
        "admin": protected_paths[9:],
    }
    for role_name, expected_paths in allowed_paths.items():
        login(client, accounts[role_name].email)
        for path in protected_paths:
            expected_status = 200 if path in expected_paths else 403
            assert client.get(path).status_code == expected_status
        client.get("/logout")