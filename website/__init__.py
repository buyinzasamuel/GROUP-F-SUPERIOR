from flask import Flask, app, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager, current_user
from flask_admin import Admin
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  
    login_manager.login_message_category = 'info' 

    # Import models and views inside factory to avoid circular imports
    from website.models import User, Inquiry, Booking, Tour, Destination
    from website.routes.admin_routes import admin as custom_admin
    from website.routes.main_routes import main
    from flask_admin.contrib.sqla import ModelView

    # Custom AdminModelView with access control
    class AdminModelView(ModelView):
        def is_accessible(self):
            # Only allow authenticated admin users to access admin panel
            return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

        def inaccessible_callback(self, name, **kwargs):
            # Redirect to login page if user doesn't have access
            return redirect(url_for('admin.login', next=request.url))

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from website.models import User
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(custom_admin, url_prefix='/admin')
    app.register_blueprint(main)

    # Setup Flask-Admin panel with restricted views
    admin_panel = Admin(app, name='Admin Panel', template_mode='bootstrap3', endpoint='flask_admin')
    admin_panel.add_view(AdminModelView(Inquiry, db.session))
    admin_panel.add_view(AdminModelView(User, db.session))
    admin_panel.add_view(AdminModelView(Booking, db.session))
    admin_panel.add_view(AdminModelView(Tour, db.session))
    admin_panel.add_view(AdminModelView(Destination, db.session))

    return app
