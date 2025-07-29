from app import db  # type: ignore
from flask_login import UserMixin  # type: ignore
from datetime import datetime, timezone #type: ignore
import random  # type: ignore
import string  # type: ignore
from sqlalchemy import event  # type: ignore
from uuid import uuid4
import uuid

from werkzeug.security import generate_password_hash, check_password_hash# type: ignore

# from extensions import db # type: ignore

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User model
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)  # Foreign key to TourPackage model
    booking_reference = db.Column(db.String(20), unique=True, nullable=False)  # Unique booking reference for the booking
    full_name = db.Column(db.String(150), nullable=False)  # Full name of the person booking
    email = db.Column(db.String(150), nullable=False)  # Email of the person booking
    phone_number = db.Column(db.String(15), nullable=False)  # Phone number of the person booking
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)  # Date and time of booking
    status = db.Column(db.String(50), default='Pending')  # Status of the booking (e.g., Pending, Confirmed, Cancelled)
    tour = db.relationship('Tour', back_populates='bookings')
    user = db.relationship("User", back_populates="bookings")
    payments = db.relationship('Payment', back_populates='booking', lazy=True)

    
    
    
@event.listens_for(Booking, 'before_insert')
def generate_booking_reference(mapper, connect, target):
        target.booking_reference = str(uuid.uuid4()).split('-')[0].upper()
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False) # Unique username for the user
    email = db.Column(db.String(150), unique=True, nullable=False)  # Unique email for the user
    password = db.Column(db.String(512), nullable=False)  # Password for the user
    def set_password(self, plain_password):
        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        return check_password_hash(self.password, plain_password)
    is_admin = db.Column(db.Boolean, default=False)  # Flag to indicate if the user is an admin
    phone_number = db.Column(db.String(20)) 
    image = db.Column(db.String(256))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    bookings = db.relationship('Booking', back_populates='user', lazy=True)  # Relationship with Booking model
    payments = db.relationship('Payment', back_populates='user', lazy=True)
    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan')


    
class TourPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    destination = db.Column(db.String(150), nullable=False)
    image_file = db.Column(db.String(200), nullable=False, default='default.jpg')

    # Foreign key to User table - this is missing in your original code
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    # Relationship to User (linked by user_id foreign key)
    user = db.relationship('User', backref='tour_packages', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tour = db.relationship('Tour', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    def __init__(self, user_id, tour_package_id, full_name, email, phone):
        self.user_id = user_id
        self.tour_package_id = tour_package_id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.booking_reference = self.generate_booking_reference()

    def generate_booking_reference(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    
class Tour(db.Model):
    __tablename__ = 'tour' 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in days
    destination = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300), nullable=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    destination_obj = db.relationship('Destination', back_populates='tours')
    bookings = db.relationship('Booking', back_populates='tour')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    reviews = db.relationship('Review', back_populates='tour', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Tour {self.title}>'
    
class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    image = db.Column(db.String(255))
    tours = db.relationship('Tour', back_populates='destination_obj', lazy=True)

    def __repr__(self):
        return f'<Destination {self.name}>'
    
class Payment(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
        method = db.Column(db.String(50), nullable=False)  # e.g., 'Credit Card', 'Mobile Money'
        amount = db.Column(db.Float, nullable=False)
        status = db.Column(db.String(20), nullable=False, default='Pending')  # 'Pending', 'Completed'
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        user = db.relationship('User', back_populates='payments')
        booking = db.relationship('Booking', back_populates='payments')

