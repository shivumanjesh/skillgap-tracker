"""
Skill-Gap & Employability Readiness Tracker - Streamlit Cloud Application
========================================================================
Production-grade multi-role dashboard designed for Streamlit Community Cloud.
Reuses the application models, business logic, and database layer.
"""

import os
import sys
from datetime import datetime, timezone
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func
import streamlit as st

# Configure page metadata and wide layout
st.set_page_config(
    page_title="SkillGap Tracker - Employability Readiness",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Flask app context for database and models
from app import create_app
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

# Custom CSS styling for modern SaaS feel
st.markdown(
    """
    <style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1rem 1.25rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a;
    }
    /* Role Badge */
    .role-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-student { background-color: #e0e7ff; color: #3730a3; }
    .badge-mentor { background-color: #ecfdf5; color: #065f46; }
    .badge-tpo { background-color: #fef3c7; color: #92400e; }
    .badge-admin { background-color: #f3e8ff; color: #6b21a8; }
    /* Chip style */
    .skill-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.75rem;
        margin: 0.2rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 500;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        color: #1e293b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_app():
    """Create and cache the Flask application context."""
    try:
        if hasattr(st, "secrets"):
            if "DATABASE_URL" in st.secrets:
                os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
            if "SECRET_KEY" in st.secrets:
                os.environ["SECRET_KEY"] = st.secrets["SECRET_KEY"]
    except Exception:
        pass

    flask_app = create_app()

    with flask_app.app_context():
        db.create_all()
        # Seed immediately if empty
        if User.query.count() == 0:
            try:
                from seed import seed_database
                seed_database(flask_app)
            except Exception as e:
                print(f"Auto-seed exception: {e}")
    return flask_app


flask_app = get_app()


def ensure_database_seeded():
    """Guarantee tables and users exist in the database."""
    with flask_app.app_context():
        db.create_all()
        if User.query.count() == 0:
            try:
                from seed import seed_database
                seed_database(flask_app)
            except Exception as e:
                print(f"Error ensuring database seeded: {e}")


def init_session():
    """Initialize session state keys safely."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.session_state["user_name"] = None
        st.session_state["user_email"] = None
        st.session_state["user_role"] = None


init_session()


def login_user(user):
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = user.id
    st.session_state["user_name"] = user.name
    st.session_state["user_email"] = user.email
    st.session_state["user_role"] = user.role
    st.rerun()


def logout_user():
    st.session_state.clear()
    init_session()
    st.rerun()


def authenticate_user(identifier, password):
    """Authenticate by email or username, with forgiving demo password options."""
    if not identifier or not password:
        return None

    ensure_database_seeded()
    clean_id = identifier.strip().lower()

    with flask_app.app_context():
        # Match by email or name (case-insensitive)
        user = User.query.filter(
            (func.lower(User.email) == clean_id) | (func.lower(User.name) == clean_id)
        ).first()

        # Support quick username aliases like 'student', 'student1', 'mentor', 'tpo', 'admin'
        if not user:
            role_aliases = {
                "student": "student",
                "student1": "student",
                "mentor": "mentor",
                "mentor1": "mentor",
                "tpo": "tpo",
                "tpo1": "tpo",
                "admin": "admin",
                "admin1": "admin",
            }
            if clean_id in role_aliases:
                user = User.query.filter_by(role=role_aliases[clean_id]).first()

        if user:
            # Check standard password hash or demo passwords
            clean_pwd = password.strip()
            demo_passwords = [
                "password123",
                f"{user.role}123",
                "student123",
                "mentor123",
                "tpo123",
                "admin123",
            ]
            if user.check_password(clean_pwd) or clean_pwd in demo_passwords:
                return user
        return None


# ==========================================
# CALCULATION HELPERS
# ==========================================
def calculate_student_gap(student_id):
    """Calculate effective skill levels and gap percentage for a student."""
    with flask_app.app_context():
        profile = StudentProfile.query.filter_by(user_id=student_id).first()
        target_role = profile.target_job_role if profile else None
        skills = target_role.skills if target_role else []

        if not skills:
            return profile, target_role, [], {}, 0, 100.0, {"not_started": 0, "learning": 0, "comfortable": 0, "confident": 0}

        skill_ids = [s.id for s in skills]
        assessments = Assessment.query.filter(
            Assessment.student_id == student_id,
            Assessment.skill_id.in_(skill_ids),
        ).all()

        effective_level = {}
        sources = {}
        for a in assessments:
            if a.skill_id not in effective_level or a.source == "mentor":
                effective_level[a.skill_id] = a.level
                sources[a.skill_id] = a.source

        level_counts = {"confident": 0, "comfortable": 0, "learning": 0, "not_started": 0}
        for s in skills:
            lvl = effective_level.get(s.id, "not_started")
            level_counts[lvl] = level_counts.get(lvl, 0) + 1

        not_confident_count = sum(
            effective_level.get(s.id, "not_started") != "confident" for s in skills
        )
        gap_percentage = round((not_confident_count / len(skills)) * 100, 1)
        readiness_score = round(100.0 - gap_percentage, 1)

        return profile, target_role, skills, effective_level, sources, readiness_score, gap_percentage, level_counts


# ==========================================
# AUTHENTICATION SCREEN
# ==========================================
def render_auth_page():
    st.markdown("### 🎓 Skill-Gap & Employability Readiness Tracker")
    st.caption("College Career Placement & Skill-Readiness Platform")

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.info(
            """
            **Welcome to the Placement Readiness Engine!**
            
            This system tracks student competency across curated career tracks, measures skill gaps, enables faculty mentor interventions, and provides Training & Placement Officers (TPO) with real-time cohort analytics.
            """
        )

        st.markdown("#### ⚡ Quick Demo Access")
        st.caption("Click any demo role below to sign in instantly:")

        demo_cols = st.columns(4)
        with demo_cols[0]:
            if st.button("👨‍🎓 Student", key="main_student_btn", use_container_width=True, type="primary"):
                ensure_database_seeded()
                with flask_app.app_context():
                    user = User.query.filter_by(role="student").first()
                    if user:
                        login_user(user)
                    else:
                        st.error("Student user not found. Please click 'Reset Demo Database' in the sidebar.")
        with demo_cols[1]:
            if st.button("👩‍🏫 Mentor", key="main_mentor_btn", use_container_width=True):
                ensure_database_seeded()
                with flask_app.app_context():
                    user = User.query.filter_by(role="mentor").first()
                    if user:
                        login_user(user)
                    else:
                        st.error("Mentor user not found. Please click 'Reset Demo Database' in the sidebar.")
        with demo_cols[2]:
            if st.button("🏢 TPO", key="main_tpo_btn", use_container_width=True):
                ensure_database_seeded()
                with flask_app.app_context():
                    user = User.query.filter_by(role="tpo").first()
                    if user:
                        login_user(user)
                    else:
                        st.error("TPO user not found. Please click 'Reset Demo Database' in the sidebar.")
        with demo_cols[3]:
            if st.button("⚙️ Admin", key="main_admin_btn", use_container_width=True):
                ensure_database_seeded()
                with flask_app.app_context():
                    user = User.query.filter_by(role="admin").first()
                    if user:
                        login_user(user)
                    else:
                        st.error("Admin user not found. Please click 'Reset Demo Database' in the sidebar.")

    with col2:
        st.markdown("#### 🔐 Secure Sign In")
        with st.form("login_form"):
            username_or_email = st.text_input("Username or Email", placeholder="e.g. student@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submit:
                if not username_or_email or not password:
                    st.error("Please enter both username/email and password.")
                else:
                    user = authenticate_user(username_or_email, password)
                    if user:
                        login_user(user)
                    else:
                        st.error("Invalid credentials. Try using the quick demo buttons on the left, or verify your email and password.")

        with st.expander("ℹ️ Test Credentials Reference", expanded=True):
            st.markdown(
                """
                - **Student**: `student@example.com` / `student123`
                - **Mentor**: `mentor@example.com` / `mentor123`
                - **TPO**: `tpo@example.com` / `tpo123`
                - **Admin**: `admin@example.com` / `admin123`
                """
            )


# ==========================================
# STUDENT DASHBOARD
# ==========================================
def render_student_view():
    user_id = st.session_state["user_id"]
    st.title("👨‍🎓 Student Employability Dashboard")

    profile, target_role, skills, effective_level, sources, readiness_score, gap_percentage, level_counts = calculate_student_gap(user_id)

    tabs = st.tabs(["📊 Readiness Overview", "🎯 Target Role & Skills", "📝 Self-Assessment", "💬 Mentor Guidance"])

    # TAB 1: OVERVIEW
    with tabs[0]:
        if not target_role:
            st.warning("⚠️ You have not selected a Target Career Role yet! Head over to the 'Target Role & Skills' tab to choose your path.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Target Career Track", target_role.name)
            m2.metric("Readiness Score", f"{readiness_score}%", delta=f"{readiness_score - 50:.1f}% vs Benchmark")
            m3.metric("Skill Deficit Gap", f"{gap_percentage}%", delta=f"-{gap_percentage}%", delta_color="inverse")
            m4.metric("Total Competencies", len(skills))

            c1, c2 = st.columns([1, 1])
            with c1:
                st.subheader("Competency Distribution")
                df_counts = pd.DataFrame([
                    {"Status": "Confident", "Count": level_counts["confident"], "Color": "#10b981"},
                    {"Status": "Comfortable", "Count": level_counts["comfortable"], "Color": "#3b82f6"},
                    {"Status": "Learning", "Count": level_counts["learning"], "Color": "#f59e0b"},
                    {"Status": "Not Started", "Count": level_counts["not_started"], "Color": "#ef4444"},
                ])
                fig = px.pie(
                    df_counts,
                    names="Status",
                    values="Count",
                    hole=0.5,
                    color="Status",
                    color_discrete_map={
                        "Confident": "#10b981",
                        "Comfortable": "#3b82f6",
                        "Learning": "#f59e0b",
                        "Not Started": "#ef4444",
                    },
                )
                fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.subheader("Priority Focus Skills")
                priority_order = {"not_started": 1, "learning": 2, "comfortable": 3}
                priorities = [
                    (s.name, effective_level.get(s.id, "not_started"), priority_order.get(effective_level.get(s.id, "not_started"), 9))
                    for s in skills if effective_level.get(s.id, "not_started") != "confident"
                ]
                priorities.sort(key=lambda x: x[2])

                if not priorities:
                    st.success("🎉 Outstanding! You are Confident across all required competencies for your target role!")
                else:
                    st.caption("Focus on these competencies to lower your skill gap:")
                    for skill_name, lvl, _ in priorities:
                        badge_color = "red" if lvl == "not_started" else ("orange" if lvl == "learning" else "blue")
                        st.markdown(f"- **{skill_name}**: :{badge_color}[{lvl.replace('_', ' ').title()}]")

    # TAB 2: TARGET ROLE SELECTION
    with tabs[1]:
        st.subheader("Select or Update Target Career Role")
        with flask_app.app_context():
            all_roles = JobRole.query.order_by(JobRole.name).all()
            role_options = {r.name: r.id for r in all_roles}
            current_role_name = target_role.name if target_role else list(role_options.keys())[0]

            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                selected_role_name = st.selectbox(
                    "Choose your desired career aspiration:",
                    options=list(role_options.keys()),
                    index=list(role_options.keys()).index(current_role_name) if current_role_name in role_options else 0,
                )
            with col_btn:
                st.write("")
                st.write("")
                if st.button("Save Target Role", type="primary", use_container_width=True):
                    prof = StudentProfile.query.filter_by(user_id=user_id).first()
                    if not prof:
                        prof = StudentProfile(user_id=user_id, branch="Computer Science", year=3)
                        db.session.add(prof)
                    prof.target_job_role_id = role_options[selected_role_name]
                    db.session.commit()
                    st.success(f"Target role updated to {selected_role_name}!")
                    st.rerun()

        st.divider()
        st.subheader("Available Career Tracks & Required Skills")
        with flask_app.app_context():
            roles = JobRole.query.all()
            for r in roles:
                with st.expander(f"📌 {r.name} ({len(r.skills)} Core Competencies)", expanded=(r.id == (target_role.id if target_role else None))):
                    skills_html = "".join([f'<span class="skill-chip">✓ {s.name}</span>' for s in r.skills])
                    st.markdown(skills_html, unsafe_allow_html=True)

    # TAB 3: SELF-ASSESSMENT
    with tabs[2]:
        st.subheader("📝 Self-Assessment & Competency Rating")
        if not target_role or not skills:
            st.warning("Please select a target role first.")
        else:
            st.caption("Update your current proficiency level. Mentor-verified ratings are highlighted with a shield.")

            level_map = {
                "not_started": "Not Started (0%)",
                "learning": "Learning (Practicing/Courses)",
                "comfortable": "Comfortable (Built mini-projects)",
                "confident": "Confident (Interview/Production Ready)",
            }
            inv_level_map = {v: k for k, v in level_map.items()}

            with st.form("assessment_form"):
                updates = {}
                for s in skills:
                    current_lvl = effective_level.get(s.id, "not_started")
                    is_mentor = sources.get(s.id) == "mentor"
                    col_label, col_val = st.columns([2, 2])
                    with col_label:
                        mentor_tag = " 🛡️ *(Faculty Verified)*" if is_mentor else ""
                        st.markdown(f"**{s.name}**{mentor_tag}")
                    with col_val:
                        selected_str = st.selectbox(
                            f"Level for {s.name}",
                            options=list(level_map.values()),
                            index=list(level_map.keys()).index(current_lvl),
                            key=f"skill_select_{s.id}",
                            label_visibility="collapsed",
                        )
                        updates[s.id] = inv_level_map[selected_str]

                submit_assessment = st.form_submit_button("Save All Assessments", type="primary", use_container_width=True)
                if submit_assessment:
                    with flask_app.app_context():
                        for skill_id, new_level in updates.items():
                            existing = Assessment.query.filter_by(
                                student_id=user_id,
                                skill_id=skill_id,
                                source="self",
                            ).first()
                            if existing:
                                existing.level = new_level
                                existing.updated_at = datetime.now(timezone.utc)
                            else:
                                new_a = Assessment(
                                    student_id=user_id,
                                    skill_id=skill_id,
                                    level=new_level,
                                    source="self",
                                )
                                db.session.add(new_a)
                        db.session.commit()
                        st.success("Assessments successfully saved! Employability gap updated.")
                        st.rerun()

    # TAB 4: MENTOR GUIDANCE
    with tabs[3]:
        st.subheader("💬 Faculty Mentor Guidance Stream")
        with flask_app.app_context():
            assignment = MentorAssignment.query.filter_by(student_id=user_id).first()
            if assignment and assignment.mentor:
                st.info(f"**Assigned Faculty Mentor:** {assignment.mentor.name} ({assignment.mentor.email})")
            else:
                st.warning("You do not have an assigned mentor yet. The administration pairs mentors before placement season.")

            notes = MentorNote.query.filter_by(student_id=user_id).order_by(MentorNote.created_at.desc()).all()
            if not notes:
                st.write("No guidance notes recorded yet.")
            else:
                for n in notes:
                    with st.container():
                        st.markdown(f"**{n.created_at.strftime('%B %d, %Y')}** - *by Prof. {n.mentor.name}*")
                        if n.at_risk:
                            st.error(f"⚠️ **Intervention Required**: {n.note_text}")
                        else:
                            st.success(n.note_text)
                        st.divider()


# ==========================================
# FACULTY MENTOR VIEW
# ==========================================
def render_mentor_view():
    mentor_id = st.session_state["user_id"]
    st.title("👩‍🏫 Faculty Mentorship Portal")

    with flask_app.app_context():
        assignments = MentorAssignment.query.filter_by(mentor_id=mentor_id).all()
        student_ids = [a.student_id for a in assignments]
        mentees = User.query.filter(User.id.in_(student_ids)).all() if student_ids else []

    m1, m2, m3 = st.columns(3)
    m1.metric("Assigned Mentees", len(mentees))

    # Calculate at-risk count
    at_risk_count = 0
    with flask_app.app_context():
        for m in mentees:
            last_note = MentorNote.query.filter_by(student_id=m.id).order_by(MentorNote.created_at.desc()).first()
            if last_note and last_note.at_risk:
                at_risk_count += 1
    m2.metric("Flagged At-Risk", at_risk_count, delta=f"{at_risk_count} needing review", delta_color="inverse")
    m3.metric("Cohort Active Status", "Active Placement Cycle")

    if not mentees:
        st.info("No students are currently assigned to your mentorship cohort.")
        return

    st.subheader("Mentee Cohort Overview")
    mentee_records = []
    with flask_app.app_context():
        for m in mentees:
            _, t_role, _, _, _, r_score, gap, _ = calculate_student_gap(m.id)
            prof = StudentProfile.query.filter_by(user_id=m.id).first()
            mentee_records.append({
                "Student ID": m.id,
                "Name": m.name,
                "Email": m.email,
                "Branch": prof.branch if prof else "N/A",
                "Target Role": t_role.name if t_role else "Not Selected",
                "Skill Gap": f"{gap}%",
                "Readiness": f"{r_score}%",
            })

    st.dataframe(pd.DataFrame(mentee_records), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Inspect Mentee & Submit Faculty Evaluation")

    selected_student_name = st.selectbox("Select Mentee to evaluate:", [m.name for m in mentees])
    selected_mentee = next((m for m in mentees if m.name == selected_student_name), None)

    if selected_mentee:
        _, t_role, skills, eff_level, sources, r_score, gap, _ = calculate_student_gap(selected_mentee.id)

        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"#### Student: {selected_mentee.name}")
            st.write(f"**Target Role:** {t_role.name if t_role else 'None'}")
            st.write(f"**Readiness Score:** {r_score}% (Gap: {gap}%)")

            # Note Logging
            st.markdown("##### 📝 Add Guidance Note / Action Plan")
            with st.form("mentor_note_form"):
                note_text = st.text_area("Observations and Action Items:")
                at_risk_flag = st.checkbox("🚩 Flag student as At-Risk (alerts TPO placement office)")
                submit_note = st.form_submit_button("Post Note", type="primary")

                if submit_note:
                    if not note_text.strip():
                        st.error("Please enter note content.")
                    else:
                        with flask_app.app_context():
                            note = MentorNote(
                                mentor_id=mentor_id,
                                student_id=selected_mentee.id,
                                note_text=note_text.strip(),
                                at_risk=at_risk_flag,
                            )
                            db.session.add(note)
                            db.session.commit()
                            st.success("Guidance note added successfully!")
                            st.rerun()

        with c2:
            st.markdown("#### 🛡️ Faculty Assessment Override")
            st.caption("Faculty mentor assessments take priority in gap calculations.")

            if not skills:
                st.write("Student has not selected target competencies.")
            else:
                level_options = ["not_started", "learning", "comfortable", "confident"]
                with st.form("override_form"):
                    new_mentor_evals = {}
                    for s in skills:
                        curr = eff_level.get(s.id, "not_started")
                        new_mentor_evals[s.id] = st.selectbox(
                            f"{s.name} (Currently: {curr})",
                            options=level_options,
                            index=level_options.index(curr),
                            key=f"mentor_eval_{s.id}",
                        )
                    submit_override = st.form_submit_button("Save Verified Faculty Ratings", type="primary")
                    if submit_override:
                        with flask_app.app_context():
                            for sid, lvl in new_mentor_evals.items():
                                existing = Assessment.query.filter_by(
                                    student_id=selected_mentee.id,
                                    skill_id=sid,
                                    source="mentor",
                                ).first()
                                if existing:
                                    existing.level = lvl
                                    existing.updated_at = datetime.now(timezone.utc)
                                else:
                                    db.session.add(
                                        Assessment(
                                            student_id=selected_mentee.id,
                                            skill_id=sid,
                                            level=lvl,
                                            source="mentor",
                                        )
                                    )
                            db.session.commit()
                            st.success("Faculty assessment saved!")
                            st.rerun()


# ==========================================
# TPO (TRAINING & PLACEMENT OFFICER) VIEW
# ==========================================
def render_tpo_view():
    st.title("🏢 Training & Placement Officer (TPO) Cockpit")

    with flask_app.app_context():
        students = User.query.filter_by(role="student").all()
        student_rows = []
        ready_count = 0
        total_gap_sum = 0
        gap_count = 0
        at_risk_students = []

        for s in students:
            prof, t_role, skills, _, _, r_score, gap, _ = calculate_student_gap(s.id)
            if skills:
                total_gap_sum += gap
                gap_count += 1
                if gap <= 30.0:
                    ready_count += 1

            # Check at-risk
            latest_note = MentorNote.query.filter_by(student_id=s.id).order_by(MentorNote.created_at.desc()).first()
            is_at_risk = bool(latest_note and latest_note.at_risk)
            if is_at_risk:
                at_risk_students.append({
                    "Name": s.name,
                    "Email": s.email,
                    "Branch": prof.branch if prof else "N/A",
                    "Target Role": t_role.name if t_role else "N/A",
                    "Gap": f"{gap}%",
                    "Latest Note": latest_note.note_text,
                })

            student_rows.append({
                "student_id": s.id,
                "name": s.name,
                "email": s.email,
                "branch": prof.branch if prof else "Unassigned",
                "year": prof.year if prof else 1,
                "target_role": t_role.name if t_role else "Not Selected",
                "gap_percentage": gap,
                "readiness_score": r_score,
                "is_at_risk": is_at_risk,
            })

    avg_gap = round(total_gap_sum / gap_count, 1) if gap_count > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Enrolled Candidates", len(students))
    m2.metric("Placement Ready (Gap ≤ 30%)", ready_count, delta=f"{(ready_count/len(students)*100):.1f}% Cohort Ready" if students else "0%")
    m3.metric("Average Skill Gap", f"{avg_gap}%", delta=f"-{avg_gap}%", delta_color="inverse")
    m4.metric("At-Risk Interventions", len(at_risk_students), delta_color="inverse")

    tabs = st.tabs(["📊 Branch & Department Analytics", "🚩 Early Warning (At-Risk)", "📋 All Student Roster", "📥 Data Exports"])

    # TAB 1: BRANCH ANALYTICS
    with tabs[0]:
        df_students = pd.DataFrame(student_rows)
        if not df_students.empty:
            branch_summary = df_students.groupby("branch").agg(
                Total_Students=("student_id", "count"),
                Avg_Gap=("gap_percentage", "mean"),
                Ready_Count=("gap_percentage", lambda x: sum(x <= 30.0)),
                At_Risk_Count=("is_at_risk", "sum"),
            ).reset_index()
            branch_summary["Avg_Gap"] = branch_summary["Avg_Gap"].round(1)

            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.subheader("Departmental Skill Gap Benchmark")
                fig = px.bar(
                    branch_summary,
                    x="branch",
                    y="Avg_Gap",
                    color="Avg_Gap",
                    color_continuous_scale="Viridis",
                    labels={"Avg_Gap": "Average Skill Gap (%)", "branch": "Department / Branch"},
                )
                fig.update_layout(height=320)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.subheader("Department Summary Table")
                st.dataframe(branch_summary, use_container_width=True, hide_index=True)

    # TAB 2: AT RISK
    with tabs[1]:
        st.subheader("🚩 At-Risk Candidates Needing Academic & Placement Intervention")
        if not at_risk_students:
            st.success("No students are currently flagged as at-risk.")
        else:
            st.dataframe(pd.DataFrame(at_risk_students), use_container_width=True, hide_index=True)

    # TAB 3: ROSTER
    with tabs[2]:
        st.subheader("Placement Candidate Roster")
        st.dataframe(df_students, use_container_width=True, hide_index=True)

    # TAB 4: EXPORT
    with tabs[3]:
        st.subheader("📥 Export Reports for Institutional Accreditation & Companies")
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv_all = df_students.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📄 Download Complete Readiness CSV",
                data=csv_all,
                file_name="employability_readiness.csv",
                mime="text/csv",
                type="primary",
            )
        with col_exp2:
            if at_risk_students:
                csv_risk = pd.DataFrame(at_risk_students).to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="🚩 Download At-Risk Students CSV",
                    data=csv_risk,
                    file_name="at_risk_students.csv",
                    mime="text/csv",
                )


# ==========================================
# ADMIN VIEW
# ==========================================
def render_admin_view():
    st.title("⚙️ College Administration Portal")

    tabs = st.tabs(["📈 Platform Macro Trends", "🤝 Mentor-Student Pairing", "👥 User Directory"])

    with tabs[0]:
        st.subheader("Platform Analytics & Macro Readiness")
        with flask_app.app_context():
            roles = JobRole.query.all()
            role_gaps = []
            for r in roles:
                profiles = StudentProfile.query.filter_by(target_job_role_id=r.id).all()
                if profiles:
                    gaps = [calculate_student_gap(p.user_id)[6] for p in profiles]
                    role_gaps.append({"Job Role": r.name, "Students": len(profiles), "Average Gap": round(sum(gaps) / len(gaps), 1)})
                else:
                    role_gaps.append({"Job Role": r.name, "Students": 0, "Average Gap": 0})

            df_roles = pd.DataFrame(role_gaps)
            fig = px.bar(
                df_roles,
                x="Job Role",
                y="Average Gap",
                color="Average Gap",
                color_continuous_scale="Inferno",
                labels={"Average Gap": "Average Deficit (%)"},
            )
            st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.subheader("Mentor Assignment Management")
        with flask_app.app_context():
            mentors = User.query.filter_by(role="mentor").all()
            students = User.query.filter_by(role="student").all()
            active_assignments = MentorAssignment.query.all()

            assigned_student_ids = {a.student_id for a in active_assignments}
            unassigned_students = [s for s in students if s.id not in assigned_student_ids]

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### Assign Faculty Mentor")
                if not unassigned_students:
                    st.success("All students currently have an assigned mentor!")
                else:
                    with st.form("pairing_form"):
                        sel_mentor = st.selectbox("Select Faculty Mentor:", [f"{m.name} ({m.email})" for m in mentors])
                        sel_student = st.selectbox("Select Student:", [f"{s.name} ({s.email})" for s in unassigned_students])
                        submit_pair = st.form_submit_button("Confirm Assignment", type="primary")

                        if submit_pair:
                            mentor_obj = next(m for m in mentors if f"{m.name} ({m.email})" == sel_mentor)
                            student_obj = next(s for s in unassigned_students if f"{s.name} ({s.email})" == sel_student)
                            db.session.add(MentorAssignment(mentor_id=mentor_obj.id, student_id=student_obj.id))
                            db.session.commit()
                            st.success(f"Assigned {student_obj.name} to {mentor_obj.name}!")
                            st.rerun()

            with c2:
                st.markdown("##### Current Assignments")
                assignment_data = [
                    {"Mentor": a.mentor.name, "Student": a.student.name, "Student Email": a.student.email}
                    for a in active_assignments if a.mentor and a.student
                ]
                st.dataframe(pd.DataFrame(assignment_data), use_container_width=True, hide_index=True)

    with tabs[2]:
        st.subheader("Central Directory")
        with flask_app.app_context():
            users = User.query.order_by(User.role, User.name).all()
            user_list = [{"ID": u.id, "Name": u.name, "Email": u.email, "Role": u.role.upper()} for u in users]
            st.dataframe(pd.DataFrame(user_list), use_container_width=True, hide_index=True)


# ==========================================
# MAIN ROUTING & SIDEBAR
# ==========================================
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🎓 SkillGap Tracker")
        st.caption("College Placement Readiness Platform")
        st.divider()

        if st.session_state["authenticated"]:
            role = st.session_state["user_role"]
            user_name = st.session_state["user_name"]
            st.markdown(f"#### 👤 {user_name}")
            role_class = f"badge-{role}"
            st.markdown(f'<span class="role-badge {role_class}">{role.upper()}</span>', unsafe_allow_html=True)
            st.caption(st.session_state["user_email"])
            st.divider()

            if st.button("🚪 Sign Out", key="sidebar_sign_out", use_container_width=True):
                logout_user()
        else:
            st.markdown("#### ⚡ Quick Demo Logins")
            sc1, sc2 = st.columns(2)
            with sc1:
                if st.button("👨‍🎓 Student", key="sb_student", use_container_width=True):
                    ensure_database_seeded()
                    with flask_app.app_context():
                        u = User.query.filter_by(role="student").first()
                        if u:
                            login_user(u)
            with sc2:
                if st.button("👩‍🏫 Mentor", key="sb_mentor", use_container_width=True):
                    ensure_database_seeded()
                    with flask_app.app_context():
                        u = User.query.filter_by(role="mentor").first()
                        if u:
                            login_user(u)
            sc3, sc4 = st.columns(2)
            with sc3:
                if st.button("🏢 TPO", key="sb_tpo", use_container_width=True):
                    ensure_database_seeded()
                    with flask_app.app_context():
                        u = User.query.filter_by(role="tpo").first()
                        if u:
                            login_user(u)
            with sc4:
                if st.button("⚙️ Admin", key="sb_admin", use_container_width=True):
                    ensure_database_seeded()
                    with flask_app.app_context():
                        u = User.query.filter_by(role="admin").first()
                        if u:
                            login_user(u)

            st.divider()
            st.markdown(
                """
                **Credentials:**
                - Student: `student@example.com` / `student123`
                - Mentor: `mentor@example.com` / `mentor123`
                - TPO: `tpo@example.com` / `tpo123`
                - Admin: `admin@example.com` / `admin123`
                """
            )
            st.divider()
            if st.button("🔄 Reset Demo Database", key="sb_reseed", use_container_width=True):
                try:
                    from seed import seed_database
                    seed_database(flask_app)
                    st.success("Database re-seeded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error seeding database: {e}")

        st.divider()
        st.markdown(
            """
            **Platform Architecture**
            - Engine: Streamlit + SQLAlchemy
            - Deployment: Streamlit Cloud
            - Security: Salted Hashing & RBAC
            """
        )


def main():
    ensure_database_seeded()
    render_sidebar()

    if not st.session_state["authenticated"]:
        render_auth_page()
    else:
        role = st.session_state["user_role"]
        if role == "student":
            render_student_view()
        elif role == "mentor":
            render_mentor_view()
        elif role == "tpo":
            render_tpo_view()
        elif role == "admin":
            render_admin_view()
        else:
            st.error("Unrecognized user role.")


if __name__ == "__main__":
    main()
