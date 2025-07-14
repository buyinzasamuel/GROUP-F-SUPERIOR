from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from tour_travel_app import db, login

# Removed duplicate placeholder class definitions for User, Tour, and Booking.

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    duration = db.Column(db.Integer)  # in days
    price = db.Column(db.Float)
    destination = db.Column(db.String(100))
    image = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='tour', lazy='dynamic')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'))
    booking_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    travel_date = db.Column(db.DateTime)
    persons = db.Column(db.Integer)
    special_requests = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled

@login.user_loader
def load_user(id):
    return User.query.get(int(id))