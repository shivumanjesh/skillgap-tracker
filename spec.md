# Specification: Skill-Gap & Employability Readiness Tracker

## 1. Problem Statement

Tier-3 engineering colleges consistently report low placement rates, not primarily
due to lack of student effort, but due to a **visibility gap**: no one in the
system — student, mentor, or placement officer — has a real-time, unified view
of which students are falling behind on the skills recruiters actually want,
until it is too late (final year, placement season).

Skill development, mentoring, and placement readiness are currently tracked
through disconnected, manual processes: spreadsheets per department, WhatsApp
groups for opportunities, paper mentor-mentee logs, and placement data
compiled only right before recruitment drives.

## 2. Goals

- Give every student a clear, continuously updated view of their skill gaps
  relative to their target job roles.
- Give mentors a structured way to track mentee progress across a semester
  instead of relying on memory or informal check-ins.
- Give the Training & Placement Officer (TPO) an early-warning view of
  at-risk students, months before placement drives — not days before.
- Give department/college administration a data-backed view of readiness
  trends across batches and departments.

## 3. Non-Goals (explicitly out of scope for v1)

- No integration with actual recruiter/company systems (no live job board).
- No automated resume parsing or AI-based skill inference from resumes.
- No mobile app — web only, responsive design is sufficient.
- No real-time chat/messaging system (existing tools like WhatsApp stay for
  that; this system is for structured tracking, not communication).
- No plagiarism detection or academic integrity tooling.

## 4. Stakeholders & Roles

| Role | Description |
|---|---|
| **Student** | Views own skill profile, gap analysis, and assigned action items |
| **Mentor (Faculty)** | Assigned a set of mentee students; logs progress, flags concerns |
| **TPO** | Views cross-department readiness dashboard, manages skill benchmarks per job role |
| **Admin/HOD** | Views department-level analytics, manages mentor-mentee assignments |

## 5. Functional Requirements

### 5.1 Authentication & Roles
- Users log in with email + password.
- Each user has exactly one role: `student`, `mentor`, `tpo`, or `admin`.
- Role determines which views/actions are available (role-based access control).

### 5.2 Student Skill Profile
- A student has a profile listing: branch, year, target job role(s).
- Each target job role has an associated **skill checklist** (e.g., "Data
  Structures", "SQL", "Communication") defined by the TPO.
- Student self-reports proficiency per skill (scale: Not Started / Learning /
  Comfortable / Confident).
- Mentor can override or annotate a student's self-reported proficiency with
  a verified assessment.

### 5.3 Skill Gap Calculation
- For a given student and target role, the system computes a **gap score**:
  the count/percentage of required skills not yet at "Confident" level.
- Gap score is visible to the student, their mentor, and the TPO — not to
  other students.

### 5.4 Mentor Tracking
- Mentor sees a list of assigned mentees with each one's current gap score.
- Mentor can log a dated note per mentee (e.g., "Discussed DSA plan on
  12 Feb, student to complete 20 problems by 26 Feb").
- Mentor can flag a mentee as "at risk" — this surfaces on the TPO dashboard.

### 5.5 TPO Dashboard
- TPO can define/edit skill checklists per job role.
- TPO sees an aggregate view: number of students per department who are
  "at risk," median gap score per branch, and a list of flagged students.
- TPO can export the at-risk list (CSV) for use in intervention planning.

### 5.6 Admin/HOD View
- Admin sees department-wide trends over time (are gap scores improving
  semester over semester?).
- Admin manages mentor-mentee assignments (bulk assign via CSV upload or
  manual pairing).

## 6. Acceptance Criteria (representative examples)

- **AC1:** Given a student has marked 3 of 10 required skills as "Confident,"
  the system correctly displays a gap score of 70%.
- **AC2:** Given a mentor flags a mentee as "at risk," that student appears
  in the TPO's at-risk list within the same session (no manual refresh
  needed beyond a page reload).
- **AC3:** Given a user with role `student` attempts to access the TPO
  dashboard URL directly, the system denies access and redirects to their
  own dashboard.
- **AC4:** Given the TPO edits a skill checklist for a job role, all
  students who selected that role see their gap score recalculated on next
  login (recalculation does not need to be instantaneous/live).

## 7. Edge Cases to Handle

- A student has not selected any target job role yet → show a prompt to
  select one; gap score is undefined, not zero.
- A mentor is unassigned (no mentees yet) → show an empty state, not an error.
- A skill checklist is edited after students have already self-assessed
  against the old version → recalculate against the new checklist; don't
  silently keep stale data.
- Two students have identical names → always key on unique student ID, never
  display name alone in any admin/mentor list.

## 8. Constraints

- Must run as a self-hosted web app suitable for a college's own low-cost
  hosting (no dependency on paid third-party SaaS for core functionality).
- Should be usable on shared/lab computers with modest specs — avoid
  heavy client-side frameworks that require high-end browsers.
- Data privacy: student skill data should only be visible to that student,
  their assigned mentor, TPO, and admin — never to other students.

## 9. Pointers / Prior Art

- Similar in spirit to LMS gradebooks (e.g., Moodle) but focused on
  skill-readiness rather than course grades.
- Similar in spirit to OKR/goal-tracking tools but scoped to placement
  readiness rather than general goal-setting.
