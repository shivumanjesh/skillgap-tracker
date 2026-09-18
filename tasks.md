# Task Breakdown: Skill-Gap & Employability Readiness Tracker

Each task is scoped to be handed to Qwen2.5-Coder-7B-Instruct as a single,
self-contained prompt. Do them in order — later tasks depend on earlier ones.
After each task: run it, check it works, THEN move to the next one.

---

## Phase 0 — Project Skeleton

**Task 0.1** — Create the Flask app factory and directory structure from
plan.md (`app/__init__.py`, `config.py`, `run.py`, empty blueprint folders).
_Acceptance:_ `python run.py` starts a server with no errors, shows a blank
"It works" page at `/`.

**Task 0.2** — Set up `requirements.txt` with Flask, Flask-SQLAlchemy,
Flask-Login, and create the SQLite database file via a small init script.
_Acceptance:_ Running the init script creates `app.db` with no errors.

---

## Phase 1 — Data Model

**Task 1.1** — Implement `app/models.py` with the `User` model only
(id, name, email, password_hash, role). Include a method to set/check password.
_Acceptance:_ Can create a User row via a Python shell and verify the
password check works.

**Task 1.2** — Add `JobRole` and `Skill` models to `models.py`, with the
relationship (a Skill belongs to a JobRole).
_Acceptance:_ Can create a JobRole and attach 3 Skills to it via shell.

**Task 1.3** — Add `StudentProfile`, `Assessment`, `MentorAssignment`, and
`MentorNote` models per the schema in plan.md section 4.
_Acceptance:_ Can create one row of each and query relationships (e.g., get
all Assessments for a student).

---

## Phase 2 — Auth

**Task 2.1** — Implement the auth blueprint: `/login`, `/logout` routes
using Flask-Login, with a simple login form template.
_Acceptance:_ Can log in as a seeded test user and see a logged-in session;
logout clears the session.

**Task 2.2** — Add a `role_required(role)` decorator that blocks access to a
route unless the logged-in user has the given role, returning a 403 or
redirect otherwise.
_Acceptance:_ A student user hitting a `role_required('tpo')` route is denied.

**Task 2.3** — Write a seed script that creates one test user per role
(student, mentor, tpo, admin) with known credentials, for manual testing.
_Acceptance:_ Running the seed script lets you log in as each of the 4 roles.

---

## Phase 3 — Student Module

**Task 3.1** — Student dashboard route: shows the student's target job role
(or a prompt to pick one if unset) and their current skill list with
proficiency dropdowns.
_Acceptance:_ Logging in as the seeded student shows the dashboard with no
target role selected initially.

**Task 3.2** — Route to let the student select a target job role from a
list, saving it to their StudentProfile.
_Acceptance:_ Selecting a role persists after logout/login.

**Task 3.3** — Route to let the student update their self-reported
proficiency per skill (creates/updates an Assessment row with source=self).
_Acceptance:_ Changing a skill's level and reloading shows the new value.

**Task 3.4** — Implement the gap score calculation (per AC1 in spec.md:
percentage of required skills not at "confident") and display it on the
dashboard.
_Acceptance:_ Matches the worked example in spec.md AC1 exactly (3 of 10
confident → 70% gap).

---

## Phase 4 — Mentor Module

**Task 4.1** — Mentor dashboard: list of assigned mentees (via
MentorAssignment) with each one's current gap score.
_Acceptance:_ Seeded mentor with 0 mentees sees an empty state, not an error
(per spec.md edge cases).

**Task 4.2** — Route for a mentor to add a dated note for a mentee, with an
"at risk" checkbox.
_Acceptance:_ Note appears in a chronological list on the mentee's detail
view within the mentor module.

---

## Phase 5 — TPO Module

**Task 5.1** — Route for the TPO to create/edit a JobRole and its Skill
checklist.
_Acceptance:_ Adding a skill to a role makes it appear in that role's
student-facing checklist.

**Task 5.2** — TPO dashboard: aggregate view showing count of at-risk
students (per mentor flags) and median gap score per branch.
_Acceptance:_ Numbers match a manually-computed example from seeded data.

**Task 5.3** — CSV export route for the at-risk student list.
_Acceptance:_ Downloaded CSV opens correctly and contains the expected columns.

---

## Phase 6 — Admin Module

**Task 6.1** — Admin view for department-wide gap score trends (simple table
or chart, current semester only is fine for v1).
_Acceptance:_ Displays correctly with seeded multi-student data.

**Task 6.2** — Bulk mentor-mentee assignment via CSV upload.
_Acceptance:_ Uploading a well-formed CSV creates the correct
MentorAssignment rows; a malformed CSV shows a clear error, not a crash.

---

## Phase 7 — Hardening (recommend cloud model or manual work per plan.md §6)

**Task 7.1** — Audit all routes to confirm role_required is applied
correctly and no student can access another student's data by URL
manipulation (per spec.md AC3 and constraints §8).

**Task 7.2** — Add basic automated tests for the gap score calculation and
the access-control decorator (these are the two most correctness-critical,
easy-to-silently-break pieces).
