from wtforms import Form, BooleanField, StringField, PasswordField, validators

class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    adminname = StringField('Adminname', [validators.Length(min=4, max=25)])
    email = StringField('Email address', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('New password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat password')
    
class LoginForm(Form):
    email = StringField('Email address', [validators.Length(min=5, max=35), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    