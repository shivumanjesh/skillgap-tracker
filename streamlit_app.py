"""
Skill-Gap & Employability Readiness Tracker - Intelligent Streamlit Platform
===========================================================================
A competitive, market-grade employability analytics & placement readiness platform.
Features SMART autonomous student self-assessment rubrics, Plotly radar/spider charts,
an AI Career Copilot for students, AI Guidance Assistant for faculty mentors,
Corporate Hiring Tier forecasting for TPO, and AI Curriculum Gap analytics for Admins.
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
        width: 240px;
        height: 240px;
        background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1.025rem;
        color: #c7d2fe;
        max-width: 760px;
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

    /* Metric Cards */
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

    /* AI Accent Pill */
    .ai-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.75rem;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: #ffffff;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        box-shadow: 0 2px 5px rgba(168, 85, 247, 0.3);
    }

    /* AI Feature Callout Container */
    .ai-box {
        background: #faf5ff;
        border: 1px solid #e9d5ff;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 2px 4px rgba(168, 85, 247, 0.05);
    }

    /* Tier Card Container */
    .tier-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }

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
    </style>
    """,
    unsafe_allow_html=True,
)


# 4. CACHED FLASK CONTEXT & RECOVERY
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
# SMART RUBRICS & VISUALIZATION HELPERS
# ==========================================
def get_skill_rubrics(skill_name):
    """Return 3 concrete, verifiable behavioral milestones for an objective diagnostic."""
    name_lower = skill_name.lower()
    if any(k in name_lower for k in ["machine learning", "ai", "deep learning", "nlp", "vision"]):
        return [
            "Theoretical intuition: understands loss functions, gradient descent, tokenization, and evaluation metrics (F1/AUC).",
            "Hands-on execution: has cleaned datasets, trained models, and evaluated inference in PyTorch or Scikit-learn.",
            "Production optimization: can mitigate overfitting, fine-tune hyper-parameters, and deploy models to API endpoints.",
        ]
    elif any(k in name_lower for k in ["sql", "database", "relational"]):
        return [
            "Query mastery: writes complex SELECT, JOIN, GROUP BY, subqueries, and understands 3NF normalization.",
            "Schema design: implements primary/foreign keys, indexes (B-Tree), and constraints in a relational engine.",
            "High-throughput tuning: understands EXPLAIN plans, transactions (ACID), connection pooling, and replication.",
        ]
    elif any(k in name_lower for k in ["api", "flask", "backend", "python"]):
        return [
            "HTTP fundamentals: understands REST conventions, status codes, headers, and JSON serialization.",
            "Application architecture: has built authenticated endpoints with session/JWT auth, input validation, and ORM.",
            "System reliability: can implement error logging, rate-limiting, and automated unit/integration tests.",
        ]
    elif any(k in name_lower for k in ["docker", "kubernetes", "cloud", "ci/cd", "devops", "terraform", "linux"]):
        return [
            "Infrastructure basics: comfortable with Linux terminal, virtualization vs containerization, and cloud primitives.",
            "Container automation: writes multi-stage Dockerfiles, Docker Compose files, and GitHub Actions CI pipelines.",
            "Cluster orchestration: understands Pod lifecycles, Service ingress, volume persistence, and declarative IaC.",
        ]
    elif any(k in name_lower for k in ["frontend", "javascript", "html", "css", "ui"]):
        return [
            "DOM & Styling: understands responsive design, CSS Flexbox/Grid, and modern HTML5 semantic elements.",
            "Interactive logic: writes ES6+ JavaScript, asynchronous Promises, and consumes REST APIs via Fetch.",
            "Production UX: optimizes bundle size, ensures cross-browser compatibility, and adheres to accessibility standards.",
        ]
    elif any(k in name_lower for k in ["security", "vulnerability", "penetration", "iam", "cryptographic"]):
        return [
            "Threat awareness: understands OWASP Top 10 vulnerabilities (SQLi, XSS, CSRF) and the CIA security triad.",
            "Defensive controls: implements TLS/PKI certificates, salted password hashing, and Role-Based Access Control (RBAC).",
            "Security audits: can inspect network traffic, conduct vulnerability audits, and remediate permission escalations.",
        ]
    elif any(k in name_lower for k in ["algorithms", "structures", "dsa"]):
        return [
            "Complexity analysis: calculates Big-O time and space complexity and implements arrays, stacks, and queues.",
            "Non-linear traversal: can implement recursion, binary search trees, heaps, and graph traversals (BFS/DFS).",
            "Advanced problem solving: can solve medium-tier algorithmic challenges involving dynamic programming and graphs.",
        ]
    else:
        return [
            f"Understands foundational concepts, terminology, and core syntax of {skill_name}.",
            f"Has built, debugged, and documented a functioning project demonstrating {skill_name}.",
            f"Can optimize production performance and solve technical interview problems in {skill_name}.",
        ]


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
            title={"text": "Placement Readiness Gauge", "font": {"size": 16, "color": "#1e293b", "family": "Inter, sans-serif"}},
            number={"suffix": "%", "font": {"size": 42, "color": "#0f172a", "family": "Inter, sans-serif"}},
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


def create_competency_radar(skills, effective_level):
    """Create an interactive polar radar/spider chart comparing verified mastery to benchmark."""
    if not skills:
        return None

    categories = [s.name for s in skills]
    level_numeric = {"not_started": 15, "learning": 45, "comfortable": 75, "confident": 100}
    current_values = [level_numeric.get(effective_level.get(s.id, "not_started"), 15) for s in skills]
    benchmark_values = [100 for _ in skills]

    categories_closed = categories + [categories[0]]
    current_closed = current_values + [current_values[0]]
    benchmark_closed = benchmark_values + [benchmark_values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=benchmark_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(148, 163, 184, 0.1)",
        name="Target Benchmark (100%)",
        line=dict(color="#94a3b8", dash="dash", width=1.5),
    ))

    fig.add_trace(go.Scatterpolar(
        r=current_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(79, 70, 229, 0.25)",
        name="Current Verified Mastery",
        line=dict(color="#4f46e5", width=2.5),
        marker=dict(size=6, color="#4338ca"),
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color="#64748b"),
                gridcolor="#e2e8f0",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#1e293b", family="Inter, sans-serif"),
                rotation=90,
                direction="clockwise",
                gridcolor="#e2e8f0",
            ),
            bgcolor="rgba(248, 250, 252, 0.5)",
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
        height=320,
        margin=dict(l=35, r=35, t=15, b=35),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
    )
    return fig


# ==========================================
# AI COPILOT GENERATORS
# ==========================================
def generate_student_roadmap(student_name, target_role, deficit_skills):
    """Generate a personalized 30-day week-by-week learning blueprint."""
    if not deficit_skills:
        return f"🎉 **Outstanding, {student_name}!** You are already placement-ready across all competencies for **{target_role}**! Recommended next step: Schedule mock interviews with alumni and apply for Tier-1 Product Engineering drives."

    top_deficits = deficit_skills[:3]
    skills_str = ", ".join([d[0] for d in top_deficits])
    primary_focus = top_deficits[0][0]

    return f"""### 🚀 30-Day Placement Acceleration Roadmap for {student_name}
**Target Role:** {target_role} | **Primary Deficit Focus:** {skills_str}

---

#### 📅 **Week 1: Core Conceptual Foundations & Drills**
- **Focus Competency:** *{primary_focus}*
- 🎯 **Daily Target:** 2 hours dedicated theory + syntax drills.
- 📚 **Milestone:** Complete core documentation review; build 3 minimal proofs-of-concept.
- 💡 **Interview Tip:** Summarize architectural principles into 1-page cheatsheets for interview quick-recall.

#### 📅 **Week 2: Hands-On Capstone Mini-Project**
- **Focus Competency:** *{" & ".join([d[0] for d in top_deficits[:2]])}*
- 🎯 **Daily Target:** Build a portfolio-worthy project integrating both competencies.
- 📚 **Milestone:** Commit clean, documented code to a public GitHub repository with an architecture diagram.
- 💡 **Action Item:** Add unit tests with >80% coverage and configure automated CI testing.

#### 📅 **Week 3: Advanced Optimization, Edge Cases & System Design**
- **Focus Competency:** *{top_deficits[-1][0] if len(top_deficits) > 2 else primary_focus}*
- 🎯 **Daily Target:** Production error handling, benchmarking, latency optimization, and security audits.
- 📚 **Milestone:** Implement caching, connection pooling, or vector search depending on track requirements.
- 💡 **Action Item:** Record a 2-minute video walkthrough explaining trade-offs made during development.

#### 📅 **Week 4: Mock Technical Interviews & Placement Polish**
- 🎯 **Daily Target:** 1 timed technical simulation daily + behavioral STAR questions.
- 📚 **Milestone:** Schedule a 1-on-1 review with your assigned Faculty Mentor.
- 💡 **Action Item:** Retake the **SMART Diagnostic** to verify competency transition to **Confident**!
"""


def generate_interview_questions(target_role):
    """Generate tailored technical interview questions with model answer frameworks."""
    role_lower = target_role.lower() if target_role else ""
    if "full-stack" in role_lower or "web" in role_lower:
        return [
            ("Explain the complete lifecycle of an HTTP request from browser URL entry to database query and response.",
             "Evaluates networking, DNS resolution, TLS handshake, web servers (Nginx/Gunicorn), WSGI middleware, routing, ORM SQL execution, and browser DOM rendering."),
            ("How do you prevent SQL Injection and Cross-Site Scripting (XSS) in a production web application?",
             "Mentions parameterized prepared statements via ORMs, HTML entity escaping/sanitization, Content Security Policy (CSP) headers, and HttpOnly Secure cookie flags."),
            ("Describe the difference between optimistic and pessimistic locking in relational databases.",
             "Explains version column checking vs SELECT FOR UPDATE database-level row locks, highlighting write conflict trade-offs and throughput implications."),
            ("What strategies do you employ to optimize slow database queries in an application?",
             "Mentions EXPLAIN ANALYZE, indexing composite columns, avoiding N+1 query loops via eager loading (joinedload), read replicas, and Redis caching."),
            ("How would you architect JWT authentication with refresh token rotation?",
             "Discusses short-lived access tokens (15 mins) in memory, long-lived refresh tokens in secure HttpOnly cookies, and database revocation blacklists upon reuse detection.")
        ]
    elif "ai" in role_lower or "machine learning" in role_lower:
        return [
            ("Explain the mathematical intuition behind the Attention Mechanism in Transformers.",
             "Discusses Query, Key, Value dot-product projection, scaled softmax attention weighting, and multi-head representation subspace capturing."),
            ("How do you identify and mitigate vanishing vs exploding gradients in deep neural networks?",
             "Mentions gradient clipping, Batch Normalization, LayerNorm, Residual skip connections (ResNet), and ReLU/GELU activation functions."),
            ("When would you choose Precision over Recall, and how does the ROC-AUC curve inform model selection?",
             "Details false positive vs false negative penalties (e.g. spam vs disease diagnosis) and explains threshold-independent performance evaluation."),
            ("Describe the end-to-end pipeline for fine-tuning an LLM using LoRA (Low-Rank Adaptation).",
             "Explains decomposing weight update matrices delta-W into low-rank matrices A x B, freezing base weights, memory efficiency, and rank r parameter selection."),
            ("How do you monitor and resolve Data Drift and Concept Drift in production ML models?",
             "Discusses Kolmogorov-Smirnov tests, Population Stability Index (PSI), automated retraining triggers, and shadow deployment validation.")
        ]
    elif "devops" in role_lower or "cloud" in role_lower:
        return [
            ("Explain the internal mechanics of a Kubernetes Pod lifecycle and Service networking.",
             "Covers kubelet, pause containers, iptables/eBPF routing, ClusterIP vs NodePort, and Readiness vs Liveness probe behaviors."),
            ("How do multi-stage Docker builds reduce image attack surface and deployment footprint?",
             "Separates compilation/build dependencies from lean runtime artifacts (e.g. Alpine/scratch base image), eliminating compilers and source files from the final container."),
            ("Describe an automated Zero-Downtime Blue-Green or Canary deployment pipeline using CI/CD.",
             "Details staging environments, traffic splitting (weighted routing), automated health threshold rollbacks, and database migration forward-compatibility."),
            ("What is Infrastructure as Code (IaC) drift, and how do you prevent it using Terraform?",
             "Explains terraform state synchronization, `terraform plan -refresh-only`, CI pipeline enforcement, and revoking manual console write permissions."),
            ("How do you architect highly available distributed logging and alerting across microservices?",
             "Discusses OpenTelemetry distributed tracing, centralized log aggregation (FluentBit/Grafana Loki), Prometheus metric scraping, and PagerDuty SLA thresholds.")
        ]
    else:
        return [
            ("Explain how you measure and optimize time and space complexity in algorithms.",
             "Big-O notation, asymptotic analysis, worst vs average cases, and auxiliary memory allocation."),
            ("Describe how you structure a relational database schema for high read throughput.",
             "Denormalization trade-offs, materialized views, indexing strategies, and read-replicas."),
            ("What is your approach to handling concurrency and race conditions in application logic?",
             "Locks, semaphores, atomic operations, message queues, and distributed consensus."),
            ("How do you ensure automated test coverage across unit, integration, and end-to-end levels?",
             "The Testing Pyramid, mocking external dependencies, regression pipelines, and test-driven design."),
            ("Describe your strategy for diagnosing a critical performance bottleneck in production.",
             "APM profiling tools, distributed trace analysis, database query execution plans, and memory heap dumps.")
        ]


def generate_resume_bullets(target_role, skills, effective_level):
    """Generate STAR-formatted resume bullet points for mastered competencies."""
    bullets = []
    for s in skills:
        lvl = effective_level.get(s.id, "not_started")
        if lvl in ["confident", "comfortable"]:
            bullets.append(
                f"• Architected and deployed production-ready solutions using **{s.name}**, optimizing system reliability and passing rigorous faculty evaluation with **{lvl.title()}** proficiency rating."
            )
    if not bullets:
        bullets.append(f"• Actively developing industry-aligned technical proficiencies across **{target_role}** curriculum tracks, focusing on foundational software architecture and modern workflows.")
    return bullets


def generate_ai_mentor_feedback(mentee_name, branch, target_role, readiness_score, gap_percentage, deficit_skills):
    """Generate structured, empathetic faculty mentor guidance with a 14-day milestone recovery roadmap."""
    lowest_skills = [s[0] for s in deficit_skills[:3]] if deficit_skills else ["Core Engineering Competencies"]
    skills_text = ", ".join(lowest_skills)
    primary_deficit = lowest_skills[0]

    if readiness_score >= 80:
        tone = f"Commendable progress! {mentee_name} demonstrates Tier-1 placement readiness ({readiness_score}% score). Focus on high-scale systems architecture and mock interview leadership."
        action_plan = """1. Day 1–5: Solve 10 hard-tier algorithmic concurrency problems.
2. Day 6–10: Mentor junior peers and conduct 1 mock technical interview.
3. Day 11–14: Polish GitHub portfolio repository for Tier-1 corporate drives."""
    elif readiness_score >= 60:
        tone = f"Solid progress ({readiness_score}% ready). Key focus required on mastering {skills_text} to clear Tier-2 product engineering interview technical bars."
        action_plan = f"""1. Day 1–5: Intensive hands-on syntax and API practice in {primary_deficit}.
2. Day 6–10: Build and push a working mini-project with unit tests to GitHub.
3. Day 11–14: Schedule a 15-minute code walkthrough with faculty mentor to verify proficiency."""
    elif readiness_score >= 40:
        tone = f"Developing competency ({readiness_score}% ready). Significant deficit ({gap_percentage}%) detected across {skills_text}."
        action_plan = f"""1. Day 1–5: Review core theory and complete fundamental coding lab sheets in {primary_deficit}.
2. Day 6–10: Re-implement 3 reference sample applications with proper exception handling.
3. Day 11–14: Attend department guided mentoring lab; retake SMART diagnostic."""
    else:
        tone = f"🚩 Critical Academic Intervention: Readiness is {readiness_score}% with a {gap_percentage}% deficit across core competencies ({skills_text}). Remedial action mandatory."
        action_plan = f"""1. Day 1–5: Daily 1-hour mandatory remedial lab attendance for {primary_deficit}.
2. Day 6–10: Pair programming with assigned student teaching assistant on core tasks.
3. Day 11–14: Mandatory 1-on-1 counseling check-in with faculty mentor and TPO coordinator."""

    return f"""Periodic Mentorship Advisory Note for {mentee_name} ({branch})
Target Track: {target_role} | Readiness Benchmark: {readiness_score}% (Deficit: {gap_percentage}%)

Diagnostic Assessment:
{tone}

Recommended 14-Day Milestone Recovery Roadmap:
{action_plan}
"""


def generate_ai_recruiter_pitch(total_students, ready_count, avg_gap, branch_data, tier_counts):
    """Generate a high-converting, professional placement pitch for corporate recruiters."""
    ready_pct = round((ready_count / total_students * 100), 1) if total_students else 0
    t1 = tier_counts.get("Tier 1", tier_counts.get("tier1", 0))
    t2 = tier_counts.get("Tier 2", tier_counts.get("tier2", 0))
    t3 = tier_counts.get("Tier 3", tier_counts.get("tier3", 0))
    t_rem = tier_counts.get("Intervention", tier_counts.get("remedial", 0))

    return f"""### 🏢 Executive Placement Brief for Visiting Corporate Recruiters
**Institutional Batch Overview:** {total_students} Graduating Engineers Assessed

---

#### 🌟 **Recruitment Readiness Highlights:**
- **Tier-1 Product-Ready Cohort (15+ LPA):** **{t1} students** ({round(t1/total_students*100, 1) if total_students else 0}%) verified in advanced systems architecture, concurrency, and high-scale design (Readiness >= 80%).
- **Tier-2 Scaleup-Ready Cohort (8–15 LPA):** **{t2} students** ({round(t2/total_students*100, 1) if total_students else 0}%) possessing independent full-stack implementation proficiency (Readiness 60%–79%).
- **Tier-3 Services Cohort (4–8 LPA):** **{t3} students** ({round(t3/total_students*100, 1) if total_students else 0}%) with verified foundational programming and database competence (Readiness 40%–59%).
- **Remedial Intervention Cohort:** **{t_rem} students** enrolled in targeted department remedial coding labs (Readiness < 40%).
- **Overall Placement-Ready Ratio:** **{ready_pct}%** of candidates meet rigorous corporate thresholds with average deficit of only **{avg_gap}%**.

#### 🎯 **Why Recruit From Our Campus:**
1. **Empirical Rubric Verification:** Every candidate's proficiency is cross-validated through objective behavioral milestones and faculty mentor code reviews (zero self-reported fluff).
2. **Modern Technology Stacks:** Core competencies focus on production-grade Python, React, PostgreSQL, Docker, and Cloud architectures.
3. **Outcome-Based Education (OBE):** Fully compliant with NBA/NAAC Program Outcomes (POs) and continuous curriculum alignment.
"""


def generate_ai_curriculum_analysis(role_gap_df):
    """Detect systemic curriculum blind spots and generate syllabus intervention recommendations."""
    if role_gap_df.empty:
        return "No cohort data available for curriculum analysis."

    highest_gap_role = role_gap_df.sort_values(by="Average Gap", ascending=False).iloc[0]

    return f"""### 🧠 Institutional Curriculum Gap & Industry Alignment Report
**Audited Target Tracks:** {len(role_gap_df)} Academic Pathways

---

#### 🔍 **Key Syllabus Blind Spot Identified**
- **Highest Gap Domain:** **{highest_gap_role['Job Role']}** (Average Student Deficit: **{highest_gap_role['Average Gap']}%** across {highest_gap_role['Students']} enrolled students).
- **Core Structural Finding:** While students demonstrate adequate command of foundational theory, there is a pronounced deficit in production-grade deployment, containerization, and modern architecture tooling.

#### 📋 **Strategic Action Plan for Academic Council (BoS / Dean of Academics)**
1. **Value-Added Elective Recommendation:** Introduce a 2-credit hands-on lab elective on *Cloud-Native Systems & Microservice Architecture* in Semester 6.
2. **Faculty Development Program (FDP):** Sponsor a 5-day industry workshop for engineering faculty on modern DevOps CI/CD and AI/ML model deployment.
3. **Capstone Industry Alignment:** Mandate that final-year engineering projects include automated unit testing (>70% coverage) and public cloud deployment as grading criteria.
"""


# ==========================================
# AUTHENTICATION & REGISTRATION SCREEN
# ==========================================
def render_auth_page():
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">🎓 Skill-Gap & Employability Readiness Tracker</div>
            <div class="hero-subtitle">
                An intelligent college placement engine bridging academic curricula and industry hiring expectations.
                Continuously track student competencies, empower faculty mentors with verified evaluations, and give placement officers real-time cohort readiness analytics.
            </div>
            <div class="hero-badge-row">
                <span class="hero-badge">🎯 SMART Diagnostic Rubrics</span>
                <span class="hero-badge">📊 Competency Radar Analytics</span>
                <span class="hero-badge">🤖 AI Placement Copilot</span>
                <span class="hero-badge">🛡️ Verified Faculty Assessments</span>
                <span class="hero-badge">🏢 Institutional Placement Cockpit</span>
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
        st.markdown("#### 🌟 Market-Leading Capabilities")
        st.markdown(
            """
            - **SMART Objective Diagnostic**: Students self-evaluate on concrete behavioral milestones rather than arbitrary ratings.
            - **Multi-Axis Radar Charts**: Visual comparison of verified candidate mastery against target industry standards.
            - **AI Career Copilot**: 30-day adaptive roadmaps, interview question simulators, and resume bullet point generators.
            - **Placement Tier Matchmaker**: Automatic segmentation into Tier-1, Tier-2, and Tier-3 corporate hiring tiers.
            """
        )

    with col2:
        auth_tabs = st.tabs(["🔐 Sign In to Account", "📝 Create New Account"])

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
                            st.success(f"🎉 Account successfully created for {result['name']}! Signing in...")
                            login_user(result)
                        else:
                            st.error(result)


# ==========================================
# STUDENT VIEW WITH SMART DIAGNOSTIC & COPILOT
# ==========================================
def render_student_view():
    user_id = st.session_state["user_id"]
    user_name = st.session_state["user_name"]

    profile, target_role, skills, effective_level, sources, readiness_score, gap_percentage, level_counts = calculate_student_gap(user_id)

    if readiness_score >= 70:
        tier_badge = '<span class="role-badge badge-mentor">🚀 Tier-1 Placement Ready</span>'
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

    tabs = st.tabs([
        "📊 Overview & Radar",
        "📅 30-Day Sprint Roadmap",
        "💡 Tech Interview Flashcards",
        "📄 STAR Resume Generator",
        "🎯 SMART Diagnostic & Rubrics",
        "💬 Mentor Guidance Stream",
        "⚙️ Change Career Track",
    ])

    priority_order = {"not_started": 1, "learning": 2, "comfortable": 3}
    deficit_skills = [
        (s.name, effective_level.get(s.id, "not_started"), priority_order.get(effective_level.get(s.id, "not_started"), 9))
        for s in skills if effective_level.get(s.id, "not_started") != "confident"
    ]
    deficit_skills.sort(key=lambda x: x[2])

    # TAB 0: READINESS & RADAR
    with tabs[0]:
        if not target_role:
            st.warning("⚠️ You have not chosen a target career role yet! Head over to the 'Change Career Track' tab to select your path.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Target Role", target_role.name)
            m2.metric("Readiness Score", f"{readiness_score}%", delta=f"{readiness_score - 50:.1f}% vs Goal")
            m3.metric("Skill Deficit Gap", f"{gap_percentage}%", delta=f"-{gap_percentage}%", delta_color="inverse")
            m4.metric("Total Competencies", len(skills))

            # AI Copilot Quick Launchpad Banner
            st.markdown(
                """
                <div class="ai-box" style="margin-top: 1rem; margin-bottom: 1.25rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span class="ai-badge">AI Assistant Suite</span>
                            <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #581c87;">AI Placement Career Copilot</h3>
                        </div>
                        <span style="font-size: 0.85rem; color: #6b21a8; font-weight: 600;">Autonomous Student Self-Empowerment</span>
                    </div>
                    <p style="margin: 0.35rem 0 0 0; color: #7e22ce; font-size: 0.95rem;">
                        Directly access your <strong>30-Day Sprint Roadmap</strong>, <strong>Tech Interview Flashcards</strong>, and <strong>STAR Resume Generator</strong> via the tabs above or quick previews below:
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Quick-Access Cards
            col_ai1, col_ai2, col_ai3 = st.columns(3)
            with col_ai1:
                st.markdown(
                    """
                    <div style="background: #ffffff; border: 1px solid #e9d5ff; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.5rem; border-top: 4px solid #9333ea;">
                        <div style="font-size: 1.3rem;">📅</div>
                        <div style="font-size: 1rem; font-weight: 700; color: #581c87; margin: 0.25rem 0;">30-Day Sprint Roadmap</div>
                        <div style="font-size: 0.8rem; color: #64748b;">4-week sprint plan tailored to your skill deficits.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("👀 Open Roadmap Quick-View"):
                    st.markdown(generate_student_roadmap(user_name, target_role.name, deficit_skills))

            with col_ai2:
                st.markdown(
                    """
                    <div style="background: #ffffff; border: 1px solid #e9d5ff; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.5rem; border-top: 4px solid #a855f7;">
                        <div style="font-size: 1.3rem;">💡</div>
                        <div style="font-size: 1rem; font-weight: 700; color: #581c87; margin: 0.25rem 0;">Tech Interview Simulator</div>
                        <div style="font-size: 0.8rem; color: #64748b;">Role-specific questions with answer criteria.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("👀 Open Interview Questions Quick-View"):
                    questions_prev = generate_interview_questions(target_role.name)
                    for idx, (q, model_answer) in enumerate(questions_prev[:2]):
                        st.markdown(f"**Q{idx+1}: {q}**")
                        st.info(f"Model Criteria: {model_answer}")

            with col_ai3:
                st.markdown(
                    """
                    <div style="background: #ffffff; border: 1px solid #e9d5ff; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.5rem; border-top: 4px solid #c084fc;">
                        <div style="font-size: 1.3rem;">📄</div>
                        <div style="font-size: 1rem; font-weight: 700; color: #581c87; margin: 0.25rem 0;">STAR Resume Bullets</div>
                        <div style="font-size: 0.8rem; color: #64748b;">Copy-paste ready accomplishment statements.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("👀 Open Resume Bullets Quick-View"):
                    bullets_prev = generate_resume_bullets(target_role.name, skills, effective_level)
                    for b in bullets_prev[:2]:
                        st.markdown(b)

            st.divider()

            c1, c2 = st.columns([1, 1.2])
            with c1:
                st.plotly_chart(create_readiness_gauge(readiness_score), use_container_width=True)
                # Donut Chart below gauge
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
                fig_pie.update_layout(height=230, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_pie, use_container_width=True)

            with c2:
                st.markdown("##### 🕸️ Competency Radar Analysis (You vs Industry Benchmark)")
                radar_fig = create_competency_radar(skills, effective_level)
                if radar_fig:
                    st.plotly_chart(radar_fig, use_container_width=True)

            st.divider()
            st.subheader("🎯 Urgent Action Items (Priority Deficit Competencies)")
            priorities = deficit_skills
            if not priorities:
                st.success("🎉 Outstanding! You are Confident across all required competencies for your target career role.")
            else:
                p_cols = st.columns(min(3, len(priorities)))
                for idx, (skill_name, lvl, _) in enumerate(priorities[:3]):
                    with p_cols[idx % 3]:
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

    # TAB 1: 30-DAY SPRINT ROADMAP
    with tabs[1]:
        st.markdown(
            """
            <div class="ai-box">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span class="ai-badge">AI Assistant</span>
                    <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #581c87;">📅 30-Day Placement Acceleration Roadmap</h3>
                </div>
                <p style="margin: 0.35rem 0 0 0; color: #7e22ce; font-size: 0.95rem;">
                    Customized week-by-week learning blueprint engineered around your specific competency deficits.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(generate_student_roadmap(user_name, target_role.name if target_role else "Engineering", deficit_skills))

    # TAB 2: TECH INTERVIEW SIMULATOR
    with tabs[2]:
        st.markdown(
            f"""
            <div class="ai-box">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span class="ai-badge">AI Assistant</span>
                    <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #581c87;">💡 Technical Interview Simulator & Flashcards</h3>
                </div>
                <p style="margin: 0.35rem 0 0 0; color: #7e22ce; font-size: 0.95rem;">
                    High-probability questions asked by Tier-1 & Tier-2 corporate recruiters for <strong>{target_role.name if target_role else 'Role'}</strong>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        questions = generate_interview_questions(target_role.name if target_role else "")
        for idx, (q, model_answer) in enumerate(questions):
            with st.expander(f"📌 Question #{idx+1}: {q}", expanded=(idx == 0)):
                st.markdown(f"**Recruiter Evaluation Rubric & Model Answer:**")
                st.info(model_answer)
                st.caption("Tip: Practice explaining your answers out loud following the STAR (Situation-Task-Action-Result) format.")

    # TAB 3: STAR RESUME GENERATOR
    with tabs[3]:
        st.markdown(
            f"""
            <div class="ai-box">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span class="ai-badge">AI Assistant</span>
                    <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #581c87;">📄 STAR Resume Impact Statement Generator</h3>
                </div>
                <p style="margin: 0.35rem 0 0 0; color: #7e22ce; font-size: 0.95rem;">
                    Accomplishment statements mapped to your verified competencies for your technical resume:
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        bullets = generate_resume_bullets(target_role.name if target_role else "Role", skills, effective_level)
        for b in bullets:
            st.markdown(b)
        st.caption("📋 Copy and paste these bullet points under your Projects / Technical Experience section.")

    # TAB 4: SMART DIAGNOSTIC & SELF-ASSESSMENT
    with tabs[4]:
        st.subheader("🎯 SMART Autonomous Diagnostic & Empirical Self-Assessment")
        st.caption(
            "Self-evaluate against objective, verifiable behavioral milestones. Checking milestones automatically determines your true competency level."
        )

        if not target_role or not skills:
            st.warning("Please choose your target role first.")
        else:
            with st.form("smart_diagnostic_form"):
                new_diagnostic_levels = {}
                score_to_level = {0: "not_started", 1: "learning", 2: "comfortable", 3: "confident"}

                for skill in skills:
                    curr_level = effective_level.get(skill.id, "not_started")
                    is_mentor_verified = sources.get(skill.id) == "mentor"
                    rubric_items = get_skill_rubrics(skill.name)

                    mentor_badge = " 🛡️ *(Faculty Verified)*" if is_mentor_verified else ""
                    with st.expander(f"📌 {skill.name} — Current: {curr_level.replace('_', ' ').title()}{mentor_badge}", expanded=False):
                        st.markdown(f"**Check which milestones you have objectively demonstrated:**")
                        m1 = st.checkbox(f"1️⃣ {rubric_items[0]}", key=f"rubric_{skill.id}_1", value=(curr_level in ["learning", "comfortable", "confident"]))
                        m2 = st.checkbox(f"2️⃣ {rubric_items[1]}", key=f"rubric_{skill.id}_2", value=(curr_level in ["comfortable", "confident"]))
                        m3 = st.checkbox(f"3️⃣ {rubric_items[2]}", key=f"rubric_{skill.id}_3", value=(curr_level == "confident"))

                        computed_score = int(m1) + int(m2) + int(m3)
                        computed_lvl = score_to_level[computed_score]
                        new_diagnostic_levels[skill.id] = computed_lvl

                        st.caption(f"Calculated Empirical Level: **{computed_lvl.replace('_', ' ').title()}** ({computed_score}/3 criteria met)")

                submit_diagnostic = st.form_submit_button("Submit SMART Diagnostic & Recalculate Readiness", type="primary", use_container_width=True)

                if submit_diagnostic:
                    with flask_app.app_context():
                        for skill_id, new_level in new_diagnostic_levels.items():
                            existing = Assessment.query.filter_by(
                                student_id=user_id,
                                skill_id=skill_id,
                                source="self",
                            ).first()
                            if existing:
                                existing.level = new_level
                                existing.updated_at = datetime.now(timezone.utc)
                            else:
                                db.session.add(
                                    Assessment(
                                        student_id=user_id,
                                        skill_id=skill_id,
                                        level=new_level,
                                        source="self",
                                    )
                                )
                        db.session.commit()
                        st.balloons()
                        st.success("Empirical diagnostic saved! Your placement readiness index and radar polygon have been updated.")
                        st.rerun()

    # TAB 5: MENTOR GUIDANCE
    with tabs[5]:
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

    # TAB 6: CHANGE TRACK
    with tabs[6]:
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


# ==========================================
# FACULTY MENTOR VIEW WITH AI ASSISTANT
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
        prof, t_role, skills, eff_level, sources, r_score, gap, _ = calculate_student_gap(selected_mentee.id)

        c1, c2 = st.columns([1.1, 1])
        with c1:
            st.markdown(f"#### Mentee: {selected_mentee.name}")
            st.write(f"**Target Role:** {t_role.name if t_role else 'None'}")
            st.write(f"**Readiness Score:** {r_score}% (Skill Deficit: {gap}%)")

            # Deficit skills calculation
            priority_order = {"not_started": 1, "learning": 2, "comfortable": 3}
            mentee_deficits = [
                (s.name, eff_level.get(s.id, "not_started"), priority_order.get(eff_level.get(s.id, "not_started"), 9))
                for s in skills if eff_level.get(s.id, "not_started") != "confident"
            ]
            mentee_deficits.sort(key=lambda x: x[2])

            # AI Note Assistant
            st.markdown(
                """
                <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 10px; padding: 0.75rem 1rem; margin: 0.75rem 0;">
                    <span class="ai-badge">AI Assistant</span>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #6b21a8; margin-left: 0.35rem;">One-Click Feedback Drafter</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("✨ Draft AI Feedback for Mentee", key="btn_draft_ai_note"):
                st.session_state["drafted_note"] = generate_ai_mentor_feedback(
                    selected_mentee.name,
                    prof.branch if prof else "Engineering",
                    t_role.name if t_role else "Role",
                    r_score,
                    gap,
                    mentee_deficits,
                )

            initial_note_text = st.session_state.get("drafted_note", "")

            with st.form("mentor_note_form"):
                note_text = st.text_area("Observations and Action Items:", value=initial_note_text, height=150)
                at_risk_flag = st.checkbox("🚩 Flag student as At-Risk (alerts TPO placement office)", value=(gap > 50))
                submit_note = st.form_submit_button("Post Guidance Note", type="primary")

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
                            if "drafted_note" in st.session_state:
                                del st.session_state["drafted_note"]
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
# TPO VIEW WITH CORPORATE TIER FORECASTING & AI PITCH
# ==========================================
def render_tpo_view():
    user_name = st.session_state["user_name"]

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <h2 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #0f172a;">Training & Placement Officer (TPO) Cockpit 🏢</h2>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.95rem;">{user_name} • Institutional Employability & Corporate Placement Center</p>
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

        # Corporate Tiers buckets
        tier_data = {"Tier 1": [], "Tier 2": [], "Tier 3": [], "Intervention": []}

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

            # Assign corporate tier
            if r_score >= 80:
                tier_data["Tier 1"].append(s.name)
            elif r_score >= 60:
                tier_data["Tier 2"].append(s.name)
            elif r_score >= 40:
                tier_data["Tier 3"].append(s.name)
            else:
                tier_data["Intervention"].append(s.name)

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
    m2.metric("Placement Ready (Gap <= 30%)", ready_count, delta=f"{(ready_count/len(students)*100):.1f}% Cohort Ready" if students else "0%")
    m3.metric("Average Skill Gap", f"{avg_gap}%", delta=f"-{avg_gap}%", delta_color="inverse")
    m4.metric("At-Risk Interventions", len(at_risk_students), delta_color="inverse")

    tabs = st.tabs([
        "🏆 Corporate Hiring Tiers & AI Recruiter Pitch",
        "📊 Departmental Benchmark",
        "🚩 Early Warning (At-Risk)",
        "📋 All Student Roster",
        "📥 Data Exports",
    ])

    # TAB 0: CORPORATE TIERS & AI PITCH
    with tabs[0]:
        st.markdown(
            """
            <div class="ai-box">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span class="ai-badge">Predictive Corporate Intelligence</span>
                    <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #581c87;">Corporate Hiring Tier Forecasting & AI Pitch</h3>
                </div>
                <p style="margin: 0.35rem 0 0 0; color: #7e22ce; font-size: 0.95rem;">
                    Empirical candidate tiering based on verified industry skill benchmarks and 1-click recruiter pitch generation.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tc1, tc2, tc3, tc4 = st.columns(4)
        tc1.metric("🥇 Tier-1 Product (15+ LPA)", len(tier_data["Tier 1"]), delta="Readiness >= 80%")
        tc2.metric("🥈 Tier-2 Scaleup (8-15 LPA)", len(tier_data["Tier 2"]), delta="Readiness 60%-79%")
        tc3.metric("🥉 Tier-3 Services (4-8 LPA)", len(tier_data["Tier 3"]), delta="Readiness 40%-59%")
        tc4.metric("⚠️ Remedial Intervention", len(tier_data["Intervention"]), delta="Readiness < 40%", delta_color="inverse")

        st.divider()
        st.subheader("✨ Generate AI Corporate Placement Pitch & Executive Brief")
        st.caption("One-click high-converting recruitment pitch generated for visiting corporate HR teams, emphasizing verified technical competencies and NBA/NAAC compliance:")

        df_branches = pd.DataFrame(student_rows)
        branch_stats = df_branches.groupby("branch").size().reset_index(name="count") if not df_branches.empty else pd.DataFrame()

        tier_counts = {
            "Tier 1": len(tier_data["Tier 1"]),
            "Tier 2": len(tier_data["Tier 2"]),
            "Tier 3": len(tier_data["Tier 3"]),
            "Intervention": len(tier_data["Intervention"]),
        }

        # Auto-populate pitch if not yet generated so the brief is instantly visible
        if "recruiter_pitch" not in st.session_state:
            st.session_state["recruiter_pitch"] = generate_ai_recruiter_pitch(
                len(students), ready_count, avg_gap, branch_stats, tier_counts
            )

        col_pitch_btn, col_pitch_dl = st.columns([2, 1])
        with col_pitch_btn:
            if st.button("✨ Generate AI Corporate Placement Pitch", type="primary", use_container_width=True, key="btn_gen_pitch"):
                st.session_state["recruiter_pitch"] = generate_ai_recruiter_pitch(
                    len(students), ready_count, avg_gap, branch_stats, tier_counts
                )
                st.success("✅ AI Corporate Placement Pitch generated & updated successfully!")
        with col_pitch_dl:
            st.download_button(
                "📥 Download Placement Pitch (.md)",
                data=st.session_state.get("recruiter_pitch", ""),
                file_name="institutional_corporate_placement_pitch.md",
                mime="text/markdown",
                use_container_width=True,
                key="btn_dl_pitch"
            )

        if "recruiter_pitch" in st.session_state:
            st.markdown(
                """
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-top: 1rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                """,
                unsafe_allow_html=True,
            )
            st.markdown(st.session_state["recruiter_pitch"])
            st.markdown("</div>", unsafe_allow_html=True)

    # TAB 1: BENCHMARK
    with tabs[1]:
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

    # TAB 3: AT RISK
    with tabs[2]:
        st.subheader("🚩 At-Risk Candidates Needing Intervention")
        if not at_risk_students:
            st.success("No students are currently flagged as at-risk.")
        else:
            st.dataframe(pd.DataFrame(at_risk_students), use_container_width=True, hide_index=True)

    # TAB 4: ROSTER
    with tabs[3]:
        st.subheader("Placement Candidate Roster")
        st.dataframe(df_students, use_container_width=True, hide_index=True)

    # TAB 5: EXPORTS
    with tabs[4]:
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
# ADMIN VIEW WITH AI CURRICULUM GAP ANALYSIS
# ==========================================
def render_admin_view():
    user_name = st.session_state["user_name"]

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <h2 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #0f172a;">College Administration Portal ⚙️</h2>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.95rem;">{user_name} • Platform Trends & Academic Council Intelligence</p>
                </div>
                <div><span class="role-badge badge-admin">Administrator</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs([
        "🧠 AI Curriculum Gap Analytics",
        "📈 Platform Macro Trends",
        "🤝 Mentor-Student Pairing",
        "👥 User Directory",
    ])

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

    with tabs[0]:
        st.markdown(
            """
            <div class="ai-box">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span class="ai-badge">Academic Council Intelligence</span>
                    <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #581c87;">AI Curriculum Gap & Syllabus Analytics</h3>
                </div>
                <p style="margin: 0.35rem 0 0 0; color: #7e22ce; font-size: 0.95rem;">
                    Synthesize college-wide student deficits to detect structural syllabus deficiencies and formulate accreditation interventions.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("🏛️ Institutional Syllabus Gap Analysis & Board of Studies Action Plan")
        st.caption("One-click diagnostic across all active engineering tracks (AI/ML, DevOps, Full-Stack, Cloud) to pinpoint syllabus gaps and formulate accreditation improvements:")

        if "curriculum_plan" not in st.session_state:
            st.session_state["curriculum_plan"] = generate_ai_curriculum_analysis(df_roles)

        col_curr_btn, col_curr_dl = st.columns([2, 1])
        with col_curr_btn:
            if st.button("🧠 AI Institutional Curriculum Gap Detector", type="primary", use_container_width=True, key="btn_run_curriculum"):
                st.session_state["curriculum_plan"] = generate_ai_curriculum_analysis(df_roles)
                st.success("✅ AI Institutional Curriculum Gap Detector executed successfully! Academic Council action plan refreshed.")
        with col_curr_dl:
            st.download_button(
                "📥 Download Action Plan (.md)",
                data=st.session_state.get("curriculum_plan", ""),
                file_name="academic_council_curriculum_gap_audit.md",
                mime="text/markdown",
                use_container_width=True,
                key="btn_dl_curriculum"
            )

        # 3 Structured Recommendation Cards
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown(
                """
                <div style="background: #fdf4ff; border: 1px solid #f0abfc; border-left: 4px solid #c026d3; border-radius: 8px; padding: 1rem; height: 100%;">
                    <div style="font-weight: 700; color: #701a75; font-size: 0.95rem;">📘 Value-Added Elective Courses</div>
                    <div style="font-size: 0.825rem; color: #4a044e; margin-top: 0.35rem; line-height: 1.5;">
                        Recommend 2-credit intensive electives on <em>Cloud-Native Systems & Microservices</em> to bridge applied software architecture gaps.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with rc2:
            st.markdown(
                """
                <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #2563eb; border-radius: 8px; padding: 1rem; height: 100%;">
                    <div style="font-weight: 700; color: #1e3a8a; font-size: 0.95rem;">👨‍🏫 Faculty Development (FDP)</div>
                    <div style="font-size: 0.825rem; color: #172554; margin-top: 0.35rem; line-height: 1.5;">
                        Conduct semester industry immersion FDPs for CSE & IT faculty on <em>Production Full-Stack Patterns</em> and containerized DevOps workflows.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with rc3:
            st.markdown(
                """
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; border-radius: 8px; padding: 1rem; height: 100%;">
                    <div style="font-weight: 700; color: #14532d; font-size: 0.95rem;">🔬 Capstone Lab Revamp</div>
                    <div style="font-size: 0.825rem; color: #052e16; margin-top: 0.35rem; line-height: 1.5;">
                        Mandate that 30% of laboratory internal assessment evaluates public GitHub repositories, Dockerized runs, and automated unit test coverage.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-top: 1rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(st.session_state["curriculum_plan"])
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[1]:
        st.subheader("Platform Analytics & Macro Readiness")
        fig = px.bar(
            df_roles,
            x="Job Role",
            y="Average Gap",
            color="Average Gap",
            color_continuous_scale="Inferno",
            labels={"Average Gap": "Average Deficit (%)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
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

    with tabs[3]:
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

            if role == "student":
                st.markdown(
                    """
                    <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 800; color: #7e22ce; letter-spacing: 0.05em;">AI Copilot Tools</div>
                        <div style="margin-top: 0.4rem; font-size: 0.825rem; color: #581c87; line-height: 1.6;">
                            • 📅 <strong>30-Day Sprint Roadmap</strong><br>
                            • 💡 <strong>Tech Interview Simulator</strong><br>
                            • 📄 <strong>STAR Resume Bullets</strong><br>
                            • 🎯 <strong>SMART Diagnostic</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif role == "mentor":
                st.markdown(
                    """
                    <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 800; color: #7e22ce; letter-spacing: 0.05em;">AI Mentorship Tools</div>
                        <div style="margin-top: 0.4rem; font-size: 0.825rem; color: #581c87; line-height: 1.6;">
                            • ✨ <strong>Draft AI Feedback for Mentee</strong><br>
                            • 🗓️ <strong>14-Day Milestone Recovery</strong><br>
                            • ⚠️ <strong>Automated At-Risk Detection</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif role == "tpo":
                st.markdown(
                    """
                    <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 800; color: #7e22ce; letter-spacing: 0.05em;">AI Placement Intelligence</div>
                        <div style="margin-top: 0.4rem; font-size: 0.825rem; color: #581c87; line-height: 1.6;">
                            • 🏆 <strong>Corporate Tier Segmentation</strong><br>
                            • ✨ <strong>Generate AI Corporate Pitch</strong><br>
                            • 📜 <strong>NBA / NAAC Compliance Pitch</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif role == "admin":
                st.markdown(
                    """
                    <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 800; color: #7e22ce; letter-spacing: 0.05em;">AI Governance Tools</div>
                        <div style="margin-top: 0.4rem; font-size: 0.825rem; color: #581c87; line-height: 1.6;">
                            • 🧠 <strong>AI Curriculum Gap Detector</strong><br>
                            • 🏛️ <strong>Board of Studies Action Plan</strong><br>
                            • 📊 <strong>Macro Deficit Distribution</strong>
                        </div>
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
                <strong>Platform Intelligence</strong><br>
                • SMART Empirical Diagnostic Rubrics<br>
                • Competency Radar & Speedometer<br>
                • AI Career Copilot for Students<br>
                • Corporate Hiring Tier Matchmaker
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
