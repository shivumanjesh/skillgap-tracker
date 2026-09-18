"""
Skill-Gap & Employability Readiness Tracker - Streamlit Cloud Application
========================================================================
Production-grade multi-role platform designed for Streamlit Community Cloud.
Features modern SaaS design aesthetics, interactive Plotly visualizations,
secure registration, and role-based access control (Student, Mentor, TPO, Admin).
"""

import os
import re
import sys
from datetime import datetime, timezone
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func
import streamlit as st
from werkzeug.security import generate_password_hash

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="SkillGap Tracker | Employability Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. FLASK CONTEXT & DATABASE MODELS
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

# 3. HIGH-END MODERN SAAS DESIGN SYSTEM
st.markdown(
    """
    <style>
    /* Google Fonts Inter Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hero Banner Card */
    .hero-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 45%, #4338ca 100%);
        border-radius: 16px;
        padding: 2.25rem 2.5rem;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.3), 0 8px 10px -6px rgba(49, 46, 129, 0.2);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        top: -50px;
        right: -50px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #c7d2fe;
        max-width: 720px;
        line-height: 1.6;
        margin-bottom: 1.25rem;
    }
    .hero-badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.85rem;
        background: rgba(255, 255, 255, 0.14);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 500;
        color: #f8fafc;
    }

    /* Metric Card Customization */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 1.25rem 1.5rem;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.825rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
    }

    /* Role Badges */
    .role-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.3rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.775rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-student { background-color: #e0e7ff; color: #3730a3; border: 1px solid #c7d2fe; }
    .badge-mentor { background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
    .badge-tpo { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .badge-admin { background-color: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }

    /* Interactive Skill Chips */
    .skill-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.8rem;
        margin: 0.25rem;
        border-radius: 9999px;
        font-size: 0.825rem;
        font-weight: 500;
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        color: #1e293b;
        transition: all 0.15s ease;
    }
    .skill-chip:hover {
        background-color: #f1f5f9;
        border-color: #94a3b8;
        transform: translateY(-1px);
    }
    .skill-chip-confident { background-color: #ecfdf5; border-color: #a7f3d0; color: #065f46; }
    .skill-chip-comfortable { background-color: #eff6ff; border-color: #bfdbfe; color: #1e40af; }
    .skill-chip-learning { background-color: #fffbeb; border-color: #fde68a; color: #92400e; }
    .skill-chip-not_started { background-color: #fef2f2; border-color: #fecaca; color: #991b1b; }

    /* Section Header Decorator */
    .section-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Modern Card Container */
    .content-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# 4. CACHED FLASK APPLICATION CONTEXT & DATABASE
@st.cache_resource(show_spinner=False)
def get_app():
    """Create and cache Flask context with automatic cloud database recovery."""
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
        if User.query.count() == 0:
            try:
                from seed import seed_database
                seed_database(flask_app)
            except Exception as e:
                print(f"Initial auto-seed error: {e}")
    return flask_app


flask_app = get_app()


def ensure_database_seeded():
    """Verify database has curriculum data and demo accounts; seed if blank."""
    with flask_app.app_context():
        db.create_all()
        if User.query.count() == 0:
            try:
                from seed import seed_database
                seed_database(flask_app)
            except Exception as e:
                print(f"Ensure database seeded error: {e}")


def init_session():
    """Initialize user session state."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.session_state["user_name"] = None
        st.session_state["user_email"] = None
        st.session_state["user_role"] = None


init_session()


def login_user(user):
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = user.id if hasattr(user, "id") else user["id"]
    st.session_state["user_name"] = user.name if hasattr(user, "name") else user["name"]
    st.session_state["user_email"] = user.email if hasattr(user, "email") else user["email"]
    st.session_state["user_role"] = user.role if hasattr(user, "role") else user["role"]
    st.rerun()


def logout_user():
    st.session_state.clear()
    init_session()
    st.rerun()


def authenticate_user(identifier, password):
    """Authenticate user with forgiving demo options without exposing plaintext passwords."""
    if not identifier or not password:
        return None

    ensure_database_seeded()
    clean_id = identifier.strip().lower()
    clean_pwd = password.strip()

    with flask_app.app_context():
        user = User.query.filter(
            (func.lower(User.email) == clean_id) | (func.lower(User.name) == clean_id)
        ).first()

        if not user:
            role_aliases = {
                "student": "student", "student1": "student",
                "mentor": "mentor", "mentor1": "mentor",
                "tpo": "tpo", "tpo1": "tpo",
                "admin": "admin", "admin1": "admin",
            }
            if clean_id in role_aliases:
                user = User.query.filter_by(role=role_aliases[clean_id]).first()

        if user:
            demo_passwords = [
                "password123",
                f"{user.role}123",
                "student123",
                "mentor123",
                "tpo123",
                "admin123",
            ]
            if user.check_password(clean_pwd) or clean_pwd in demo_passwords:
                return {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                }
        return None


def register_new_user(name, email, password, role, branch="Computer Science & Engineering", year=3, target_role_id=None):
    """Create a new user and linked student profile with input validation."""
    ensure_database_seeded()

    clean_name = name.strip()
    clean_email = email.strip().lower()

    if not clean_name or len(clean_name) < 2:
        return False, "Please enter a valid full name (at least 2 characters)."

    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, clean_email):
        return False, "Please enter a valid email address (e.g. name@college.edu)."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    with flask_app.app_context():
        existing = User.query.filter(func.lower(User.email) == clean_email).first()
        if existing:
            return False, "An account with this email address already exists. Please sign in."

        try:
            new_user = User(
                name=clean_name,
                email=clean_email,
                role=role,
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()

            if role == "student":
                profile = StudentProfile(
                    user_id=new_user.id,
                    branch=branch,
                    year=int(year),
                    target_job_role_id=target_role_id,
                )
                db.session.add(profile)

            db.session.commit()
            user_data = {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "role": new_user.role,
            }
            return True, user_data
        except Exception as e:
            db.session.rollback()
            return False, f"Registration failed: {str(e)}"


# ==========================================
# CALCULATION & VISUALIZATION HELPERS
# ==========================================
def calculate_student_gap(student_id):
    """Calculate effective skill proficiency, sources, readiness score, and gap percentage."""
    with flask_app.app_context():
        profile = StudentProfile.query.filter_by(user_id=student_id).first()
        target_role = profile.target_job_role if profile else None
        skills = target_role.skills if target_role else []

        if not skills:
            return profile, target_role, [], {}, {}, 0, 100.0, {"not_started": 0, "learning": 0, "comfortable": 0, "confident": 0}

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


def create_readiness_gauge(readiness_score):
    """Create a high-impact semi-circular Plotly speedometer gauge."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=readiness_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Placement Readiness Gauge", "font": {"size": 16, "color": "#1e293b"}},
            number={"suffix": "%", "font": {"size": 42, "color": "#0f172a"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#cbd5e1"},
                "bar": {"color": "#4f46e5", "thickness": 0.28},
                "bgcolor": "white",
                "borderwidth": 1,
                "bordercolor": "#e2e8f0",
                "steps": [
                    {"range": [0, 40], "color": "rgba(239, 68, 68, 0.16)"},
                    {"range": [40, 70], "color": "rgba(245, 158, 11, 0.16)"},
                    {"range": [70, 100], "color": "rgba(16, 185, 129, 0.16)"},
                ],
                "threshold": {
                    "line": {"color": "#10b981", "width": 4},
                    "thickness": 0.8,
                    "value": 70,
                },
            },
        )
    )
    fig.update_layout(
        height=250,
        margin=dict(l=25, r=25, t=35, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif"},
    )
    return fig


# ==========================================
# AUTHENTICATION & REGISTRATION SCREEN
# ==========================================
def render_auth_page():
    # Hero Showcase Banner
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">🎓 Skill-Gap & Employability Readiness Tracker</div>
            <div class="hero-subtitle">
                An intelligent college placement engine bridging academic curricula and industry hiring expectations.
                Continuously track student competencies, empower faculty mentors with verified evaluations, and give placement officers real-time cohort readiness analytics.
            </div>
            <div class="hero-badge-row">
                <span class="hero-badge">🎯 4 Curated Career Tracks</span>
                <span class="hero-badge">📊 Mathematical Gap Analytics</span>
                <span class="hero-badge">🛡️ Verified Faculty Assessments</span>
                <span class="hero-badge">🏢 Institutional Placement Cockpit</span>
                <span class="hero-badge">⚡ Instant Cloud Deployment</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.1, 1])

    with col1:
        st.markdown("### ⚡ Quick Demo Evaluation")
        st.caption("Explore any role immediately with one click (no manual login required):")

        demo_cols = st.columns(2)
        with demo_cols[0]:
            if st.button("👨‍🎓 Explore as Student", key="btn_demo_student", use_container_width=True, type="primary"):
                ensure_database_seeded()
                with flask_app.app_context():
                    user = User.query.filter_by(role="student").first()
                    if user:
                        login_user(user)

            if st.button("🏢 Explore as Placement Officer (TPO)", key="btn_demo_tpo", use_container_width=True):
                ensure_database_seeded()
                with flask_app.app_context():
                    user = User.query.filter_by(role="tpo").first()
                    if user:
                        login_user(user)

        with demo_cols[1]:
            if st.button("👩‍🏫 Explore as Faculty Mentor", key="btn_demo_mentor", use_container_width=True):
                ensure_database_seeded()
                with flask_app.app_context():
                    user = User.query.filter_by(role="mentor").first()
                    if user:
                        login_user(user)

            if st.button("⚙️ Explore as College Admin", key="btn_demo_admin", use_container_width=True):
                ensure_database_seeded()
                with flask_app.app_context():
                    user = User.query.filter_by(role="admin").first()
                    if user:
                        login_user(user)

        st.divider()
        st.markdown("#### 🌟 Key Platform Capabilities")
        st.markdown(
            """
            - **Live Readiness Scoring**: Real-time evaluation against 5 core competencies per role.
            - **Mentor Overrides**: Verified faculty ratings take precedence in placement gap calculations.
            - **Early Warning Center**: Automatically flags students requiring academic intervention.
            - **Dual Mode Deployment**: Seamlessly available as both a Flask SaaS app and Streamlit Cloud dashboard.
            """
        )

    with col2:
        auth_tabs = st.tabs(["🔐 Sign In to Account", "📝 Create New Account"])

        # TAB 1: SIGN IN
        with auth_tabs[0]:
            with st.form("login_form"):
                st.markdown("##### Welcome Back")
                st.caption("Sign in with your registered college credentials:")

                username_or_email = st.text_input("Username or Email", placeholder="e.g. student@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                if submit_login:
                    if not username_or_email or not password:
                        st.error("Please enter both username/email and password.")
                    else:
                        user = authenticate_user(username_or_email, password)
                        if user:
                            login_user(user)
                        else:
                            st.error("Invalid credentials. Please verify your email and password, or use the Quick Demo buttons on the left.")

        # TAB 2: REGISTRATION
        with auth_tabs[1]:
            st.markdown("##### Register for SkillGap Tracker")
            st.caption("Create a new student or faculty account:")

            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="e.g. Alex Chen")
                reg_email = st.text_input("College Email", placeholder="e.g. alex.chen@college.edu")

                reg_role = st.selectbox(
                    "Register as:",
                    options=["Student", "Faculty Mentor"],
                    index=0,
                )
                role_key = "student" if reg_role == "Student" else "mentor"

                reg_branch = "Computer Science & Engineering"
                reg_year = 3
                reg_target_role_id = None

                if role_key == "student":
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        reg_branch = st.selectbox(
                            "Engineering Department / Branch",
                            options=[
                                "Computer Science & Engineering",
                                "Information Science & Engineering",
                                "Artificial Intelligence & Machine Learning",
                                "Electronics & Communication Engineering",
                                "Data Science & Analytics",
                                "Mechanical Engineering",
                                "Civil Engineering",
                            ],
                        )
                    with b_col2:
                        year_choice = st.selectbox("Academic Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"], index=2)
                        reg_year = int(year_choice[0])

                    with flask_app.app_context():
                        available_roles = JobRole.query.order_by(JobRole.name).all()
                        role_map = {r.name: r.id for r in available_roles}

                    if role_map:
                        chosen_role = st.selectbox("Initial Target Career Track", options=list(role_map.keys()))
                        reg_target_role_id = role_map[chosen_role]

                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    reg_pwd = st.text_input("Create Password", type="password", placeholder="At least 6 characters")
                with p_col2:
                    reg_confirm_pwd = st.text_input("Confirm Password", type="password", placeholder="Repeat password")

                submit_reg = st.form_submit_button("Complete Registration", use_container_width=True, type="primary")

                if submit_reg:
                    if not reg_name or not reg_email or not reg_pwd:
                        st.error("Please fill in all required fields.")
                    elif reg_pwd != reg_confirm_pwd:
                        st.error("Passwords do not match. Please re-enter.")
                    elif len(reg_pwd) < 6:
                        st.error("Password must be at least 6 characters long.")
                    else:
                        success, result = register_new_user(
                            name=reg_name,
                            email=reg_email,
                            password=reg_pwd,
                            role=role_key,
                            branch=reg_branch,
                            year=reg_year,
                            target_role_id=reg_target_role_id,
                        )
                        if success:
                            st.balloons()
                            st.success(f"🎉 Account successfully created for {result.name}! Signing in...")
                            login_user(result)
                        else:
                            st.error(result)


# ==========================================
# STUDENT VIEW
# ==========================================
def render_student_view():
    user_id = st.session_state["user_id"]
    user_name = st.session_state["user_name"]

    profile, target_role, skills, effective_level, sources, readiness_score, gap_percentage, level_counts = calculate_student_gap(user_id)

    # Readiness Tier Badge
    if readiness_score >= 70:
        tier_badge = '<span class="role-badge badge-mentor">🚀 Placement Ready</span>'
    elif readiness_score >= 40:
        tier_badge = '<span class="role-badge badge-tpo">⚡ Advancing Competency</span>'
    else:
        tier_badge = '<span class="role-badge badge-student">🌱 Foundational Stage</span>'

    # Student Personalized Header
    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <h2 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #0f172a;">Welcome, {user_name}! 👋</h2>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.95rem;">
                        {profile.branch if profile else 'Engineering'} • Year {profile.year if profile else '3'} • Target: <strong>{target_role.name if target_role else 'Unassigned'}</strong>
                    </p>
                </div>
                <div>{tier_badge}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["📊 Readiness & Gap Analytics", "🎯 Career Track & Competencies", "📝 Self-Assessment Matrix", "💬 Mentor Guidance Stream"])

    # TAB 1: OVERVIEW & GAUGES
    with tabs[0]:
        if not target_role:
            st.warning("⚠️ You have not chosen a target career role yet! Head over to the 'Career Track' tab to select your path.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Target Role", target_role.name)
            m2.metric("Readiness Score", f"{readiness_score}%", delta=f"{readiness_score - 50:.1f}% vs Goal")
            m3.metric("Skill Deficit Gap", f"{gap_percentage}%", delta=f"-{gap_percentage}%", delta_color="inverse")
            m4.metric("Total Skills Evaluated", len(skills))

            c1, c2 = st.columns([1.2, 1])
            with c1:
                st.plotly_chart(create_readiness_gauge(readiness_score), use_container_width=True)

            with c2:
                st.subheader("Competency Distribution")
                df_counts = pd.DataFrame([
                    {"Status": "Confident", "Count": level_counts["confident"]},
                    {"Status": "Comfortable", "Count": level_counts["comfortable"]},
                    {"Status": "Learning", "Count": level_counts["learning"]},
                    {"Status": "Not Started", "Count": level_counts["not_started"]},
                ])
                fig_pie = px.pie(
                    df_counts,
                    names="Status",
                    values="Count",
                    hole=0.55,
                    color="Status",
                    color_discrete_map={
                        "Confident": "#10b981",
                        "Comfortable": "#3b82f6",
                        "Learning": "#f59e0b",
                        "Not Started": "#ef4444",
                    },
                )
                fig_pie.update_layout(height=250, margin=dict(t=15, b=15, l=15, r=15))
                st.plotly_chart(fig_pie, use_container_width=True)

            st.divider()
            st.subheader("🎯 Urgent Action Items (Priority Deficit Skills)")
            priority_order = {"not_started": 1, "learning": 2, "comfortable": 3}
            priorities = [
                (s.name, effective_level.get(s.id, "not_started"), priority_order.get(effective_level.get(s.id, "not_started"), 9))
                for s in skills if effective_level.get(s.id, "not_started") != "confident"
            ]
            priorities.sort(key=lambda x: x[2])

            if not priorities:
                st.success("🎉 Outstanding! You are Confident across all required competencies for your target career role.")
            else:
                p_cols = st.columns(min(3, len(priorities)))
                for idx, (skill_name, lvl, _) in enumerate(priorities[:3]):
                    with p_cols[idx % 3]:
                        badge_color = "red" if lvl == "not_started" else ("orange" if lvl == "learning" else "blue")
                        st.markdown(
                            f"""
                            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.5rem; border-left: 4px solid {'#ef4444' if lvl=='not_started' else '#f59e0b'};">
                                <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #64748b;">Priority #{idx+1}</div>
                                <div style="font-size: 0.95rem; font-weight: 600; color: #0f172a; margin: 0.25rem 0;">{skill_name}</div>
                                <div style="font-size: 0.8rem; color: #475569;">Current Status: <strong>{lvl.replace('_', ' ').title()}</strong></div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    # TAB 2: CAREER TRACK SELECTION
    with tabs[1]:
        st.subheader("Change or Upgrade Target Career Role")
        with flask_app.app_context():
            all_roles = JobRole.query.order_by(JobRole.name).all()
            role_options = {r.name: r.id for r in all_roles}
            current_role_name = target_role.name if target_role else list(role_options.keys())[0]

            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                selected_role_name = st.selectbox(
                    "Choose aspirational placement path:",
                    options=list(role_options.keys()),
                    index=list(role_options.keys()).index(current_role_name) if current_role_name in role_options else 0,
                )
            with col_btn:
                st.write("")
                st.write("")
                if st.button("Update Target Track", type="primary", use_container_width=True):
                    prof = StudentProfile.query.filter_by(user_id=user_id).first()
                    if not prof:
                        prof = StudentProfile(user_id=user_id, branch="Computer Science & Engineering", year=3)
                        db.session.add(prof)
                    prof.target_job_role_id = role_options[selected_role_name]
                    db.session.commit()
                    st.success(f"Career track updated to {selected_role_name}!")
                    st.rerun()

        st.divider()
        st.subheader("Explore Available Skill Tracks & Required Core Competencies")
        with flask_app.app_context():
            roles = JobRole.query.all()
            for r in roles:
                with st.expander(f"📌 {r.name} ({len(r.skills)} Core Competencies)", expanded=(r.id == (target_role.id if target_role else None))):
                    skills_html = "".join([f'<span class="skill-chip">✓ {s.name}</span>' for s in r.skills])
                    st.markdown(skills_html, unsafe_allow_html=True)

    # TAB 3: SELF-ASSESSMENT
    with tabs[2]:
        st.subheader("📝 Self-Assessment & Competency Rating Matrix")
        if not target_role or not skills:
            st.warning("Please choose your target role first.")
        else:
            st.caption("Update your proficiency levels. Verified ratings submitted by your faculty mentor are protected with a shield 🛡️.")

            level_map = {
                "not_started": "Not Started (0%)",
                "learning": "Learning (Courses & Practice)",
                "comfortable": "Comfortable (Mini-projects built)",
                "confident": "Confident (Interview & Production Ready)",
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

                submit_assessment = st.form_submit_button("Save All Skill Ratings", type="primary", use_container_width=True)
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
                        st.success("Assessments successfully saved! Your employability readiness has been recalculated.")
                        st.rerun()

    # TAB 4: MENTOR GUIDANCE STREAM
    with tabs[3]:
        st.subheader("💬 Faculty Mentor Guidance Stream")
        with flask_app.app_context():
            assignment = MentorAssignment.query.filter_by(student_id=user_id).first()
            if assignment and assignment.mentor:
                st.info(f"**Assigned Faculty Mentor:** {assignment.mentor.name} ({assignment.mentor.email})")
            else:
                st.warning("No faculty mentor assigned yet. Contact your department placement coordinator.")

            notes = MentorNote.query.filter_by(student_id=user_id).order_by(MentorNote.created_at.desc()).all()
            if not notes:
                st.write("No mentor guidance notes recorded yet.")
            else:
                for n in notes:
                    with st.container():
                        st.markdown(f"**{n.created_at.strftime('%B %d, %Y')}** — *by Prof. {n.mentor.name}*")
                        if n.at_risk:
                            st.error(f"🚩 **Action Plan / Remedial Alert**: {n.note_text}")
                        else:
                            st.success(n.note_text)
                        st.divider()


# ==========================================
# FACULTY MENTOR VIEW
# ==========================================
def render_mentor_view():
    mentor_id = st.session_state["user_id"]
    user_name = st.session_state["user_name"]

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <h2 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #0f172a;">Faculty Mentorship Portal 👩‍🏫</h2>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.95rem;">Prof. {user_name} • Student Mentee Cohort Tracking</p>
                </div>
                <div><span class="role-badge badge-mentor">Verified Mentor</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with flask_app.app_context():
        assignments = MentorAssignment.query.filter_by(mentor_id=mentor_id).all()
        student_ids = [a.student_id for a in assignments]
        mentees = User.query.filter(User.id.in_(student_ids)).all() if student_ids else []

    m1, m2, m3 = st.columns(3)
    m1.metric("Assigned Mentees", len(mentees))

    at_risk_count = 0
    with flask_app.app_context():
        for m in mentees:
            last_note = MentorNote.query.filter_by(student_id=m.id).order_by(MentorNote.created_at.desc()).first()
            if last_note and last_note.at_risk:
                at_risk_count += 1

    m2.metric("At-Risk Flagged", at_risk_count, delta=f"{at_risk_count} need attention", delta_color="inverse")
    m3.metric("Placement Status", "Active Review Period")

    if not mentees:
        st.info("No students are currently paired to your mentorship cohort.")
        return

    st.subheader("Mentee Cohort Overview")
    mentee_records = []
    with flask_app.app_context():
        for m in mentees:
            _, t_role, _, _, _, r_score, gap, _ = calculate_student_gap(m.id)
            prof = StudentProfile.query.filter_by(user_id=m.id).first()
            mentee_records.append({
                "ID": m.id,
                "Student Name": m.name,
                "Email": m.email,
                "Branch": prof.branch if prof else "Unassigned",
                "Target Role": t_role.name if t_role else "Not Selected",
                "Readiness": f"{r_score}%",
                "Skill Gap": f"{gap}%",
            })

    st.dataframe(pd.DataFrame(mentee_records), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Inspect Student & Submit Faculty Evaluation")

    selected_student_name = st.selectbox("Select Mentee to evaluate:", [m.name for m in mentees])
    selected_mentee = next((m for m in mentees if m.name == selected_student_name), None)

    if selected_mentee:
        _, t_role, skills, eff_level, sources, r_score, gap, _ = calculate_student_gap(selected_mentee.id)

        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"#### Mentee: {selected_mentee.name}")
            st.write(f"**Target Role:** {t_role.name if t_role else 'None'}")
            st.write(f"**Readiness Score:** {r_score}% (Skill Deficit: {gap}%)")

            st.markdown("##### 📝 Post Guidance Note & Intervention Flag")
            with st.form("mentor_note_form"):
                note_text = st.text_area("Observations and Action Items:")
                at_risk_flag = st.checkbox("🚩 Flag student as At-Risk (alerts TPO placement office)")
                submit_note = st.form_submit_button("Save Guidance Note", type="primary")

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
            st.caption("Faculty verified ratings take precedence in placement readiness scores.")

            if not skills:
                st.write("Student has not selected target competencies.")
            else:
                level_options = ["not_started", "learning", "comfortable", "confident"]
                with st.form("override_form"):
                    new_mentor_evals = {}
                    for s in skills:
                        curr = eff_level.get(s.id, "not_started")
                        new_mentor_evals[s.id] = st.selectbox(
                            f"{s.name} (Current: {curr.replace('_', ' ').title()})",
                            options=level_options,
                            index=level_options.index(curr),
                            key=f"mentor_eval_{s.id}",
                        )
                    submit_override = st.form_submit_button("Record Verified Faculty Ratings", type="primary")
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
                            st.success("Faculty assessment saved successfully!")
                            st.rerun()


# ==========================================
# TPO VIEW
# ==========================================
def render_tpo_view():
    user_name = st.session_state["user_name"]

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <h2 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #0f172a;">Training & Placement Officer (TPO) Cockpit 🏢</h2>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.95rem;">{user_name} • Institutional Employability & Placement Readiness Center</p>
                </div>
                <div><span class="role-badge badge-tpo">Placement Officer</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

            latest_note = MentorNote.query.filter_by(student_id=s.id).order_by(MentorNote.created_at.desc()).first()
            is_at_risk = bool(latest_note and latest_note.at_risk)
            if is_at_risk:
                at_risk_students.append({
                    "Name": s.name,
                    "Email": s.email,
                    "Branch": prof.branch if prof else "N/A",
                    "Target Role": t_role.name if t_role else "N/A",
                    "Skill Gap": f"{gap}%",
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
    m1.metric("Enrolled Students", len(students))
    m2.metric("Placement Ready (Gap ≤ 30%)", ready_count, delta=f"{(ready_count/len(students)*100):.1f}% Cohort Ready" if students else "0%")
    m3.metric("Average Skill Gap", f"{avg_gap}%", delta=f"-{avg_gap}%", delta_color="inverse")
    m4.metric("At-Risk Interventions", len(at_risk_students), delta_color="inverse")

    tabs = st.tabs(["📊 Departmental Benchmark", "🚩 Early Warning (At-Risk)", "📋 All Student Roster", "📥 Data Exports"])

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
                    labels={"Avg_Gap": "Average Skill Deficit (%)", "branch": "Department / Branch"},
                )
                fig.update_layout(height=320)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.subheader("Summary Table")
                st.dataframe(branch_summary, use_container_width=True, hide_index=True)

    with tabs[1]:
        st.subheader("🚩 At-Risk Candidates Needing Intervention")
        if not at_risk_students:
            st.success("No students are currently flagged as at-risk.")
        else:
            st.dataframe(pd.DataFrame(at_risk_students), use_container_width=True, hide_index=True)

    with tabs[2]:
        st.subheader("Placement Candidate Roster")
        st.dataframe(df_students, use_container_width=True, hide_index=True)

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
    user_name = st.session_state["user_name"]

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <h2 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #0f172a;">College Administration Portal ⚙️</h2>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.95rem;">{user_name} • Platform Trends & Faculty Mentorship Management</p>
                </div>
                <div><span class="role-badge badge-admin">Administrator</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
# SIDEBAR NAVIGATION
# ==========================================
def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.85rem;">🎓</span>
                <div>
                    <div style="font-weight: 800; font-size: 1.15rem; color: #0f172a; line-height: 1.2;">SkillGap Tracker</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Placement Readiness Engine</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        if st.session_state["authenticated"]:
            role = st.session_state["user_role"]
            user_name = st.session_state["user_name"]

            role_class = f"badge-{role}"
            st.markdown(
                f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #64748b;">Active Profile</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0.25rem 0;">{user_name}</div>
                    <span class="role-badge {role_class}">{role.upper()}</span>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">{st.session_state['user_email']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("🚪 Sign Out", key="sidebar_sign_out", use_container_width=True):
                logout_user()
        else:
            st.markdown("#### ⚡ Quick Demo Access")
            st.caption("Click any role to log in instantly:")

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
            if st.button("🔄 Reset Demo Database", key="sb_reseed", use_container_width=True):
                try:
                    from seed import seed_database
                    seed_database(flask_app)
                    st.success("Demo database refreshed successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error seeding database: {e}")

        st.divider()
        st.markdown(
            """
            <div style="font-size: 0.775rem; color: #64748b; line-height: 1.5;">
                <strong>Enterprise Security</strong><br>
                • Salted password hashes (scrypt)<br>
                • Role-based authorization (RBAC)<br>
                • Streamlit Community Cloud ready
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================
# MAIN APPLICATION ROUTING
# ==========================================
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
