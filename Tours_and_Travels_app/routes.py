from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory # type: ignore
from flask import current_app as app# type: ignore
from app import app, db, mail
from models import User, TourPackage, Booking, Inquiry, Review, Tour, Destination, Payment # type: ignore
from forms import RegistrationForm, LoginForm, TourPackageForm, BookingForm, ReviewForm, InquiryForm, TourForm, DestinationForm, EditUserForm, DummyForm
from flask_login import login_user, current_user, logout_user, login_required # type: ignore
from flask_mail import Mail, Message # type: ignore
import stripe # type: ignore
from flask import jsonify # type: ignore
from werkzeug.utils import secure_filename # type: ignore
from sqlalchemy import func, extract #type:  ignore
from sqlalchemy.orm import joinedload # type: ignore
import os
from flask import current_app # type: ignore
from datetime import datetime
import uuid



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
    
@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/my_bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).options(db.joinedload(Booking.tour)).all()
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/book_tour')
@login_required
def book_tour():
    book_tour = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('book_tour.html', bookings=book_tour)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        image_file = form.image.data
        image_filename = None

        if image_file:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join('static', 'uploads', image_filename)
            image_file.save(image_path)

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            image=image_filename  # Make sure your User model has this field
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "success": True,
            "redirect_url": url_for('login')
        })

    elif request.method == 'POST':
        error_messages = [
            f"{getattr(form, field).label.text}: {error}"
            for field, errors in form.errors.items()
            for error in errors
        ]
        return jsonify({
            "success": False,
            "message": " ".join(error_messages) or "Validation failed."
        })

    return render_template("register.html", form=form)




@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    next_page = request.args.get('next') or url_for('tours')  # default user redirect

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)

                # Check if the user is an admin based on email
                admin_emails = ['admin@example.com', 'admin2@example.com']
                if user.email in admin_emails:
                    return jsonify({
                        "success": True,
                        "redirect_url": url_for('dashboard')
                    })

                return jsonify({
                    "success": True,
                    "redirect_url": next_page  # Normal user
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Invalid username or password."
                })
        else:
            error_messages = [f"{form[field].label.text}: {error}"
                              for field, errors in form.errors.items()
                              for error in errors]
            return jsonify({
                "success": False,
                "message": " ".join(error_messages) or "Validation failed."
            })

    return render_template("login.html", form=form)




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
    tour_packages = Tour.query.all()  # or TourPackage if you're using that
    return render_template('tours.html', tours=tour_packages)
   
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

   
# @app.route('/review/<int:tour_id>', methods=['POST'])
# @login_required
# def submit_reviews(tour_id):
#     form = ReviewForm()
#     if form.validate_on_submit():
#         review = Review(
#             tour_package_id=tour_id,
#             user_id=current_user.id,
#             rating=form.rating.data,
#             comment=form.comment.data
#         )
#         db.session.add(review)
#         db.session.commit()
#         flash('Your review has been submitted!', 'success')
#         return redirect(url_for('tour_detail', tour_id=tour_id))
#     return redirect(url_for('tour_detail', tour_id=tour_id))   

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
    
    
@app.route('/about')
def about():
    return render_template('about.html')  # Make sure you have about.html in templates

@app.route('/destinations', methods=['GET', 'POST'])
@login_required
def destinations():
    form = DestinationForm()
    
    if form.validate_on_submit():
        destination = Destination(
            name=form.name.data,
            description=form.description.data,
            country=form.country.data,
            category=form.category.data,
            price_range=form.price_range.data
        )
        db.session.add(destination)
        db.session.commit()
        flash('Destination added successfully!', 'success')
        return redirect(url_for('destinations.html'))
    
    return render_template('destinations.html', form=form)

@app.route('/contact')
def contact():
    return render_template('contact.html')  

@app.route('/dashboard')
@login_required
def dashboard():
    new_bookings_count = Booking.query.filter_by(status='new').count()
    pending_approvals_count = Booking.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(func.sum(Payment.amount)).scalar() or 0
    active_customers = User.query.filter_by(is_admin=False).count()
    # total_destinations = Destination.query.count()
    bookings = Booking.query.all()
    destinations = Destination.query.all()
    customers = User.query.filter_by(is_admin=False).all()
    form = TourForm()
    bookings1 = Booking.query.order_by(Booking.booking_date.desc()).all()
    monthly_revenue_query = (
        db.session.query(
            extract('year', Payment.created_at).label('year'),
            extract('month', Payment.created_at).label('month'),
            func.sum(Payment.amount).label('total')
        )
        .group_by('year', 'month')
        .order_by('year', 'month')
        .all()
    )

    monthly_revenue_labels = [f"{int(r.year)}-{int(r.month):02d}" for r in monthly_revenue_query]
    monthly_revenue_data = [float(r.total) for r in monthly_revenue_query]
    
    
    top_booked_data = (
        db.session.query(Tour.title, func.count(Booking.id))
        .join(Booking, Booking.tour_id == Tour.id)
        .group_by(Tour.title)
        .order_by(func.count(Booking.id).desc())
        .limit(5)  # Optional: limit to top 5
        .all()
    )

    top_booked_labels = [name for name, count in top_booked_data]
    top_booked_counts = [count for name, count in top_booked_data]
    
    
    
    new_customers_query = (
    db.session.query(
        extract('year', User.created_at).label('year'),
        extract('month', User.created_at).label('month'),
        func.count(func.distinct(User.id)).label('count')
    )
    .join(Booking, Booking.user_id == User.id)
    .filter(User.is_admin == False)
    .group_by('year', 'month')
    .order_by('year', 'month')
    .all()
)

    new_customer_labels = [f"{int(row.year)}-{int(row.month):02d}" for row in new_customers_query]
    new_customer_counts = [row.count for row in new_customers_query]    
    

    status_distribution_query = (
    db.session.query(
        Booking.status,
        func.count(Booking.id).label('count')
    )
    .group_by(Booking.status)
    .all()
)
    
    
    status_labels = [row[0] for row in status_distribution_query]
    status_counts = [row[1] for row in status_distribution_query]

    
    
    
    
            
    return render_template(
        'dashboard.html',
        form=form,
        user=current_user,
        new_bookings=new_bookings_count,
        pending_approvals=pending_approvals_count,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        active_customers=active_customers,
        bookings=bookings,
        destinations=destinations,
        customers=customers,
        bookings1=bookings1,monthly_revenue_labels=monthly_revenue_labels,
        monthly_revenue_data=monthly_revenue_data,
        top_booked_labels=top_booked_labels,
        top_booked_counts=top_booked_counts,new_customer_labels=new_customer_labels,
        new_customer_counts=new_customer_counts,
        status_labels=status_labels,
        status_counts=status_counts
             
    )

@app.route('/tours-create', methods=['GET', 'POST'])
@login_required
def tours_create():
    form = TourForm()
    if form.validate_on_submit():
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.static_folder, 'uploads', filename)
        image_file.save(image_path)

        new_tour = Tour(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            duration=form.duration.data,
            destination=form.destination.data,
            image=filename,
        )
        db.session.add(new_tour)
        db.session.commit()

        # Return JSON response here, not redirect
        return jsonify({
            'success': True,
            'redirect_url': url_for('dashboard')  # or wherever you want to go after success
        })

    # If validation fails or method is GET
    if request.method == 'POST':
        # form failed validation; send JSON with error
        return jsonify({
            'success': False,
            'message': 'Form validation failed. Please check your input.'
        })

    return render_template('tours_create.html', form=form)


@app.route('/admin_tour_details')
def tour_details():
    return render_template('tour_details.html')  

# Show all tours in admin dashboard
@app.route('/admin/tours')
@login_required
def admin_tours():
    tours = Tour.query.all()
    return render_template('admin_tours.html', tours=tours)

# Edit a tour
@app.route('/admin/tours/edit/<int:tour_id>', methods=['GET', 'POST'])
@login_required
def edit_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    form = TourForm(obj=tour)

    try:
        if form.validate_on_submit():
            # Handle image upload first (if any)
            if form.image.data:
                image_file = form.image.data
                filename = secure_filename(image_file.filename)
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
                image_file.save(upload_path)
                tour.image = filename

            # Update other fields
            tour.title = form.title.data
            tour.description = form.description.data
            tour.price = form.price.data
            tour.duration = form.duration.data
            tour.destination = form.destination.data

            db.session.commit()

            # ✅ Return JSON for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(success=True, redirect_url=url_for('admin_tours'))

            flash('Tour updated successfully!', 'success')
            return redirect(url_for('admin_tours'))

        # ✅ Handle validation errors in AJAX
        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message="Form validation failed", errors=form.errors)

    except Exception as e:
        print("Caught error:", str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message="Server error", error=str(e)), 500
        flash('Server error. Please try again later.', 'danger')

    # Regular GET request or failed POST (non-AJAX)
    return render_template('edit_tour.html', form=form, tour=tour)






# Delete a tour
@app.route('/admin/tours/delete/<int:tour_id>', methods=['POST'])
@login_required
def delete_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    db.session.delete(tour)
    db.session.commit()
    flash('Tour deleted.', 'success')
    return redirect(url_for('admin_tours'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )
    
    
    
    
    
    
    
@app.route('/customers')
@login_required  
def customer_list():
    customers = User.query.options(
        joinedload(User.bookings).joinedload(Booking.tour)
    ).all()

    return render_template("dashboard.html", customers=customers)


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')  # Optional feedback
    except Exception as e:
        print(f"Error deleting user {user_id}: {e}")
        flash('Failed to delete user.', 'danger')  # Optional feedback

    return redirect(url_for('dashboard'))  # or wherever you want to redirect






@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)  # pre-fill form with user data

    if form.validate_on_submit():
        try:
            # Update fields from form data
            user.username = form.username.data
            user.email = form.email.data
            user.phone_number = form.phone_number.data
            user.is_admin = form.is_admin.data

            # Update password if provided
            if form.password.data:
                user.set_password(form.password.data)

            # Handle image upload if file provided
            if form.image.data:
                image_file = form.image.data
                filename = secure_filename(image_file.filename)
                image_path = os.path.join('static', 'uploads', filename)
                image_file.save(image_path)

                # Store relative path for template usage (optional: adjust as needed)
                user.image = filename

            db.session.commit()

            return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
        
        except Exception as e:
            print(f"Error updating user {user_id}: {e}")
            return jsonify({'success': False, 'message': 'An error occurred while updating the user.'}), 500

    # For GET or if form not valid
    return render_template('edit_user.html', user=user, form=form)



@app.route('/admin/destinations')
@login_required
def list_destinations():
    destinations = Destination.query.all()
    form = DummyForm()
    return render_template('dashboard.html', destinations=destinations, form=form)

@app.route('/create-destination', methods=['GET', 'POST'])
def create_destination():
    form = DestinationForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            # Save the destination
            destination = Destination(
                name=form.name.data,
                description=form.description.data,
                country=form.country.data, 
                image=form.image.data.filename  # or handle image saving properly
            )
            db.session.add(destination)
            db.session.commit()

            # ✅ Return JSON for success
            return jsonify({
                'success': True,
                'redirect_url': url_for('list_destinations')  # Adjust as needed
            })
        else:
            print(form.errors) 
            # ❌ Return JSON for validation errors
            return jsonify({
                'success': False,
                'message': 'Validation failed. Please check the form.'
            })

    # Handle GET request (for loading the form)
    return render_template('create_destination.html', form=form)



@app.route('/admin/destinations/edit/<int:dest_id>', methods=['GET', 'POST'])
@login_required
def edit_destination(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    form = DestinationForm(obj=dest)
    if form.validate_on_submit():
        dest.name = form.name.data
        dest.description = form.description.data
        dest.country = form.country.data

        if form.image.data:
            image_file = form.image.data
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.static_folder, 'uploads', image_filename)
            image_file.save(image_path)
            dest.image = image_filename

        db.session.commit()
        flash('Destination updated successfully!', 'success')
        return redirect(url_for('list_destinations'))

    return render_template('dashboard.html', form=form, dest=dest)

@app.route('/admin/destinations/delete/<int:dest_id>', methods=['POST'])
@login_required
def delete_destination(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    try:
        form = DummyForm()
        db.session.delete(dest)
        db.session.commit()
        flash('Destination deleted successfully!', 'success')
    except Exception:
        flash('Error deleting destination.', 'error')
    return redirect(url_for('list_destinations'))

@app.route('/api/reports/data')
def reports_data():
    # --- Monthly Revenue ---
    # Sum prices of confirmed bookings grouped by month
    monthly_revenue_query = (
        db.session.query(
            extract('month', Booking.booking_date).label('month'),
            func.sum(Tour.price).label('revenue')
        )
        .join(Booking.tour)
        .filter(Booking.status == 'Confirmed')
        .group_by('month')
        .order_by('month')
        .all()
    )
    
    revenue_labels = []
    revenue_data = []
    for row in monthly_revenue_query:
        revenue_labels.append(datetime(1900, int(row.month), 1).strftime('%b'))
        revenue_data.append(float(row.revenue or 0))

    # --- Top Destinations ---
    top_destinations_query = (
        db.session.query(
            Destination.name,
            func.count(Booking.id).label('booking_count')
        )
        .join(Destination.tours)  # assuming Destination has 'tours' relationship
        .join(Tour.bookings)
        .group_by(Destination.id)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
        .all()
    )
    
    top_dest_labels = [row.name for row in top_destinations_query]
    top_dest_data = [row.booking_count for row in top_destinations_query]

    # --- Customer Acquisition ---
    # Users created grouped by month
    customer_acquisition_query = (
        db.session.query(
            extract('month', User.created_at).label('month'),
            func.count(User.id).label('count')
        )
        .filter(User.created_at.isnot(None))
        .group_by('month')
        .order_by('month')
        .all()
    )
    
    cust_labels = []
    cust_data = []
    for row in customer_acquisition_query:
        cust_labels.append(datetime(1900, int(row.month), 1).strftime('%b'))
        cust_data.append(row.count)

    # --- Booking Status Overview ---
    booking_status_query = (
        db.session.query(
            Booking.status,
            func.count(Booking.id).label('count')
        )
        .group_by(Booking.status)
        .all()
    )
    
    status_labels = [row.status for row in booking_status_query]
    status_data = [row.count for row in booking_status_query]

    # Prepare JSON response
    return jsonify({
        "monthly_revenue": {
            "labels": revenue_labels,
            "data": revenue_data
        },
        "top_destinations": {
            "labels": top_dest_labels,
            "data": top_dest_data
        },
        "customer_acquisition": {
            "labels": cust_labels,
            "data": cust_data
        },
        "booking_status": {
            "labels": status_labels,
            "data": status_data
        }
    })
    
    
@app.route('/create-booking', methods=['POST'])
def create_booking():
    tour_id_raw = request.form.get("tour_id")
    if not tour_id_raw or not tour_id_raw.isdigit():
        return "Invalid tour_id provided", 400

    tour_id = int(tour_id_raw)
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')


    new_booking = Booking(
            tour_id=tour_id,
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            user_id=current_user.id #if you use login system
        )
    db.session.add(new_booking)
    db.session.commit()

    flash('Booking created successfully!', 'success')
    return redirect(url_for('my_bookings'))


@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.get_json()
    booking_id = data.get('booking_id')
    method = data.get('method')
    amount = data.get('amount')

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    # Assuming booking has a user_id and status field
    user = User.query.get(booking.user_id)

    payment = Payment(
        user_id=user.id,
        booking_id=booking.id,
        method=method,
        amount=float(amount),
        status='Completed'
    )

    booking.status = 'Completed'
    db.session.add(payment)
    db.session.commit()

    # Send confirmation email
    try:
        msg = Message('Payment Confirmation',
                      recipients=[user.email])
        msg.body = f"Hi {user.username},\n\nYour payment of ${amount} for booking #{booking_id} was successful.\n\nThank you!"
        mail.send(msg)
    except Exception as e:
        print(f"Email sending failed: {e}")

    return jsonify({'success': True})



@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking:
        booking.status = 'Cancelled'
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Booking not found'}), 404


@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    data = request.get_json()
    tour_id = data.get('tour_id')
    rating = data.get('rating')
    comment = data.get('comment', '')

    if not tour_id or not rating:
        return jsonify({'error': 'Missing required fields'}), 400

    # Create and save review
    new_review = Review(
        tour_id=tour_id,
        user_id=current_user.id,
        rating=int(rating),
        comment=comment,
        created_at=datetime.utcnow()
    )
    db.session.add(new_review)
    db.session.commit()

    return jsonify({'message': 'Review submitted successfully'}), 200



@app.route('/admin/bookings/<int:booking_id>/delete', methods=['POST'])
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return '', 204





@app.route('/admin/bookings')
@login_required  # If needed
def admin_bookings():
    bookings = Booking.query.all()
    return render_template('dashboard.html', bookings=bookings)





@app.route('/admin/bookings/<int:booking_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if request.method == 'POST':
        # Update fields here
        booking.status = request.form['status']
        db.session.commit()
        flash('Booking updated successfully')
        return redirect(url_for('admin_bookings'))

    return render_template('edit_booking.html', booking=booking)




# @app.route('/delete_user/<int:user_id>', methods=['POST'])
# @login_required  # optional: protect with login
# def delete_user(user_id):
#     user = User.query.get_or_404(user_id)
#     db.session.delete(user)
#     db.session.commit()
#     flash('User deleted successfully.', 'success')
#     return render_template('dashboard.html')
