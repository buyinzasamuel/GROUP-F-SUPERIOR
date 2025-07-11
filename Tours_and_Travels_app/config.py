import os

class Config:
    #Secret key for session management and CSRF protection
    #It should be kept secret in production
    #You can set it as an environment variable for security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_secret_key'
    
    #Database URI for SQLAlchemy
    #You can set it as an environment variable for security
    #If DATABASE_URL is not set, it defaults to a SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    #Disable track modifications to save memory
    #This is not needed in most cases and can be set to False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #Folder for file uploads
    #This is where uploaded files will be stored
    #Make sure this folder exists and is writable by the application
    UPLOAD_FOLDER = 'static/uploads'
    
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY') or 'your_stripe_public_key'
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or 'your_stripe_secret_key'