from email.policy import default
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, IntegerField, StringField, BooleanField, TextAreaField, DecimalField, validators

class Addbook(Form):
    isbn = StringField('ISBN', [validators.DataRequired()])
    title = StringField('Title', [validators.DataRequired()])
    edition = IntegerField('Edition', default=1)
    publish_date = StringField('Publish date', [validators.DataRequired()])
    price = DecimalField('Price', [validators.DataRequired()])
    stock = IntegerField('Stock', [validators.DataRequired()])
    sales_amount = IntegerField('Sales amount', default=0)
    longdesc= TextAreaField('Long description', [validators.DataRequired()])
    shortdesc= TextAreaField('Short description', [validators.DataRequired()])
    
    image_1 = FileField('Image 1', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'], 'images only please')])
    image_2 = FileField('Image 2', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'], 'images only please')])
    image_3 = FileField('Image 3', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'], 'images only please')])
    