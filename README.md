# Skill-Gap & Employability Readiness Tracker 🎓

A modern, production-grade college employability readiness and placement analytics platform. Features dual deployment modes: **Full-Stack Flask SaaS App** and a **Native Streamlit Community Cloud App** (`streamlit_app.py`).

---

## 🚀 Dual Deployment Modes

### Mode 1: Streamlit Cloud (Fastest 1-Click Hosting)
Run locally or deploy to **Streamlit Community Cloud**:
```bash
streamlit run streamlit_app.py
```
- Interactive multi-role dashboard with Plotly visual analytics.
- Integrated role-based authentication and demo access buttons.
- Direct CSV downloads and real-time gap calculations.

### Mode 2: Flask Web Application (Full SaaS Experience)
```powershell
# Run Flask dev server
$env:FLASK_DEBUG="1"
python run.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 🔐 Security Architecture & Best Practices

This project implements strict security controls to protect student data and institutional credentials:

1. **Environment Secrets**: Sensitive variables (`SECRET_KEY`, `DATABASE_URL`) are read from environment variables or `st.secrets` rather than hardcoded.
2. **Credential & Secret Protection**: `.gitignore` strictly excludes `.env`, `Credentials.docx`, local SQLite databases (`app.db`), virtual environments (`venv/`), and cache folders.
3. **Cryptographic Password Hashing**: Passwords are never stored in plaintext; salted hashes are generated and verified via `werkzeug.security`.
4. **Role-Based Access Control (RBAC)**: Enforces strict session isolation for `student`, `mentor`, `tpo`, and `admin` roles across all views.
5. **Database Portability**: Supports local SQLite and production cloud PostgreSQL instances (e.g. Supabase, Neon, AWS RDS) by simply setting `DATABASE_URL`.

---

## ☁️ Deploying to Streamlit Community Cloud

Deploy directly to the cloud for free using GitHub:

1. **Push your repository to GitHub** (follow the [GitHub Push Guide](#-github-setup--push-guide) below).
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with your GitHub account.
3. Click **"New app"** and select:
   - **Repository**: `your-username/skillgap-tracker`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
4. *(Optional - Advanced Security)*: Under **"Advanced settings"** -> **"Secrets"**, define your production variables:
   ```toml
   SECRET_KEY = "your-strong-random-production-secret"
   # Optional: Connect to external cloud PostgreSQL database
   # DATABASE_URL = "postgresql://user:password@hostname:5432/dbname"
   ```
5. Click **"Deploy!"**. Streamlit Cloud will install dependencies from `requirements.txt` and launch the app immediately!

---

## 🐙 GitHub Setup & Push Guide

To push this repository to your GitHub account:

```bash
# 1. Initialize local repository (if not already done)
git init -b main

# 2. Stage and commit files securely
git add .
git commit -m "feat: Initial commit with Streamlit Cloud and Flask support"

# 3. Link your remote GitHub repository
# (Replace with your actual GitHub repository URL)
git remote add origin https://github.com/<your-username>/skillgap-tracker.git

# 4. Push to main branch
git push -u origin main
```

---

## 🔑 Quick Demo Credentials

| Role | Username / Email | Password | Key Features to Test |
|---|---|---|---|
| **Student** | `student@example.com` | `student123` | Chart.js / Plotly donut chart, priority skills, batch self-assessments |
| **Faculty Mentor** | `mentor@example.com` | `mentor123` | Mentee cohort tracking, verified skill assessment override, at-risk flagging |
| **Placement Officer (TPO)** | `tpo@example.com` | `tpo123` | Placement cockpit, department median gaps, at-risk alerts, CSV exports |
| **Administrator** | `admin@example.com` | `admin123` | Macro trends charts, mentor-student pairing, user directory |

*(Note: One-click demo buttons are provided on both the Flask `/login` page and the Streamlit app sidebar/login screen for friction-free evaluation).*

---

## 📖 Comprehensive Documentation
For a complete analysis of the project's **Need**, **Significance**, **Outcomes**, **Architecture**, **Mathematical Formulation**, and **API Inventory**, please read:
👉 **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)**

