from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from models import User, Tour, Booking, Inquiry, Review
from forms import RegistrationForm, LoginForm, TourPackageForm, BookingForm, ReviewForm, InquiryForm
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, mail
from flask_mail import Message
import stripe # type: ignore

main = Blueprint('main', __name__)



def send_confirmation_email(booking):
    msg = Message(
        'Booking Confirmation',
        sender='your_email@example.com',
        recipients=[booking.email]
    )
    msg.body = f'''
Thank you for your booking, {booking.full_name}!

Booking Reference: {booking.booking_reference}
Tour: {booking.tour.title}
Full Name: {booking.full_name}
Email: {booking.email}
Phone: {booking.phone_number}

We look forward to seeing you!
'''
    mail.send(msg)

def send_inquiry_notification(inquiry):
    msg = Message(
        subject="New Inquiry Received",
        recipients=[current_app.config.get('ADMIN_EMAIL', 'admin@example.com')],
        html=f"""
        <h1>New Inquiry Received</h1>
        <p><strong>Name:</strong> {inquiry.name}</p>
        <p><strong>Email:</strong> {inquiry.email}</p>
        <p><strong>Message:</strong> {inquiry.message}</p>
        """
    )
    mail.send(msg)

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            if user.is_admin:
                return redirect(url_for('custom_admin.dashboard'))
            else:
                return redirect(url_for('main.profile'))

        flash('Invalid email or password.', 'danger')
        return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/my_bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('my_bookings.html', bookings=bookings)

@main.route('/tours', methods=['GET', 'POST'])
@login_required
def tours():
    form = TourPackageForm()
    if form.validate_on_submit():
        tour = Tour(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            duration=form.duration.data,
            destination=form.destination.data,
            image_url=form.image_url.data or 'default.jpg'
        )
        db.session.add(tour)
        db.session.commit()
        flash('Tour created successfully!', 'success')
        return redirect(url_for('main.tours'))
    tours = Tour.query.all()
    return render_template('tour_list.html', tours=tours, form=form)

@main.route('/pay/<int:booking_id>', methods=['POST'])
@login_required
def pay(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    amount = int(booking.tour.price * 100)  # amount in cents

    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description=f'Booking for {booking.tour.title}',
            source=request.form['stripeToken']
        )
        booking.status = 'Paid'
        db.session.commit()
        return jsonify({'status': 'success', 'charge_id': charge.id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@main.route('/review/<int:tour_id>', methods=['POST'])
@login_required
def submit_review(tour_id):
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            tour_id=tour_id,
            user_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('main.tours'))
    return redirect(url_for('main.tours'))

@main.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    form = InquiryForm()
    if form.validate_on_submit():
        inquiry = Inquiry(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(inquiry)
        db.session.commit()
        send_inquiry_notification(inquiry)
        flash('Your inquiry has been sent!', 'success')
        return redirect(url_for('main.index'))
    return render_template('inquiry.html', form=form)
