from flask import Flask #type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from flask_migrate import Migrate  # type: ignore
from flask_login import LoginManager  # type: ignore
from config import Config  # type: ignore
import psycopg2  # type: ignore

#Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config) #Load configuration from Config class

#Initialize SQLAlchemy for database operations
db = SQLAlchemy(app)

conn = psycopg2.connect(
    database=app.config['DATABASE']['database'],
    user=app.config['DATABASE']['user'],
    password=app.config['DATABASE']['password'],
    host=app.config['DATABASE']['host'],
    port=app.config['DATABASE']['port']
)

# Example of accessing the DATABASE configuration
database = app.config['DATABASE']['database']
#Initialize Flask-Migrate for database migrations
migrate = Migrate(app, db)

#Initialize Flask-Login for user session management
login_manager = LoginManager(app)
login_manager.login_view = 'login'  #Set the login view endpoint and redirect to login page if not authenticated

#Import routes after initializing app, db, migrate, and login_manager to avoid circular imports
from routes import *  # type: ignore
from models import Booking, User, TourPackage, Review, Inquiry
