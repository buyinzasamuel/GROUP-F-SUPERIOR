from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from config import Config

# Initialize extensions (no app yet)
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions with app
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'main.login'  # blueprint_name.endpoint for login

    # Import models here to register them with SQLAlchemy
    from models import User, Inquiry, Booking, Tour

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import blueprints here (after app is created)
    from routes import main
    from admin_routes import admin as custom_admin

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(custom_admin, url_prefix='/admin')

    # Setup Flask-Admin with custom views
    from admin import setup_admin
    setup_admin(app, db, [User, Inquiry, Booking, Tour])

    # Create tables if not exist
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
