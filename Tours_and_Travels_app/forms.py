from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, IntegerField, FileField, SelectField, BooleanField # type: ignore
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, URL, Optional # type: ignore
from wtforms import DecimalField # type: ignore
from wtforms.fields import EmailField# type: ignore
from flask_wtf.file import FileAllowed# type: ignore


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone_number = StringField('Phone Number')
    image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
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
    
    
class TourForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    image = FileField('Image', validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Create Tour') 
    
    
class DestinationForm(FlaskForm):
    name = StringField('Destination Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    country = StringField('Country', validators=[DataRequired(), Length(min=2, max=100)])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField('Save Destination')
    
class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    password = PasswordField('New Password', validators=[Optional()])
    is_admin = BooleanField('Is Admin')
    image = FileField('Profile Image')
    
    
class DummyForm(FlaskForm):
    pass