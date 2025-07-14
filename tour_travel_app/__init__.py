# tour_travel_app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from tour_travel_app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from tour_travel_app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from tour_travel_app.tours import bp as tours_bp
    app.register_blueprint(tours_bp, url_prefix='/tours')

    from tour_travel_app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

from tour_travel_app import models