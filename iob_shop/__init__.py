from multiprocessing.spawn import prepare
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
from sqlalchemy.ext.automap import automap_base
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:tnh210302@localhost/IOB_test'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'lkajdlkfhawoiherlhslhd'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images/book')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

db = SQLAlchemy(app)
Base = automap_base()
Base.prepare(db.engine, reflect=True)
bcrypt = Bcrypt(app)

from iob_shop.admin import routes
from iob_shop.admin import models
from iob_shop.books import routes
from iob_shop.carts import carts