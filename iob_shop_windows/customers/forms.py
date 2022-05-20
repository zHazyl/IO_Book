from wtforms import Form, StringField, TextAreaField, PasswordField, SubmitField, validators, ValidationError
from flask_wtf.file import FileRequired, FileAllowed, FileField
from flask_wtf import FlaskForm
from .models import Customer
from iob_shop import db

class CustomerRegisterForm(FlaskForm):
    fname = StringField('First name: ')
    lname = StringField('Last name: ')
    username = StringField('Username: ', [validators.DataRequired()])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired(), validators.EqualTo('confirm', message=' Both password must match!! ')])
    confirm = PasswordField('Repeat password: ', [validators.DataRequired()])
    city = StringField('City: ', [validators.DataRequired()])
    state = StringField('State: ', [validators.DataRequired()])
    street = StringField('Street: ', [validators.DataRequired()])
    flat = StringField('Flat: ', [validators.DataRequired()])
    building = StringField('Building: ', [validators.DataRequired()])
    phonenum = StringField('Phone: ', [validators.DataRequired()])
    zipcode = StringField('Zip code', [validators.DataRequired()])
    profile = FileField('Profile', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Image only please')])
    submit = SubmitField('Register')
        
    def validate_username(self, username):
        if db.session.query(Customer).filter_by(username=username.data).first():
            raise ValidationError('This username is already in use!!') 
               
    def validate_email(self, email):
        if db.session.query(Customer).filter_by(email=email.data).first():
            raise ValidationError('This email is already in use!!')
        
class CustomerLoginForm(FlaskForm):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired()])