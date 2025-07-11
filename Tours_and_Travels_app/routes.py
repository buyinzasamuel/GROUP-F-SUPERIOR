from flask import render_template, redirect, url_for, flash, request
from app import app, db
from models import User, TourPackage, Booking, Inquiry, Review # type: ignore
from forms import RegistrationForm, LoginForm, TourPackageForm, BookingForm, ReviewForm, InquiryForm
from flask_login import login_user, current_user, logout_user, login_required # type: ignore
from flask_mail import Mail, Message # type: ignore
import stripe # type: ignore
from flask import jsonify # type: ignore

mail = Mail(app)

def send_confirmation_email(booking):
    msg = Message('Booking Confirmation', sender='your_email@example.com', recipients=[booking.email])
    msg.body = f'''
    Thank you for your booking, {booking.full_name}!
    
    Booking Reference: {booking.booking_reference}
    Tour Package: {booking.tour_package.title}
    Full Name: {booking.full_name}
    Email: {booking.email}
    Phone: {booking.phone}
    
    We look forward to seeing you!
    '''
    mail.send(msg)
@app.route('/my_bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('profile'))
        flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/tours', methods=['GET', 'POST'])
@login_required
def tours():
    if request.method == 'POST':
        form = TourPackageForm()
        if form.validate_on_submit():
            tour = TourPackage(title=form.title.data, description=form.description.data,
                               price=form.price.data, duration=form.duration.data,
                               destination=form.destination.data, image_url=form.image_url.data)
            db.session.add(tour)
            db.session.commit()
            flash('Tour package created!', 'success')
            return redirect(url_for('tours'))
    tour_packages = TourPackage.query.all()
    return render_template('tour_list.html', tours=tour_packages)
   
stripe.api_key = app.config['STRIPE_SECRET_KEY']  # Set Stripe secret key for payment processing


@app.route('/pay/<int:booking_id>', methods=['POST'])
@login_required
def pay(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    amount = booking.tour_package.price * 100  # Amount in cents

    try:
        # Create a new charge
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description=f'Booking for {booking.tour_package.title}',
            source=request.form['stripeToken']
        )
        # Update booking status
        booking.status = 'Paid'
        db.session.commit()
        return jsonify({'status': 'success', 'charge_id': charge.id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

   
@app.route('/review/<int:tour_id>', methods=['POST'])
@login_required
def submit_review(tour_id):
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            tour_package_id=tour_id,
            user_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('tour_detail', tour_id=tour_id))
    return redirect(url_for('tour_detail', tour_id=tour_id))   

@app.route('/inquiry', methods=['GET', 'POST'])
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
        send_inquiry_email(inquiry)
        flash('Your inquiry has been sent!', 'success')
        return redirect(url_for('home'))
    return render_template('inquiry.html', form=form)

def send_inquiry_email(inquiry):
    msg = Message('New Inquiry', sender='your_email@example.com', recipients=['admin@example.com'])
    msg.body = f'''
    New Inquiry from {inquiry.name}:
    Email: {inquiry.email}
    Message: {inquiry.message}
    '''
    mail.send(msg)
