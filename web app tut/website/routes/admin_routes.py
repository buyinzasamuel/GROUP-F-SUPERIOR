from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from ..models import User, Tour, Booking, Inquiry
from .. import db

admin = Blueprint('custom_admin', __name__)

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

@admin.route('/dashboard', endpoint='dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    tours = Tour.query.all()
    bookings = Booking.query.all()
    inquiries = Inquiry.query.all()

    total_revenue = sum(t.price for t in tours if t.price)
    most_booked = (
        db.session.query(
            Tour.title,
            db.func.count(Booking.tour_id).label('count')
        )
        .join(Booking)
        .group_by(Tour.title)
        .order_by(db.desc('count'))
        .first()
    )

    return render_template('admin/dashboard.html',
                           users=users,
                           bookings=bookings,
                           tours=tours,
                           inquiries=inquiries,
                           total_revenue=total_revenue,
                           most_booked=most_booked)

# ---------- USERS CRUD ----------

@admin.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form['username']
    email = request.form['email']
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    flash('User added successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/users/delete/<int:id>')
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/users/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    user.username = request.form['username']
    user.email = request.form['email']
    db.session.commit()
    flash('User updated successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

# ---------- TOURS CRUD ----------

@admin.route('/tours/add', methods=['POST'])
@login_required
@admin_required
def add_tour():
    title = request.form['title']
    description = request.form['description']
    price = float(request.form['price'])
    tour = Tour(title=title, description=description, price=price)
    db.session.add(tour)
    db.session.commit()
    flash('Tour added successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/tours/delete/<int:id>')
@login_required
@admin_required
def delete_tour(id):
    tour = Tour.query.get_or_404(id)
    db.session.delete(tour)
    db.session.commit()
    flash('Tour deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/tours/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_tour(id):
    tour = Tour.query.get_or_404(id)
    tour.title = request.form['title']
    tour.description = request.form['description']
    tour.price = float(request.form['price'])
    db.session.commit()
    flash('Tour updated successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

# ---------- LOGIN / LOGOUT ----------

@admin.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if user.is_admin:
                login_user(user)
                flash('Logged in successfully as admin.', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Access denied: not an admin.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')

        return redirect(url_for('custom_admin.login'))

    return render_template('admin/login.html')


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('custom_admin.login'))
