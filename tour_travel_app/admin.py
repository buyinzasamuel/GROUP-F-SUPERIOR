# tour_travel_app/admin.py
from flask import Blueprint, render_template
from flask_login import login_required
from tour_travel_app.models import Tour, Booking, User

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
	# Example: Render an admin dashboard template
	return render_template('admin/dashboard.html')