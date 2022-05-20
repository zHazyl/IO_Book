from datetime import datetime
from iob_shop import Base, login_manager, db, Customer
from flask_login import UserMixin
import json

@login_manager.user_loader
def user_loader(user_id):
    return db.session.query(Customer).filter_by(id=int(user_id)).first_or_404()

SalesAmount=Base.classes.quarterlyrevenue
Debit = Base.classes.debit

class JsonEncodedDict(db.TypeDecorator):
    impl = db.Text
    
    def process_bind_param(self, value, dialect): #set
        if value is None:
            return '{}'
        return json.dumps(value)
    
    def process_result_value(self, value, dialect): #get
        if value is None:
            return {}
        return json.loads(value)

class CustomerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    customer_id = db.Column(db.Integer, unique=False, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    orders = db.Column(JsonEncodedDict)
    
    def __repr__(self):
        return '<CustomerOrder %r>' % self.invoice


db.create_all()