from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, make_response
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import func, extract
from io import BytesIO, StringIO
import csv
from xhtml2pdf import pisa
from werkzeug.security import generate_password_hash
from .. import db
from ..models import Destination, User, Tour, Booking, Inquiry

admin = Blueprint('custom_admin', __name__, url_prefix='/admin')


def admin_required(func):
    """Decorator to check if user is admin."""
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for('custom_admin.login'))
        return func(*args, **kwargs)
    return wrapper


# ---------- LOGIN / LOGOUT ----------

@admin.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            flash('Logged in successfully as admin.', 'success')
            return redirect(url_for('custom_admin.dashboard'))
        else:
            flash('Invalid credentials or not an admin.', 'danger')
            return redirect(url_for('custom_admin.login'))

    return render_template('admin/login.html')


@admin.route('/logout', endpoint='logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('custom_admin.login'))


# ---------- DASHBOARD ----------

@admin.route('/dashboard', endpoint='dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    tours = Tour.query.order_by(Tour.id.desc()).all()  # latest first
    bookings = Booking.query.all()
    inquiries = Inquiry.query.all()

    # Sum actual booking revenue
    total_revenue = db.session.query(func.sum(Tour.price))\
    .join(Booking, Booking.tour_id == Tour.id).scalar() or 0

    most_booked = (
        db.session.query(
            Tour.title,
            func.count(Booking.tour_id).label('count')
        )
        .join(Booking, Booking.tour_id == Tour.id)
        .group_by(Tour.title)
        .order_by(func.count(Booking.tour_id).desc())
        .first()
    )

    return render_template(
        'admin/dashboard.html',
        users=users,
        tours=tours,
        bookings=bookings,
        inquiries=inquiries,
        total_revenue=total_revenue,
        most_booked=most_booked
    )


# ---------- USERS CRUD ----------

@admin.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    password = request.form['password']  # Get password first
    user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        email=request.form['email'],
        password_hash=generate_password_hash(password),
        is_admin=False,
    )
    db.session.add(user)
    db.session.commit()
    flash('User added successfully.', 'success')
    return redirect(url_for('custom_admin.dashboard'))


@admin.route('/users/delete/<int:id>', endpoint='delete_user')
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('custom_admin.dashboard'))


@admin.route('/users/edit/<int:id>', methods=['POST'], endpoint='edit_user')
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.email = request.form['email']
    db.session.commit()
    flash('User updated successfully.', 'success')
    return redirect(url_for('custom_admin.dashboard'))


# ---------- TOURS CRUD ----------

@admin.route('/tours/add', methods=['POST'])
@login_required
@admin_required
def add_tour():
    # Get destination ID from form and validate it
    destination_id = request.form.get('destination_id')
    destination_id = int(destination_id) if destination_id else None

    # Create new tour instance
    tour = Tour(
        title=request.form['title'],
        description=request.form['description'],
        price=float(request.form['price']),
        destination_id=destination_id,  # use the already validated variable
        image_url=request.form.get('image_url', '')
    )

    # Commit to database
    db.session.add(tour)
    db.session.commit()
    flash('Tour added successfully.', 'success')
    return redirect(url_for('custom_admin.dashboard'))


@admin.route('/tours/new', methods=['GET'])
@login_required
@admin_required
def new_tour_form():
    destinations = Destination.query.all()
    return render_template('admin/new_tour.html', destinations=destinations)

@admin.route('/tours/delete/<int:id>', endpoint='delete_tour')
@login_required
@admin_required
def delete_tour(id):
    tour = Tour.query.get_or_404(id)
    db.session.delete(tour)
    db.session.commit()
    flash('Tour deleted successfully.', 'success')
    return redirect(url_for('custom_admin.dashboard'))


@admin.route('/tours/edit/<int:id>', methods=['POST'], endpoint='edit_tour')
@login_required
@admin_required
def edit_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    if request.method == 'POST':
        tour.title = request.form['title']
        tour.description = request.form['description']
        tour.price = float(request.form['price'])
        tour.destination_id = int(request.form['destination_id'])
        tour.image_url = request.form.get('image_url', tour.image_url)
        db.session.commit()
        flash('Tour updated successfully.', 'success')
        return redirect(url_for('custom_admin.dashboard'))
    destinations = Destination.query.all()
    return render_template('admin/edit_tour.html', tour=tour, destinations=destinations)

# ---------- INQUIRIES (if needed) ----------

# add your inquiry CRUD here...


# ---------- REPORTS ----------

@admin.route('/reports', endpoint='view_reports')
@login_required
@admin_required
def view_reports():
    # Total bookings
    total_bookings = Booking.query.count()

    # Total revenue
    total_revenue = db.session.query(func.sum(Tour.price))\
    .join(Booking, Booking.tour_id == Tour.id).scalar() or 0

    # Most popular destinations
    popular_destinations = db.session.query(
    Destination,
    func.count(Booking.id).label('booking_count')
    ).join(Tour, Tour.destination_id == Destination.id)\
    .join(Booking, Booking.tour_id == Tour.id)\
    .group_by(Destination.id)\
    .order_by(func.count(Booking.id).desc())\
    .limit(5).all()
    popular_labels = [dest for dest, _ in popular_destinations]
    popular_counts = [cnt for _, cnt in popular_destinations]

    # Monthly revenue
    monthly_data = (
    db.session.query(
        extract('month', Booking.date_booked).label('month'),
        func.sum(Tour.price).label('revenue')
    )
    .join(Tour, Booking.tour_id == Tour.id)
    .group_by('month')
    .order_by('month')
    .all()
)
    month_map = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    monthly_labels = [month_map[int(m)-1] for m, _ in monthly_data]
    monthly_revenue = [float(r) for _, r in monthly_data]

    return render_template(
        'admin/reports.html',
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        popular_labels=popular_labels,
        popular_counts=popular_counts,
        monthly_labels=monthly_labels,
        monthly_revenue=monthly_revenue
    )


@admin.route('/reports/export/pdf', endpoint='export_pdf')
@login_required
@admin_required
def export_pdf():
    # Recompute reports data here:
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(func.sum(Tour.price))\
    .join(Booking, Booking.tour_id == Tour.id).scalar() or 0
    popular_destinations = db.session.query(
    Destination,
    func.count(Booking.id).label('booking_count')
    ).join(Tour, Tour.destination_id == Destination.id)\
    .join(Booking, Booking.tour_id == Tour.id)\
    .group_by(Destination.id)\
    .order_by(func.count(Booking.id).desc())\
    .limit(5).all()

    rendered = render_template(
        'admin/reports_pdf.html',
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        popular_destinations=popular_destinations
    )
    pdf = BytesIO()
    pisa.CreatePDF(rendered, dest=pdf)
    pdf.seek(0)
    return send_file(pdf, mimetype='application/pdf', download_name='report.pdf')


@admin.route('/reports/export/csv', endpoint='export_csv')
@login_required
@admin_required
def export_csv():
    popular_destinations = db.session.query(
    Destination,
    func.count(Booking.id).label('booking_count')
    ).join(Tour, Tour.destination_id == Destination.id)\
    .join(Booking, Booking.tour_id == Tour.id)\
    .group_by(Destination.id)\
    .order_by(func.count(Booking.id).desc())\
    .limit(5).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Destination', 'Bookings'])
    for dest, count in popular_destinations:
        writer.writerow([dest, count])

    resp = make_response(output.getvalue())
    resp.headers['Content-Disposition'] = 'attachment; filename=popular_destinations.csv'
    resp.headers['Content-Type'] = 'text/csv'
    return resp
