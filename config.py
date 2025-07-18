# config.py
import os

from flask import app

class Config:
    SECRET_KEY = 'secret_keyxyz'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:123@localhost/flask_app'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'bahatibk@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'bahatibk72@gmail.com')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'bahatibk72@gmail.com')
