from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, FloatField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class BookingForm(FlaskForm):
    travel_date = DateField('Travel Date', validators=[DataRequired()])
    persons = IntegerField('Number of Persons', validators=[DataRequired()])
    special_requests = TextAreaField('Special Requests')
    submit = SubmitField('Book Now')

class TourForm(FlaskForm):
    title = StringField('Tour Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    duration = IntegerField('Duration (days)', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired(), Length(max=100)])
    image = StringField('Image URL')
    submit = SubmitField('Save Tour')