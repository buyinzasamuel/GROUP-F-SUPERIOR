from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request
from flask_login import current_user
from models import db, Tour, Booking, Inquiry, User

class AdminModelView(ModelView):
    def is_accessible(self):
        # Check if current_user has is_admin True (based on your User model)
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        # Redirect unauthorized users to login page, with next param for redirect after login
        return redirect(url_for('main.login', next=request.url))

def setup_admin(app, db, models):
    from flask_admin import Admin
    from flask_admin.contrib.sqla import ModelView
    from flask_login import current_user
    from flask import redirect, url_for, request

    class AdminModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('main.login', next=request.url))

    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

    added = set()
    for model in models:
        model_name = model.__name__.lower()
        if model_name not in added:
            admin.add_view(AdminModelView(model, db.session, name=model.__name__))
            added.add(model_name)
