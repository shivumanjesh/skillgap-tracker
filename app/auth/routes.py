from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.models import User


auth_bp = Blueprint("auth", __name__, template_folder="templates")


ROLE_DASHBOARD_ENDPOINTS = {
    "student": "student.dashboard",
    "mentor": "mentor.dashboard",
    "tpo": "tpo.dashboard",
    "admin": "admin.trends",
}


def _role_dashboard_redirect(user):
    return redirect(url_for(ROLE_DASHBOARD_ENDPOINTS[user.role]))


def role_required(role):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped_view(*args, **kwargs):
            if current_user.role != role:
                abort(403)
            return view(*args, **kwargs)

        return wrapped_view

    return decorator


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _role_dashboard_redirect(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        login_user(user)
        return _role_dashboard_redirect(user)

    return render_template("auth/login.html")


@auth_bp.get("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
