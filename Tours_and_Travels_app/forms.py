from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField # type: ignore
from wtforms.validators import DataRequired, Email, EqualTo # type: ignore

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