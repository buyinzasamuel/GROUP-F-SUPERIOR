from flask import Flask#type: ignore
from flask_sqlalchemy import SQLAlchemy#type: ignore
from flask_migrate import Migrate#type: ignore
from flask_login import LoginManager#type: ignore
from config import Config
from flask_mail import Mail#type: ignore
import psycopg2 #type: ignore
import traceback #type: ignore
import os

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # or your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'andimashimwerhoda@gmail.com'
app.config['MAIL_PASSWORD'] = 'pdjm kbxb yrrw vzue' # Or use environment variables!
app.config['MAIL_DEFAULT_SENDER'] = 'andimashimwerhoda@gmail.com'


db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)




login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import Booking, User, TourPackage, Review, Inquiry

# FIX: Register the user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()
    return f"An error occurred: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)

from routes import *


