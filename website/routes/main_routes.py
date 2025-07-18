from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session
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

@main.route('/')
def index():
    return render_template('login.html')


@main.route('/user/dashboard')
@login_required
def home():
    if not current_user.is_authenticated:
        flash('Please log in to access your dashboard.', 'warning')
        return redirect(url_for('main.home'))
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
        # Get fields
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        date_of_birth = request.form.get('date_of_birth')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate
        if not all([first_name, last_name, email, date_of_birth, password]):
            return jsonify({'success': False, 'message': 'All required fields must be filled.'})

        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match.'})

        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email is already registered.'})

        try:
            hashed_pw = generate_password_hash(password)
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                date_of_birth=date_of_birth,
                password_hash=hashed_pw
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            session['email'] = new_user.email

            if getattr(new_user, 'is_admin', False):
                redirect_url = url_for('custom_admin.dashboard')
            else:
                redirect_url = url_for('main.home')

            return jsonify({'success': True, 'redirect_url': redirect_url})

        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {e}")  # <-- add this to see the real error
            print("Registration error:", e)
            return jsonify({'success': False, 'message': 'An error occurred during registration.'})
        

    return render_template('register.html')

from flask import request, jsonify, url_for, session
from flask_login import login_user

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            session['email'] = email

            # Check admin or regular user
            if hasattr(user, 'is_admin') and user.is_admin:
                redirect_url = url_for('custom_admin.dashboard')
            else:
                redirect_url = url_for('main.home')

            return jsonify({'success': True, 'redirect_url': redirect_url})

        return jsonify({'success': False, 'message': 'Invalid email or password.'})

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

