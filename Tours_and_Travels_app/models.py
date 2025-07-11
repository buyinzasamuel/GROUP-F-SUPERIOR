from app import db  # type: ignore
from flask_login import UserMixin  # type: ignore
from datetime import datetime  # type: ignore
import random  # type: ignore
import string  # type: ignore

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User model
    tour_package_id = db.Column(db.Integer, db.ForeignKey('tour_package.id'), nullable=False)  # Foreign key to TourPackage model
    booking_reference = db.Column(db.String(20), unique=True, nullable=False)  # Unique booking reference for the booking
    full_name = db.Column(db.String(150), nullable=False)  # Full name of the person booking
    email = db.Column(db.String(150), nullable=False)  # Email of the person booking
    phone_number = db.Column(db.String(15), nullable=False)  # Phone number of the person booking
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)  # Date and time of booking
    status = db.Column(db.String(50), default='Pending')  # Status of the booking (e.g., Pending, Confirmed, Cancelled)
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False) # Unique username for the user
    email = db.Column(db.String(150), unique=True, nullable=False)  # Unique email for the user
    password = db.Column(db.String(150), nullable=False)  # Password for the user
    is_admin = db.Column(db.Boolean, default=False)  # Flag to indicate if the user is an admin
    bookings = db.relationship('Booking', backref='user', lazy=True)  # Relationship with Booking model
    
class TourPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)  # Name of the tour package
    description = db.Column(db.Text, nullable=False)  # Description of the tour package
    price = db.Column(db.Float, nullable=False)  # Price of the tour package
    destination = db.Column(db.String(150), nullable=False)  # Destination of the tour package
    image_file = db.Column(db.String(200), nullable=False, default='default.jpg')  # Image file for the tour package
    bookings = db.relationship('Booking', backref='tour_package', lazy=True)  # Relationship with Booking model
    
    user = db.relationship('User', backref='tour_packages', lazy=True)  # Relationship with User model
    tour_package = db.relationship('TourPackage', backref='bookings', lazy=True)  # Relationship with TourPackage model

    def __init__(self, user_id, tour_package_id, full_name, email, phone):
        self.user_id = user_id
        self.tour_package_id = tour_package_id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.booking_reference = self.generate_booking_reference()

    def generate_booking_reference(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))