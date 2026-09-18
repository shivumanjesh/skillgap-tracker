import urllib.request
import urllib.parse
import http.cookiejar
import pytest

from app import create_app
from app.models import db, User, JobRole, Skill, StudentProfile, Assessment, MentorAssignment, MentorNote


class LiveSession:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))

    def get(self, path):
        req = urllib.request.Request(f"{self.base_url}{path}")
        try:
            with self.opener.open(req) as resp:
                return resp.getcode(), resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8")

    def post(self, path, data):
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(f"{self.base_url}{path}", data=encoded_data)
        try:
            with self.opener.open(req) as resp:
                return resp.getcode(), resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8")


def test_live_server_endpoints():
    session = LiveSession("http://127.0.0.1:5000")

    # 1. Verify Landing Page
    code, html = session.get("/")
    assert code == 200
    assert "Close the" in html
    assert "SkillGap" in html
    assert "It works" not in html
    assert "Student Portal" in html
    assert "Faculty Mentors" in html
    assert "Placement Officer" in html

    # 2. Verify Login Page
    code, html = session.get("/login")
    assert code == 200
    assert "Quick Demo Logins" in html
    assert "student@example.com" in html
    assert "mentor@example.com" in html
    assert "tpo@example.com" in html
    assert "admin@example.com" in html

    # 3. Student Workflow
    code, html = session.post("/login", {"email": "student@example.com", "password": "student123"})
    assert code == 200
    assert "Student Dashboard" in html
    assert "Skill Gap:" in html
    assert "Placement Readiness Index" in html
    assert "Required Skills Checklist" in html
    assert "studentProficiencyChart" in html

    # Student Profile
    code, html = session.get("/student/profile")
    assert code == 200
    assert "Academic Profile" in html
    assert "Computer Science" in html

    # Student Assessment Page
    code, html = session.get("/student/assessment")
    assert code == 200
    assert "Employability Proficiency Benchmark Scale" in html
    assert "Save All Proficiencies" in html

    # Student Logout
    code, html = session.get("/logout")
    assert code == 200

    # 4. Mentor Workflow
    code, html = session.post("/login", {"email": "mentor@example.com", "password": "mentor123"})
    assert code == 200
    assert "Faculty Mentorship" in html
    assert "Assigned Mentees" in html
    assert "Flagged At Risk" in html
    assert "Mentee Details" in html

    # Mentor Mentee Details
    code, html = session.get("/mentor/mentee/1/note")
    assert code == 200
    assert "Mentoring Observations &amp; Action Plan" in html
    assert "Skill Verification &amp; Annotations" in html

    # Mentor Logout
    session.get("/logout")

    # 5. TPO Workflow
    code, html = session.post("/login", {"email": "tpo@example.com", "password": "tpo123"})
    assert code == 200
    assert "Placement Readiness Cockpit" in html
    assert "Department &amp; Branch Readiness Breakdown" in html
    assert "Flagged Candidates for Early Intervention" in html
    assert "Export CSV" in html

    # TPO Roles
    code, html = session.get("/tpo/roles")
    assert code == 200
    assert "Career Tracks &amp; Job Roles" in html
    assert "Full-Stack Web Developer" in html

    # TPO Export CSV
    code, csv_data = session.get("/tpo/export")
    assert code == 200
    assert "Student,Email,Target Role,Skill Gap" in csv_data

    # TPO Export At-Risk CSV
    code, at_risk_csv = session.get("/tpo/export-at-risk")
    assert code == 200
    assert "Student,Email,Branch,Target Role,Skill Gap,Mentor,Latest Review Note" in at_risk_csv

    # TPO Logout
    session.get("/logout")

    # 6. Admin Workflow
    code, html = session.post("/login", {"email": "admin@example.com", "password": "admin123"})
    assert code == 200
    assert "Student Readiness &amp; Skill Trends" in html
    assert "Role-Wise Skill Gap Overview" in html
    assert "roleGapChart" in html

    # Admin Assign Mentors
    code, html = session.get("/admin/assign-mentors")
    assert code == 200
    assert "Manual Mentor-Student Pairing" in html
    assert "Bulk CSV Pairing Upload" in html

    # Admin Users
    code, html = session.get("/admin/users")
    assert code == 200
    assert "System User Directory" in html

    # 7. Security IDOR / Cross-Role Check (Admin visiting student dashboard -> 403)
    code, html = session.get("/student/dashboard")
    assert code == 403
    assert "Access Restricted" in html
    assert "Return to My Dashboard" in html

    # 404 Check
    code, html = session.get("/this-route-does-not-exist")
    assert code == 404
    assert "Page Not Found" in html

    session.get("/logout")
