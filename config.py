import os

import stripe

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_secret_key'
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/flask_users'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'bahatibk@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'bahatibk72@gmail.com')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'bahatibk72@gmail.com')
    
    
    
    #Folder for file uploads
    #This is where uploaded files will be stored
    #Make sure this folder exists and is writable by the application
    UPLOAD_FOLDER = 'static/uploads'
    
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY') or 'your_stripe_public_key'
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or 'your_stripe_secret_key'
    stripe.api_key = STRIPE_SECRET_KEY