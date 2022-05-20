from datetime import datetime
from iob_shop import db
from iob_shop import Base

# class Book(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), nullable=False)
#     price = db.Column(db.Numeric(10,2), nullable=False)
#     discount = db.Column(db.Integer, default=0)
#     stock = db.Column(db.Integer, nullable=False)
#     desc = db.Column(db.Text, nullable=False)
#     pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
#     publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable=False)
#     publisher = db.relationship('Publisher', backref=db.backref('publishers', lazy=True))
    
#     category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
#     category = db.relationship('Category', backref=db.backref('categories', lazy=True))
    
#     author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
#     author = db.relationship('Author', backref=db.backref('authors', lazy=True))
    
#     image_1 = db.Column(db.String(150), nullable=False, default='image.jpg')
#     image_2 = db.Column(db.String(150), nullable=False, default='image.jpg')
#     image_3 = db.Column(db.String(150), nullable=False, default='image.jpg')

# class Publisher(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(30), nullable=False, unique=True)
    
# class Category(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(30), nullable=False, unique=True)
    
# class Author(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False, unique=True)
    
# db.create_all()

Book = Base.classes.BOOK
Publisher = Base.classes.PUBLISHER
Category = Base.classes.CATEGORY
Author = Base.classes.AUTHOR
Discount = Base.classes.DISCOUNT
Book_belongs_to_category = Base.classes.BOOK_BELONGS_TO_CATEGORY
Author_write_book = Base.classes.AUTHOR_WRITE_BOOK
Book_discount = Base.classes.BOOK_DISCOUNT