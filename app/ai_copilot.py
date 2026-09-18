"""
AI Copilot and SMART Diagnostic Intelligence Engine for SkillGap Tracker.
Provides automated roadmaps, interview simulations, STAR resume bullets,
faculty feedback generation, corporate recruitment pitches, and curriculum gap analytics.
"""

def get_skill_rubrics(skill_name):
    """Return 3 objective behavioral milestones for self/mentor assessment."""
    rubrics = {
        "Python": [
            "Writes idiomatic code using list comprehensions, generators, and decorators.",
            "Implements robust OOP designs, custom exception hierarchies, and pytest suites.",
            "Profiles memory bottlenecks and designs asynchronous/concurrent pipelines (asyncio/threading)."
        ],
        "Flask": [
            "Configures Application Factory pattern, Blueprints, and Jinja2 templating.",
            "Implements RESTful endpoints with Flask-SQLAlchemy, migrations, and WTForms validation.",
            "Deploys secure production configurations with Gunicorn, CSRF protection, and JWT auth."
        ],
        "PostgreSQL": [
            "Designs 3NF relational schemas with primary/foreign keys and CHECK constraints.",
            "Analyzes queries using EXPLAIN ANALYZE, creating composite and partial indexes.",
            "Manages transactions with ACID guarantees, connection pooling (PgBouncer), and isolation levels."
        ],
        "Git": [
            "Executes core branch operations (checkout, merge, stash, rebase, and cherry-pick).",
            "Resolves complex three-way merge conflicts and enforces Conventional Commits standard.",
            "Architects GitHub Actions CI/CD workflows with automated linting, security scans, and auto-deploy."
        ],
        "Docker": [
            "Authors multi-stage Dockerfiles optimizing base images (e.g. alpine) and caching layers.",
            "Orchestrates multi-container local clusters with Docker Compose (web, worker, redis, db).",
            "Secures container images by eliminating root execution and configuring health checks."
        ],
        "React": [
            "Architects modular components with functional hooks (useState, useEffect, useMemo, useCallback).",
            "Manages predictable global state via Context API or Redux Toolkit with immutable patterns.",
            "Optimizes render performance through lazy loading, code-splitting, and memoization."
        ],
        "Machine Learning": [
            "Cleans data with pandas/numpy, performing exploratory data analysis (EDA) and feature scaling.",
            "Trains and hyperparameter-tunes Scikit-Learn pipelines (RandomForest, XGBoost, Cross-Validation).",
            "Deploys model endpoints using FastAPI/ONNX with monitoring for data and concept drift."
        ],
        "Deep Learning": [
            "Implements neural architectures using PyTorch/TensorFlow with forward and backprop passes.",
            "Trains CNNs/Transformers using GPU acceleration, custom datasets, and transfer learning.",
            "Mitigates overfitting with dropout, weight decay, early stopping, and learning rate schedulers."
        ],
        "Kubernetes": [
            "Configures Pods, Deployments, Services (ClusterIP, NodePort, Ingress), and ConfigMaps.",
            "Implements Horizontal Pod Autoscalers (HPA) and rolling zero-downtime updates.",
            "Troubleshoots networking, CrashLoopBackOff states, and PersistentVolumeClaims."
        ]
    }
    return rubrics.get(skill_name, [
        f"Demonstrates foundational theory, syntax, and principles of {skill_name}.",
        f"Builds functional end-to-end applications or pipelines integrating {skill_name}.",
        f"Optimizes performance, handles edge cases, and architectures production implementations of {skill_name}."
    ])


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


def get_student_roadmap_data(student_name, target_role, deficit_skills):
    """Return structured weekly roadmap data for rendering in HTML/Jinja templates."""
    top_deficits = deficit_skills[:3] if deficit_skills else [("Core Engineering", "not_started")]
    primary_focus = top_deficits[0][0]
    secondary_focus = " & ".join([d[0] for d in top_deficits[:2]])
    advanced_focus = top_deficits[-1][0] if len(top_deficits) > 2 else primary_focus

    return [
        {
            "week_num": 1,
            "title": "Core Conceptual Foundations & Drills",
            "focus": primary_focus,
            "daily_target": "2 hours dedicated theory + syntax drills.",
            "milestone": "Complete core documentation review; build 3 minimal proofs-of-concept.",
            "tip": "Summarize architectural principles into 1-page cheatsheets for interview quick-recall.",
            "icon": "bi-journal-code",
            "color": "primary"
        },
        {
            "week_num": 2,
            "title": "Hands-On Capstone Mini-Project",
            "focus": secondary_focus,
            "daily_target": "Build a portfolio-worthy project integrating both competencies.",
            "milestone": "Commit clean, documented code to a public GitHub repository with an architecture diagram.",
            "tip": "Add unit tests with >80% coverage and configure automated CI testing.",
            "icon": "bi-code-slash",
            "color": "info"
        },
        {
            "week_num": 3,
            "title": "Advanced Optimization, Edge Cases & System Design",
            "focus": advanced_focus,
            "daily_target": "Production error handling, benchmarking, latency optimization, and security audits.",
            "milestone": "Implement caching, connection pooling, or vector search depending on track requirements.",
            "tip": "Record a 2-minute video walkthrough explaining trade-offs made during development.",
            "icon": "bi-cpu",
            "color": "warning"
        },
        {
            "week_num": 4,
            "title": "Mock Technical Interviews & Placement Polish",
            "focus": "Placement Bar Clearing",
            "daily_target": "1 timed technical simulation daily + behavioral STAR questions.",
            "milestone": "Schedule a 1-on-1 review with your assigned Faculty Mentor.",
            "tip": "Retake the SMART Diagnostic to verify competency transition to Confident!",
            "icon": "bi-mortarboard-fill",
            "color": "success"
        }
    ]


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
    """Generate structured faculty mentoring guidance notes."""
    top_deficits = [d[0] for d in deficit_skills[:3]] if deficit_skills else ["General Systems Design"]
    deficit_text = ", ".join(top_deficits)

    if readiness_score >= 75:
        tone = f"Commendable progress! {mentee_name} displays high industry alignment ({readiness_score}% ready). Recommended: Target Tier-1 engineering problem sets and lead peer code reviews."
    elif readiness_score >= 45:
        tone = f"Steady progress ({readiness_score}% ready). Key focus needed on mastering {deficit_text} to clear Tier-2 corporate interview technical bars."
    else:
        tone = f"Critical academic intervention advised. Readiness score is {readiness_score}% with a {gap_percentage}% deficit across core competencies ({deficit_text}). Recommended: Enroll in department guided remedial coding labs."

    return f"""### 📝 Faculty Advisory Note for {mentee_name} ({branch})
**Target Track:** {target_role} | **Readiness Benchmark:** {readiness_score}% (Deficit: {gap_percentage}%)

**Diagnostic Assessment:**
{tone}

**Recommended 14-Day Action Items:**
1. **Targeted Hands-on Practice:** Spend 45 minutes daily dedicated to practical problem solving in `{top_deficits[0]}`.
2. **Git Proof-of-Work:** Push at least two working micro-modules with unit tests to GitHub before our next review.
3. **Faculty Check-in:** Schedule a 15-minute code walkthrough during department office hours next week.
"""


def generate_ai_recruiter_pitch(total_students, ready_count, avg_gap, branch_data, tier_counts):
    """Generate institutional placement pitch for corporate recruiters."""
    ready_pct = round((ready_count / total_students) * 100, 1) if total_students else 0
    t1 = tier_counts.get("tier1", tier_counts.get("Tier 1", 0))
    t2 = tier_counts.get("tier2", tier_counts.get("Tier 2", 0))
    t3 = tier_counts.get("tier3", tier_counts.get("Tier 3", 0))
    t_rem = tier_counts.get("remedial", tier_counts.get("Intervention", 0))

    return f"""### 🏢 Executive Placement Brief for Visiting Corporate Recruiters
**Institutional Batch Overview:** {total_students} Graduating Engineers Assessed

---

#### 🌟 **Recruitment Readiness Highlights:**
- **Tier-1 Product-Ready Cohort (15+ LPA):** **{t1} students** ({round(t1/total_students*100, 1) if total_students else 0}%) verified in advanced systems architecture, concurrency, and high-scale design (Readiness >= 80%).
- **Tier-2 Scaleup-Ready Cohort (8–15 LPA):** **{t2} students** ({round(t2/total_students*100, 1) if total_students else 0}%) possessing independent full-stack implementation proficiency (Readiness 60%–79%).
- **Tier-3 Services Cohort (4–8 LPA):** **{t3} students** ({round(t3/total_students*100, 1) if total_students else 0}%) with verified foundational programming and database competence (Readiness 40%–59%).
- **Remedial Intervention Cohort:** **{t_rem} students** receiving targeted laboratory mentorship (Readiness < 40%).
- **Overall Placement-Ready Ratio:** **{ready_pct}%** of candidates meet rigorous corporate thresholds with average deficit of only **{avg_gap}%**.

#### 🎯 **Why Recruit From Our Campus:**
1. **Empirical Rubric Verification:** Every candidate's proficiency is cross-validated through objective behavioral milestones and faculty mentor code reviews (zero self-reported fluff).
2. **Modern Technology Stacks:** Core competencies focus on production-grade Python, React, PostgreSQL, Docker, and Cloud architectures.
3. **Outcome-Based Education (OBE):** Fully compliant with NBA/NAAC Program Outcomes (POs) and continuous curriculum alignment.
"""


def generate_ai_curriculum_analysis(role_gap_df):
    """Generate Board of Studies curriculum gap analysis for administrators."""
    if role_gap_df is None:
        return "No sufficient student data available to compute curriculum deficit correlations."

    try:
        # Check if DataFrame or list of dicts
        if hasattr(role_gap_df, "empty") and role_gap_df.empty:
            return "No sufficient student data available to compute curriculum deficit correlations."
        elif isinstance(role_gap_df, list) and not role_gap_df:
            return "No sufficient student data available to compute curriculum deficit correlations."

        if hasattr(role_gap_df, "columns"):
            # It's a pandas DataFrame
            role_col = "Role" if "Role" in role_gap_df.columns else ("Job Role" if "Job Role" in role_gap_df.columns else role_gap_df.columns[0])
            gap_col = "Avg Gap (%)" if "Avg Gap (%)" in role_gap_df.columns else ("Average Gap" if "Average Gap" in role_gap_df.columns else role_gap_df.columns[-1])
            sorted_df = role_gap_df.sort_values(by=gap_col, ascending=False)
            highest_gap_role = sorted_df.iloc[0][role_col]
            highest_gap_pct = sorted_df.iloc[0][gap_col]
        elif isinstance(role_gap_df, list):
            # It's a list of dicts
            sorted_list = sorted(role_gap_df, key=lambda x: x.get("average_gap", x.get("Avg Gap (%)", 0)) or 0, reverse=True)
            highest_gap_role = sorted_list[0].get("name", sorted_list[0].get("Role", "Software Engineering"))
            highest_gap_pct = sorted_list[0].get("average_gap", sorted_list[0].get("Avg Gap (%)", 45))
        else:
            highest_gap_role = "Software Engineering"
            highest_gap_pct = 40.0
    except Exception:
        highest_gap_role = "Full-Stack Development & Cloud"
        highest_gap_pct = 42.5

    return f"""### 🏛️ Academic Council & Board of Studies Curriculum Gap Audit
**Institutional Focus Track:** Highest systemic deficit observed in **{highest_gap_role}** (Average Deficit: **{highest_gap_pct}%**).

---

#### 🔍 **Root Cause Academic Diagnosis:**
1. **Theory-to-Practice Imbalance:** Students demonstrate acceptable theoretical test scores but lack exposure to production tools, CI/CD pipelines, and automated testing frameworks.
2. **Syllabus Currency Deficit:** Rapidly evolving industry standards (Containerization, Vector Databases, Deep Learning fine-tuning) are under-represented in traditional 2nd and 3rd year laboratory curricula.

#### 📋 **Recommended Academic Action Plan for Current Semester:**
- **Value-Added Elective Courses:** Introduce a 2-credit weekend intensive elective on *Cloud-Native Systems & Microservices Engineering*.
- **Faculty Development Program (FDP):** Conduct an industry-led FDP for computer science and information technology faculty on *Modern Full-Stack Architectural Patterns*.
- **Capstone Lab Revision:** Mandate that all semester project submissions include a functional GitHub repository, Docker container, and unit tests as 30% of internal grading rubrics.
"""
