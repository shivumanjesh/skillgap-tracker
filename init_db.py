from pathlib import Path

from app import create_app
from app.models import db


def initialize_database():
    app = create_app()
    with app.app_context():
        db.create_all()
    return Path(app.instance_path) / "app.db"


if __name__ == "__main__":
    database_path = initialize_database()
    print(f"Database initialized at {database_path}")