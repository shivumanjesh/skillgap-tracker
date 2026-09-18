from flask import Flask, redirect, render_template, url_for
from flask_login import LoginManager

from app.models import User, db


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def create_app(config_class="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @app.get("/")
    def index():
        from flask_login import current_user
        from app.auth.routes import ROLE_DASHBOARD_ENDPOINTS

        if current_user.is_authenticated and current_user.role in ROLE_DASHBOARD_ENDPOINTS:
            return redirect(url_for(ROLE_DASHBOARD_ENDPOINTS[current_user.role]))

        from app.models import JobRole, Skill, User
        stats = {
            "student_count": User.query.filter_by(role="student").count(),
            "mentor_count": User.query.filter_by(role="mentor").count(),
            "role_count": JobRole.query.count(),
            "skill_count": Skill.query.count(),
        }
        return render_template("landing.html", stats=stats)

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("errors/400.html"), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    from app.admin.routes import admin_bp
    from app.auth.routes import auth_bp
    from app.mentor.routes import mentor_bp
    from app.student.routes import student_bp
    from app.tpo.routes import tpo_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(mentor_bp)
    app.register_blueprint(tpo_bp)
    app.register_blueprint(admin_bp)

    return app

