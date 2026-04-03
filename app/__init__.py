from flask import Flask
from flask_migrate import Migrate
import os
from .models import db
from .routes.tasks import tasks_bp
from .routes.categories import categories_bp

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres:postgres@127.0.0.1:5432/tasks'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Register Blueprints
    app.register_blueprint(tasks_bp)
    app.register_blueprint(categories_bp)

    return app