from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate
from config import Config
from models import User, Tour, Booking
from forms import LoginForm, RegistrationForm, BookingForm, TourForm
from tour_travel_app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

# Sample data - in a real app, this would come from the database
tours = [
    {
        'id': 1,
        'title': 'Paris Getaway',
        'description': 'Explore the city of love with our 5-day package',
        'duration': 5,
        'price': 1200,
        'destination': 'Paris, France',
        'image': 'paris.jpg'
    },
    {
        'id': 2,
        'title': 'Tropical Bali',
        'description': 'Relax on beautiful beaches and experience Balinese culture',
        'duration': 7,
        'price': 1500,
        'destination': 'Bali, Indonesia',
        'image': 'bali.jpg'
    }
]

@app.route('/')
def index():
    featured_tours = Tour.query.order_by(Tour.created_at.desc()).limit(3).all()
    return render_template('index.html', tours=featured_tours)

@app.route('/tours')
def tour_list():
    tours = Tour.query.all()
    return render_template('tours.html', tours=tours)

@app.route('/tours/<int:tour_id>')
def tour_detail(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    return render_template('tour_detail.html', tour=tour)

@app.route('/book/<int:tour_id>', methods=['GET', 'POST'])
@login_required
def book_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    form = BookingForm()
    if form.validate_on_submit():
        booking = Booking(
            user_id=current_user.id,
            tour_id=tour.id,
            travel_date=form.travel_date.data,
            persons=form.persons.data,
            special_requests=form.special_requests.data
        )
        db.session.add(booking)
        db.session.commit()
        flash('Your booking has been submitted!', 'success')
        return redirect(url_for('index'))
    return render_template('booking.html', form=form, tour=tour)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    tours = Tour.query.count()
    bookings = Booking.query.count()
    users = User.query.count()
    return render_template('admin/dashboard.html', tours=tours, bookings=bookings, users=users)

@app.route('/admin/tours')
@login_required
def admin_tours():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    tours = Tour.query.all()
    return render_template('admin/tours.html', tours=tours)

@app.route('/admin/tours/add', methods=['GET', 'POST'])
@login_required
def add_tour():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    form = TourForm()
    if form.validate_on_submit():
        tour = Tour(
            title=form.title.data,
            description=form.description.data,
            duration=form.duration.data,
            price=form.price.data,
            destination=form.destination.data,
            image=form.image.data
        )
        db.session.add(tour)
        db.session.commit()
        flash('Tour added successfully!', 'success')
        return redirect(url_for('admin_tours'))
    return render_template('admin/add_tour.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)

