from flask import Blueprint, render_template, abort
from tour_travel_app.models import Tour

bp = Blueprint('tours', __name__)

@bp.route('/')
def tour_list():
    """
    Display a list of all available tours
    """
    try:
        tours = Tour.query.all()
        return render_template('tours/list.html', tours=tours)
    except Exception as e:
        # Log the error in production (you might want to add logging here)
        abort(500, description="An error occurred while retrieving tours")

@bp.route('/<int:tour_id>')
def tour_detail(tour_id):
    """
    Display details for a specific tour
    """
    try:
        tour = Tour.query.get_or_404(tour_id)
        return render_template('tours/detail.html', tour=tour)
    except Exception as e:
        # Log the error in production
        abort(500, description="An error occurred while retrieving tour details")