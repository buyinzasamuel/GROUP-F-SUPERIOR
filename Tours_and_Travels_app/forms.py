from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, IntegerField # type: ignore
from wtforms.validators import DataRequired, Email, EqualTo # type: ignore
from wtforms import DecimalField # type: ignore

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TourPackageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    image_url = StringField('Image URL')
    submit = SubmitField('Submit')

class BookingForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Book Now')
    
class PaymentForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired()])
    currency = StringField('Currency', validators=[DataRequired()])
    submit = SubmitField('Pay Now')

class ReviewForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired()])
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Review')
    
class InquiryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Inquiry')    