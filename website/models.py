from flask import flash, redirect, request, url_for
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from website import db
from functools import wraps
from flask import abort


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    password_hash = db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Inquiry(db.Model):
    __tablename__ = 'inquiry'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Inquiry from {self.name}>"


class Tour(db.Model):
    __tablename__ = 'tour'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    destination = db.relationship('Destination', backref=db.backref('tour_packages', lazy=True))

    def __repr__(self):
        return f"<Tour {self.title}>"


class Booking(db.Model):
    __tablename__ = 'booking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    date_booked = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='bookings')
    tour = db.relationship('Tour', backref='bookings')

    def __repr__(self):
        return f"<Booking by {self.name} for tour {self.tour_id}>"


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        from flask import redirect, url_for, flash, request
        flash("Admin access required.", "warning")
        return redirect(url_for('admin.login', next=request.url))
    
class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    # Add other fields if needed
    

    

