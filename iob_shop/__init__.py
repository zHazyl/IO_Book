from multiprocessing.spawn import prepare
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
from sqlalchemy.ext.automap import automap_base
import os
from flask_msearch import Search
from flask_login import LoginManager, UserMixin
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:tnh210302@localhost/IOB'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'lkajdlkfhawoiherlhslhd'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images/book')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

db = SQLAlchemy(app)
Base = automap_base()

class Customer(Base, UserMixin, db.Model):
    __tablename__ = 'CUSTOMER'
    
    def __repr__(self):
        return '<Register %r>' % self.name
    
Base.prepare(db.engine, reflect=True)
bcrypt = Bcrypt(app)
search = Search()
search.init_app(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customerLogin'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u'Please login first'

from iob_shop.admin import routes
from iob_shop.admin import models
from iob_shop.books import routes
from iob_shop.carts import carts
from iob_shop.customers import routes