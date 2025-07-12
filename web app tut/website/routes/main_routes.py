from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import Booking, Tour, User, Inquiry
from website import db, mail
from flask_mail import Message
from flask import current_app as app  # Use this to access app config safely
from functools import wraps
from flask import session, redirect, url_for

main = Blueprint('main', __name__)

def send_inquiry_notification(inquiry):
    msg = Message(
        subject="New Inquiry Received",
        recipients=[app.config['ADMIN_EMAIL']],
        html=f"""
        <h1>New Inquiry Received</h1>
        <p><strong>Name:</strong> {inquiry.name}</p>
        <p><strong>Email:</strong> {inquiry.email}</p>
        <p><strong>Message:</strong> {inquiry.message}</p>
        """
    )
    mail.send(msg)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'email' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return wrapper

@main.route('/user/dashboard')
@login_required
def home():
    return render_template('home.html', user=current_user)

@main.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_inquiry = Inquiry(name=name, email=email, message=message)
        db.session.add(new_inquiry)
        db.session.commit()

        send_inquiry_notification(new_inquiry)
        flash('Your inquiry has been sent!', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        date_of_birth = request.form.get('date_of_birth')
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill out all fields', 'error')
            return redirect(url_for('main.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('main.register'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(
            last_name=last_name,
            first_name=first_name,
            email=email,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            password=hashed_pw
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Try again.', 'error')
        return redirect(url_for('main.register'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)  # Log the user in regardless of role
            session['email'] = email

            if hasattr(user, 'is_admin') and user.is_admin:
                return redirect(url_for('admin.dashboard'))  # Admin dashboard route
            else:
                return redirect(url_for('main.user_dashboard'))  # User dashboard route

        flash('Invalid credentials', 'error')
        return redirect(url_for('main.login'))
    return render_template('login.html') 

@main.route('/logout')
def logout():
    logout_user()
    session.pop('email', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.login'))

# Route to list all tours
@main.route('/tours')
def tour_list():
    tours = Tour.query.all()  # Fetch tours from the database
    return render_template('tours.html', tours=tours)

# Route to show the booking form for a specific tour
@main.route('/book/<int:tour_id>', methods=['GET', 'POST'])
def book_tour(tour_id):
    tour = Tour.query.get(tour_id)
    if not tour:
        flash("Tour not found!", "error")
        return redirect(url_for('main.tour_list'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        date = request.form['date']
        booking = Booking(tour_id=tour.id, name=name, email=email, date=date)
        db.session.add(booking)
        db.session.commit()
        # Here you'd normally save the booking to a database
        flash(f"Tour booked successfully for {name}!", "success")
        return redirect(url_for('main.tour_list'))

    return render_template('book_tour.html', tour=tour)