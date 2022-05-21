from unicodedata import category
from urllib import response
from click import File
from flask import redirect, request, url_for, render_template, flash, session, current_app, make_response
from sqlalchemy import func, null
from flask_login import login_required, current_user, logout_user, login_user
from iob_shop import db, app, photos, search, bcrypt, login_manager
from iob_shop.admin.routes import publishers, register
import secrets, os
from datetime import datetime

from iob_shop.books.models import Book
from .forms import CustomerLoginForm, CustomerRegisterForm
from .models import Customer, CustomerOrder, SalesAmount
from iob_shop.books import Book
import pdfkit
import stripe

publishable_key = 'pk_test_51L0av7HsWqb2EgUCu5BzjdzJdKs3IiXeKAf0dApqs8C4ZXKzEmTf5bfP5JXCPzV4EwNmU6dcNrAUqUiRiOkXn7q3005SniBv9J'

stripe.api_key = 'sk_test_51L0av7HsWqb2EgUCT2LKZMcqIADQyiQKEINCZ49NcFv1Ixqqozh4jo8ijVruZhVAvC8rCFGJsmthDeFUBNyuF8l100aeKyTtte'

@app.route('/payment', methods=['POST'])
@login_required
def payment():
    invoice = request.form.get('invoice')
    strgrand = request.form.get('strgrand')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        description='IOB',
        amount=strgrand,
        currency='usd',
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    flash('Thanks for shipping!!', 'success')
    return redirect(url_for('profile'))

@app.route('/thanks')
def thanks():
    return render_template('customer/thank.html')

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        passwordhash = bcrypt.generate_password_hash(form.password.data)
        customer = Customer(Fname=form.fname.data, Lname=form.lname.data, username=form.username.data, email=form.email.data, 
                passwordhash=passwordhash, city=form.city.data, state=form.state.data, street=form.street.data, flat_no=form.flat.data,
                building_no=form.building.data, phone_num=form.phonenum.data, zipcode=form.zipcode.data, profile='user.png',
                id=None)
        db.session.add(customer)
        flash(f'Welcome {form.lname.data}, thanks for registering', 'success')
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('customer/register.html', form=form, title='Register')

@app.route('/customer/login', methods=['GET','POST'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = db.session.query(Customer).filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.passwordhash, form.password.data):
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect email or password', 'danger')
        return redirect(url_for('customerLogin'))
    return render_template('customer/login.html', form=form, title='Login')

@app.route('/customer/logout')
def customer_logout():
    logout_user()
    flash('You\'re loged out', 'success')
    return redirect(url_for('home'))

def updateshoppingcart():
    for _key, book in session['Shoppingcart'].items():
        session.modified = True
        del book['image']
    return updateshoppingcart
        

@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshoppingcart()
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
            grandTotal=0
            subTotal=0
            db.session.add(order)
            for key, book in order.orders.items():
                bookk = db.session.query(Book).filter_by(ISBN=key).first()
                bookk.stock -= int(book['quantity'])
                bookk.sales_amount += int(book['quantity'])
                discount = float(book['discountmax']) * float(book['price'])
                subTotal += (float(book['price']) - discount)* int(book['quantity'])
                grandTotal = subTotal
            # Tính tổng tiền theo quý
            date = order.date_created
            curr_year=db.session.query(SalesAmount).filter_by(year=int(date.year)).first()
            if curr_year == None:
                quarterly=SalesAmount(year=int(date.year),quarter1=0,quarter2=0,quarter3=0,quarter4=0)
                db.session.add(quarterly)
            else:
                if int(date.month) in [1,2,3]:
                    curr_year.quarter1+=grandTotal
                elif date.month in [4,5,6]:
                    curr_year.quarter2+=grandTotal
                elif date.month in [7,8,9]:
                    curr_year.quarter3+=grandTotal
                else:
                    curr_year.quarter4+=grandTotal

            db.session.commit()    
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully', 'success')
            return redirect(url_for('orders', invoice=invoice))
        except Exception as e:
            print(e)
            flash('Some thing went wrong while get order', 'danger')
            return redirect(url_for('get_cart'))
        
@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Customer.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        for _key, book in orders.orders.items():
            discount = float(book['discountmax']) * float(book['price'])
            subTotal += (float(book['price']) - discount)* int(book['quantity'])
            grandTotal = subTotal
            strgrand = ("%.2f" % float(grandTotal)).replace('.','')
    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/order.html', invoice=invoice, strgrand=strgrand, subTotal=subTotal, grandTotal=grandTotal, customer=customer, orders=orders, discount=discount, title='Order')

@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method == 'POST':
            customer = Customer.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            for _key, book in orders.orders.items():
                discount = round(float(book['discountmax']) * float(book['price']))
                subTotal += (float(book['price']) - discount)* int(book['quantity'])
                grandTotal = subTotal
                strgrand = str(grandTotal).replace('.','')
    
            rendered = render_template('customer/pdf.html', invoice=invoice, strgrand=strgrand, subTotal=subTotal, grandTotal=grandTotal, customer=customer, orders=orders, discount=discount, title='Order')
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['content-Type'] = 'application/pdf'
            response.headers['content-Disposition'] = 'inline: filename=' + invoice + '.pdf'
            return response
    return request(url_for('orders', invoice))

@app.route('/profile')
@login_required
def profile():
    if current_user.is_authenticated:
        customer_id = current_user.id
        customer = Customer.query.filter_by(id=customer_id).first()
        orderss = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc())
    
    else:
        return redirect(url_for('customerLogin'))
    
    return render_template('customer/profile.html', customer=customer, orderss=orderss, title='Order')